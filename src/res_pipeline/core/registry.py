"""Study registry: the canonical S001-S028 identity layer for the corpus.

Builds a deterministic, deduplicated registry from ``data/studies_metadata.jsonl``,
assigning stable StudyIDs ordered by (year, title) so that re-runs always produce
the same mapping. Every downstream artifact references studies exclusively by
StudyID — the "single source of truth" identity required for auditability.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from res_pipeline.core.config import DATA_DIR

METADATA_FILE = DATA_DIR / "studies_metadata.jsonl"
FULLTEXT_DIR = DATA_DIR / "20-paper-of-Richmond"


class StudyRecord(BaseModel):
    """One primary study in the corpus."""

    study_id: str = Field(pattern=r"^S\d{3}$")
    record_id: str
    doi: str | None
    title: str
    authors: list[str]
    year: int | None
    journal: str | None
    abstract: str | None
    source_kind: str = Field(pattern=r"^(fulltext_pdf|abstract_only)$")
    pdf_path: str | None
    metadata_confidence: float


def _normalize_doi(doi: str | None) -> str | None:
    return doi.strip().lower() if doi else None


def build_registry(metadata_file: Path = METADATA_FILE) -> list[StudyRecord]:
    """Parse metadata, deduplicate by DOI, and assign stable StudyIDs."""
    raw: list[dict] = []
    with metadata_file.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                raw.append(json.loads(line))

    seen_dois: set[str] = set()
    deduped: list[dict] = []
    for rec in raw:
        doi = _normalize_doi(rec.get("doi"))
        if doi and doi in seen_dois:
            continue
        if doi:
            seen_dois.add(doi)
        deduped.append(rec)

    # Deterministic ordering: year (unknown last), then title.
    deduped.sort(key=lambda r: (r.get("year") or 9999, (r.get("title") or "").lower()))

    studies: list[StudyRecord] = []
    for index, rec in enumerate(deduped, start=1):
        source_id = rec.get("source_id") or ""
        is_pdf = rec.get("source") == "pdf" and source_id.lower().endswith(".pdf")
        pdf_path = str(FULLTEXT_DIR / source_id) if is_pdf else None
        if pdf_path and not Path(pdf_path).exists():
            pdf_path = None
        studies.append(
            StudyRecord(
                study_id=f"S{index:03d}",
                record_id=rec["record_id"],
                doi=_normalize_doi(rec.get("doi")),
                title=(rec.get("title") or "").strip(),
                authors=rec.get("authors") or [],
                year=rec.get("year"),
                journal=rec.get("journal"),
                abstract=rec.get("abstract"),
                source_kind="fulltext_pdf" if pdf_path else "abstract_only",
                pdf_path=pdf_path,
                metadata_confidence=float(rec.get("confidence") or 0.0),
            )
        )
    return studies
