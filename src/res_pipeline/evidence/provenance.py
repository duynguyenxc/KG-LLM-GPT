"""Run-local persistence, exact quotation location, and accountable API calls."""

from __future__ import annotations

import hashlib
import json
import re
import threading
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from openai import APIStatusError, OpenAI
from pydantic import BaseModel


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def request_payload(
    model: str, system: str, user: str, schema: type[BaseModel], config: dict
) -> dict:
    """One request contract shared by execution and offline cache inspection."""
    return {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "strict": True,
                "schema": schema.model_json_schema(),
            },
        },
        "reasoning_effort": config["reasoning_effort"],
        "max_completion_tokens": config["max_completion_tokens"],
        "store": False,
    }


def locate_quote(text: str, quote: str) -> dict:
    """Locate a complete quote with traceable PDF-typography normalization, never fuzzy similarity."""
    if not quote.strip():
        return {"located": False, "start": None, "end": None, "method": "absent"}
    start = text.find(quote)
    if start >= 0:
        return {"located": True, "start": start, "end": start + len(quote), "method": "exact"}
    parts = re.split(r"\s+", quote.strip())
    match = re.search(r"\s+".join(re.escape(p) for p in parts), text)
    if match:
        return {
            "located": True,
            "start": match.start(),
            "end": match.end(),
            "method": "whitespace_normalized",
        }

    def pdf_characters(value: str):
        # PDF ligatures and line-end hyphenation are typography, not fuzzy semantic matches.
        line_hyphens = {
            broken.start(): broken.end()
            for broken in re.finditer(r"(?<=[^\W\d_])-\s*\n\s*(?=[^\W\d_])", value)
        }
        characters, offsets = [], []
        skip_until = -1
        for index, character in enumerate(value):
            if index < skip_until:
                continue
            if index in line_hyphens:
                characters.append("\ue000")
                offsets.append(index)
                skip_until = line_hyphens[index]
                continue
            if character.isspace():
                # Preserve word boundaries: "not able" must never match "notable".
                following = index + 1
                while following < len(value) and value[following].isspace():
                    following += 1
                # Spacing around punctuation and a retained line-end hyphen is typographic.
                if (
                    characters
                    and characters[-1].isalnum()
                    and following < len(value)
                    and value[following].isalnum()
                ):
                    characters.append(" ")
                    offsets.append(index)
                continue
            for normalized in unicodedata.normalize("NFKC", character):
                characters.append(normalized)
                offsets.append(index)
        return "".join(characters), offsets

    normalized_text, offsets = pdf_characters(text)
    normalized_quote, _ = pdf_characters(quote.strip())
    pattern = "\ue000?".join(
        "[-\ue000]" if char in "-\ue000" else re.escape(char) for char in normalized_quote
    )
    match = re.search(pattern, normalized_text) if pattern else None
    if match:
        return {
            "located": True,
            "start": offsets[match.start()],
            "end": offsets[match.end() - 1] + 1,
            "method": "pdf_typography_normalized_full_quote",
        }
    return {"located": False, "start": None, "end": None, "method": "not_found"}


class RunClient:
    """No automatic retries: uncertain charged calls reserve their maximum estimated cost."""

    def __init__(self, directory: Path, config: dict, api_key: str):
        self.directory = directory
        self.config = config
        self.client = OpenAI(api_key=api_key, max_retries=0, timeout=240)
        self._budget_lock = threading.RLock()
        self._provider_halted = threading.Event()

    def ledger(self) -> list[dict]:
        path = self.directory / "usage.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def append_usage(self, record: dict) -> None:
        with (
            self._budget_lock,
            (self.directory / "usage.jsonl").open("a", encoding="utf-8") as stream,
        ):
            stream.write(json.dumps(record) + "\n")

    def call(self, name: str, model: str, system: str, user: str, schema: type[BaseModel]):
        request = request_payload(model, system, user, schema, self.config)
        request_hash = digest(json.dumps(request, sort_keys=True).encode())
        location = self.directory / "calls" / name
        cached = location / "parsed.json"
        if cached.exists():
            if read_json(location / "identity.json")["request_sha256"] != request_hash:
                raise ValueError(f"Changed request for completed call {name}; use a new run")
            return schema.model_validate(read_json(cached))
        if (location / "request.json").exists():
            raise RuntimeError(
                f"Unfinished call {name}; inspect its recorded response before retrying"
            )
        if self._provider_halted.is_set():
            raise RuntimeError(
                "Provider credit failure halted new calls; completed caches remain available"
            )
        price = self.config["prices_per_million"][model]
        # UTF-8 bytes provide a deliberately conservative bound for byte-level tokenization.
        upper_input = len(json.dumps(request, ensure_ascii=False).encode()) + 16000
        reserve = (
            upper_input * price["input"] + request["max_completion_tokens"] * price["output"]
        ) / 1e6
        if model.startswith("gpt-5.5") and upper_input > 272000:
            reserve = (
                upper_input * price["input"] * 2
                + request["max_completion_tokens"] * price["output"] * 1.5
            ) / 1e6
        started = time.monotonic()
        record = {
            "call": name,
            "requested_model": model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "budget_charge_usd": reserve,
            "status": "unresolved",
            "estimated_maximum_usd": reserve,
        }
        # Reservation survives an interrupted process; later completion replaces it with actual usage.
        with self._budget_lock:
            spent = sum(row["budget_charge_usd"] for row in self.ledger())
            for prior in self.config.get("prior_budget_runs", []):
                prior_directory = self.directory.parent / prior
                if prior_directory.resolve() == self.directory:
                    continue
                prior_ledger = prior_directory / "usage.jsonl"
                if prior_ledger.exists():
                    spent += sum(
                        json.loads(line)["budget_charge_usd"]
                        for line in prior_ledger.read_text().splitlines()
                    )
            if spent + reserve > self.config["budget_usd"]:
                raise RuntimeError(
                    f"Budget ceiling prevents {name}: {spent:.2f} + reserve {reserve:.2f}"
                )
            write_json(location / "request.json", request)
            write_json(location / "identity.json", {"request_sha256": request_hash})
            self.append_usage(record)
        try:
            response = self.client.chat.completions.create(**request)
        except APIStatusError as error:
            body = error.body if isinstance(error.body, dict) else {}
            detail = body.get("error", body)
            code = detail.get("code") if isinstance(detail, dict) else None
            write_json(
                location / "error.json",
                {
                    "exception": type(error).__name__,
                    "http_status": error.status_code,
                    "code": code,
                    "request_id": error.request_id,
                },
            )
            if code in {"credit_balance_exhausted", "insufficient_quota"}:
                self._provider_halted.set()
                self.append_usage(
                    {
                        **record,
                        "status": "rejected_no_generation",
                        "error_code": code,
                        "budget_charge_usd": -reserve,
                    }
                )
            raise
        write_json(location / "response.json", response.model_dump())
        usage = response.usage
        cost = (
            usage.prompt_tokens * price["input"] + usage.completion_tokens * price["output"]
        ) / 1e6
        self.append_usage(
            {
                **record,
                "status": "completed",
                "actual_model": response.model,
                "input_tokens": usage.prompt_tokens,
                "output_tokens": usage.completion_tokens,
                "estimated_cost_usd": cost,
                "budget_charge_usd": cost - reserve,
                "seconds": round(time.monotonic() - started, 2),
            }
        )
        choice = response.choices[0]
        if choice.finish_reason != "stop" or choice.message.refusal:
            raise RuntimeError(f"Incomplete or refused output for {name}; raw response preserved")
        parsed = schema.model_validate_json(choice.message.content)
        write_json(cached, parsed.model_dump())
        print(f"{name}: {response.model}; estimated cost ${cost:.3f}", flush=True)
        return parsed
