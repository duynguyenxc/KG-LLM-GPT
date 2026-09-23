"""Offline source, request, response and cached-audit checks before spending API credit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from res_pipeline.evidence.pipeline import (
    CRITIC,
    EXTRACT,
    audit_findings,
    load_sources,
    repair_quotes,
    source_packet,
)
from res_pipeline.evidence.provenance import digest, read_json, request_payload, write_json
from res_pipeline.evidence.schemas import Extraction, ExtractionReview


class CacheMiss(Exception):
    """No parsed result exists; this is pending work, not a scientific failure."""


class CachedOnlyClient:
    """Has no SDK client, credential argument or network fallback."""

    def __init__(self, directory: Path, config: dict):
        self.directory = directory
        self.config = config
        self.checked = set()

    def call(self, name, model, system, user, schema):
        location = self.directory / "calls" / name
        expected = request_payload(model, system, user, schema, self.config)
        parsed = location / "parsed.json"
        if not parsed.exists():
            if (location / "response.json").exists():
                raise ValueError(f"Raw response needs inspection before retry: {name}")
            if (location / "request.json").exists() and read_json(
                location / "request.json"
            ) != expected:
                raise ValueError(f"Unfinished request changed: {name}")
            raise CacheMiss(name)
        request = read_json(location / "request.json")
        identity = read_json(location / "identity.json")["request_sha256"]
        if request != expected or digest(json.dumps(request, sort_keys=True).encode()) != identity:
            raise ValueError(f"Cached request identity changed: {name}")
        response = read_json(location / "response.json")
        choice = response["choices"][0]
        if choice["finish_reason"] != "stop" or choice["message"].get("refusal"):
            raise ValueError(f"Cached response was incomplete/refused: {name}")
        value = schema.model_validate(read_json(parsed))
        original = schema.model_validate_json(choice["message"]["content"])
        if value != original:
            raise ValueError(f"Parsed cache differs from the recorded model response: {name}")
        self.checked.add(name)
        return value


def inspect_run(root: Path, directory: Path) -> dict:
    config = read_json(root / "config/evidence_run.json")
    if config != read_json(directory / "config.json"):
        raise ValueError("Run configuration differs from current configuration")
    # Re-read current source PDFs in a temporary directory, never overwrite a run manifest.
    with TemporaryDirectory(prefix="realist-preflight-") as temporary:
        papers, pages = load_sources(root, Path(temporary))
        if read_json(Path(temporary) / "corpus_manifest.json") != read_json(
            directory / "corpus_manifest.json"
        ):
            raise ValueError("Source identity or metadata changed")
        if pages != read_json(directory / "source_pages.json"):
            raise ValueError("Extracted source pages changed")
    client = CachedOnlyClient(directory, config)
    pending, reproducible = [], []
    for paper in papers:
        pid = paper["paper_id"]
        packet = source_packet(paper, pages)
        try:
            extraction = client.call(
                "extract_" + pid, config["extractor_model"], EXTRACT, packet, Extraction
            )
            extraction, _ = repair_quotes(client, paper, pages, packet, extraction, config)
            indexed = extraction.model_dump()
            indexed["findings"] = [
                {"finding_index": index, **finding}
                for index, finding in enumerate(indexed["findings"])
            ]
            critic_packet = (
                packet
                + "\nINDEXED EXTRACTION (assess exactly these indices)\n"
                + json.dumps(indexed, ensure_ascii=False)
            )
            critique = client.call(
                "critic_v3_" + pid, config["critic_model"], CRITIC, critic_packet, ExtractionReview
            )
            indices = [row.finding_index for row in critique.assessments]
            if sorted(indices) != list(range(len(extraction.findings))):
                critique = client.call(
                    "critic_v3_coverage_fixed_" + pid,
                    config["critic_model"],
                    CRITIC,
                    critic_packet
                    + "\nYour previous response did not assess each index exactly once. Reassess every finding. Required zero-based indices: "
                    + json.dumps(list(range(len(extraction.findings))))
                    + "\nPREVIOUS RESPONSE\n"
                    + critique.model_dump_json(),
                    ExtractionReview,
                )
            findings = audit_findings(paper, pages, extraction, critique)
            saved = directory / "papers" / (pid + ".json")
            if not saved.exists() or read_json(saved)["findings"] != findings:
                raise ValueError(f"Saved paper audit differs from reproducible cache: {pid}")
            reproducible.append(pid)
        except CacheMiss as error:
            pending.append({"paper_id": pid, "next_call": str(error)})
    unfinished = []
    for call in sorted((directory / "calls").iterdir()):
        if (call / "request.json").exists() and not (call / "parsed.json").exists():
            if (call / "response.json").exists():
                raise ValueError(f"Raw response remains unparsed: {call.name}")
            unfinished.append(call.name)
    return {
        "check": "passed",
        "scope": "source/config identity; cached requests/raw responses; reproduction of saved paper audits",
        "scientific_validity": "not assessed by these engineering checks",
        "network_calls": 0,
        "papers": len(papers),
        "cached_calls_checked": len(client.checked),
        "reproduced_paper_audits": reproducible,
        "pending": pending,
        "unfinished_without_response": unfinished,
        "configuration_sha256": digest((directory / "config.json").read_bytes()),
        "corpus_manifest_sha256": digest((directory / "corpus_manifest.json").read_bytes()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        raise FileExistsError("Choose a new preflight report path to preserve prior checks")
    from res_pipeline.core.config import PROJECT_ROOT

    result = inspect_run(PROJECT_ROOT, args.run_dir)
    write_json(args.report, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
