"""Resolve source-unit IDs without inventing PDF page numbers."""

from __future__ import annotations

import json
from pathlib import Path


def label(locator: dict) -> str:
    kind, unit = locator["kind"], locator["source_unit"]
    if kind in {"pdf_page", "partial_pdf_page"}:
        prefix = "Partial PDF" if kind == "partial_pdf_page" else "PDF"
        return f"{prefix} page {locator['original_page']} (source unit {unit})"
    return f"{'PubMed abstract' if kind == 'abstract' else 'Metadata snippet'} (source unit {unit}; no PDF page)"


def resolve(source: Path, papers: list[dict], pages: list[dict]) -> list[dict]:
    """Validate complete explicit maps, or infer only unambiguous legacy availability."""
    path = source / "source_locators.json"
    raw = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    by_id = {p["paper_id"]: p for p in papers}
    expected = {(p["paper_id"], p["page"]) for p in pages}
    if any(pid not in by_id or type(unit) is not int or unit < 1 for pid, unit in expected):
        raise ValueError("Unknown paper or invalid source-unit ID")
    if len(expected) != len(pages):
        raise ValueError("Duplicate source-unit keys")
    if raw is None:
        raw = []
        for p in pages:
            availability = by_id[p["paper_id"]]["availability"]
            kind = {
                "fulltext_available": "pdf_page",
                "partial_pdf": "partial_pdf_page",
                "metadata_snippet_only": "metadata_snippet",
            }.get(availability)
            if kind is None:
                raise ValueError("This source availability requires an explicit locator map")
            raw.append(
                {
                    "paper_id": p["paper_id"],
                    "source_unit": p["page"],
                    "kind": kind,
                    "original_page": None if kind == "metadata_snippet" else p["page"],
                }
            )
    keys = [(r["paper_id"], r["source_unit"]) for r in raw]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError("Missing, duplicate or unknown source locators")
    out = []
    aliases = {
        "original_baseline_page": "pdf_page",
        "original_partial_pdf_page": "partial_pdf_page",
        "pubmed_abstract": "abstract",
    }
    allowed = {
        "fulltext_available": {"pdf_page"},
        "partial_pdf": {"partial_pdf_page"},
        "metadata_snippet_only": {"metadata_snippet"},
        "abstract_only": {"abstract"},
        "partial_pdf_plus_abstract": {"partial_pdf_page", "abstract"},
    }
    for r in raw:
        kind = aliases.get(r["kind"], r["kind"])
        availability = by_id[r["paper_id"]]["availability"]
        if kind not in allowed.get(availability, set()):
            raise ValueError("Locator kind disagrees with source availability")
        page = r.get("original_page")
        if kind in {"abstract", "metadata_snippet"}:
            if page is not None:
                raise ValueError("Abstracts and metadata cannot have original PDF pages")
        elif type(page) is not int or page < 1:
            raise ValueError("A PDF locator requires a positive original page")
        record = {
            "paper_id": r["paper_id"],
            "source_unit": r["source_unit"],
            "kind": kind,
            "original_page": page,
        }
        # Only bibliographic IDs enter the map; no assistant judgments or URLs from arbitrary input.
        if kind == "abstract":
            pmid = r.get("pmid")
            if not isinstance(pmid, str) or not pmid.isascii() or not pmid.isdigit():
                raise ValueError("PubMed abstract requires a valid PMID")
            record.update(pmid=pmid, source_url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")
        record["label"] = label(record)
        out.append(record)
    return sorted(out, key=lambda r: (r["paper_id"], r["source_unit"]))


def attach(audited: dict, locators: list[dict]) -> None:
    by_unit = {r["source_unit"]: r for r in locators if r["paper_id"] == audited["paper_id"]}
    for record in [*audited["entities"], *audited["assertions"]]:
        for quote in record["evidence"]:
            quote["source_locator"] = by_unit.get(
                quote["page"],
                {
                    "paper_id": audited["paper_id"],
                    "source_unit": quote["page"],
                    "kind": "unresolved",
                    "original_page": None,
                    "label": f"Unknown source unit {quote['page']} (unresolved)",
                },
            )
