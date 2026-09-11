"""Calculate human-review metrics only from attributable, completed coding records."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

VERDICTS = {"equivalent", "partial", "contradictory", "not_recovered", "uncertain"}


def completed_reviews(path: Path, allowed: set[str]) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    seen, completed = set(), {}
    for row in rows:
        key = row["reference_id"]
        if key not in allowed or key in seen:
            raise ValueError(f"Unexpected or duplicate human reference ID: {key}")
        seen.add(key)
        verdict = row.get("verdict", "").strip()
        if not verdict:
            continue
        if verdict not in VERDICTS:
            raise ValueError(f"Unknown human verdict for {key}: {verdict}")
        if not all(
            row.get(field, "").strip() for field in ["reviewer", "reviewed_at", "rationale"]
        ):
            raise ValueError(f"Human review lacks reviewer, date or rationale: {key}")
        completed[key] = row
    return completed


def summarize_reviews(coder_a: dict, coder_b: dict, adjudicated: dict, total: int) -> dict:
    paired = sorted(set(coder_a) & set(coder_b))
    observed, kappa = None, None
    if paired:
        observed = sum(coder_a[key]["verdict"] == coder_b[key]["verdict"] for key in paired) / len(
            paired
        )
        a = Counter(coder_a[key]["verdict"] for key in paired)
        b = Counter(coder_b[key]["verdict"] for key in paired)
        expected = sum(a[label] * b[label] for label in VERDICTS) / len(paired) ** 2
        kappa = (observed - expected) / (1 - expected) if expected < 1 else None
    counts = dict(Counter(row["verdict"] for row in adjudicated.values()))
    return {
        "reference_rows": total,
        "coder_a_completed": len(coder_a),
        "coder_b_completed": len(coder_b),
        "paired_rows": len(paired),
        "raw_agreement": observed,
        "kappa": kappa,
        "adjudicated_rows": len(adjudicated),
        "adjudicated_counts": counts,
        "configuration_recovery": counts.get("equivalent", 0) / total
        if len(adjudicated) == total and total
        else None,
        "interpretation": "Human metrics require recorded human judgments; attribution fields do not independently authenticate reviewer identity",
    }


def read_run_reviews(directory: Path, reference_ids: set[str]) -> tuple[dict, dict, dict, dict]:
    a = completed_reviews(directory / "human_review_coder_A.csv", reference_ids)
    b = completed_reviews(directory / "human_review_coder_B.csv", reference_ids)
    adjudicated = completed_reviews(directory / "human_review_adjudication.csv", reference_ids)
    for key in adjudicated:
        if key not in a or key not in b:
            raise ValueError(f"Adjudication precedes paired independent reviews: {key}")
    return a, b, adjudicated, summarize_reviews(a, b, adjudicated, len(reference_ids))
