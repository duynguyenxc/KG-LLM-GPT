"""Cross-study synthesis: demi-regularity (motif) detection and contradiction surfacing.

Realist logic (RAMESES II; professor's "MOTIF" concept):
  * A **demi-regularity** is a recurring CMOC pattern — here operationalized as a
    (context-concept, driver-concept, outcome-concept, polarity) motif observed in
    two or more independent studies, computed over canonicalized entities.
  * A **contradiction** is the same driver (intervention/resource concept) leading
    to opposite-polarity outcomes — realist gold, because the explanation must
    live in the differing contexts (e.g., the expertise-reversal effect). These
    are surfaced to HITL-3 for interpretive adjudication, never smoothed over.

Both computations are pure SQL/Python over the typed knowledge layer — no LLM —
so they are deterministic, cheap, and fully auditable.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from res_pipeline.core.db import get_connection, log_audit_event


@dataclass
class DemiRegularity:
    context_concept: str
    driver_concept: str          # intervention or mechanism-resource concept
    outcome_concept: str
    polarity: str
    study_ids: list[str] = field(default_factory=list)
    cmoc_ids: list[str] = field(default_factory=list)


@dataclass
class Contradiction:
    driver_concept: str
    positive_studies: list[str]
    negative_studies: list[str]
    positive_contexts: list[str]
    negative_contexts: list[str]


def _cmoc_concept_rows() -> list[dict]:
    """One row per CMOC with its concept sets, at FAMILY granularity when available.

    Motifs are computed over concept families (Richmond-level granularity, cf.
    their five broad contexts); the concept/instance layers remain the
    provenance below.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.cmoc_id, c.study_id, c.polarity,
                   array_agg(DISTINCT coalesce(f.family_id, e.canonical_id))
                       FILTER (WHERE e.entity_type='Context') AS contexts,
                   array_agg(DISTINCT coalesce(f.family_id, e.canonical_id))
                       FILTER (WHERE e.entity_type IN ('Intervention','Mechanism_Resource'))
                       AS drivers,
                   array_agg(DISTINCT coalesce(f.family_id, e.canonical_id))
                       FILTER (WHERE e.entity_type='Outcome') AS outcomes
            FROM cmocs c
            JOIN entity_instances e USING (cmoc_id)
            LEFT JOIN concept_families f ON f.canonical_id = e.canonical_id
            GROUP BY c.cmoc_id, c.study_id, c.polarity
            """
        ).fetchall()
    return rows


def find_demi_regularities(min_studies: int = 2) -> list[DemiRegularity]:
    """Motifs (context, driver, outcome, polarity) recurring across >= min_studies."""
    buckets: dict[tuple, DemiRegularity] = {}
    for row in _cmoc_concept_rows():
        for ctx in row["contexts"] or []:
            for drv in row["drivers"] or []:
                for out in row["outcomes"] or []:
                    key = (ctx, drv, out, row["polarity"])
                    motif = buckets.setdefault(
                        key, DemiRegularity(ctx, drv, out, row["polarity"])
                    )
                    if row["study_id"] not in motif.study_ids:
                        motif.study_ids.append(row["study_id"])
                    motif.cmoc_ids.append(row["cmoc_id"])
    return sorted(
        (m for m in buckets.values() if len(m.study_ids) >= min_studies),
        key=lambda m: -len(m.study_ids),
    )


def find_contradictions() -> list[Contradiction]:
    """Same driver concept with opposite-polarity outcomes across studies."""
    by_driver: dict[str, dict[str, set]] = defaultdict(
        lambda: {"pos_studies": set(), "neg_studies": set(),
                 "pos_ctx": set(), "neg_ctx": set()}
    )
    for row in _cmoc_concept_rows():
        if row["polarity"] not in ("positive", "negative"):
            continue
        side = "pos" if row["polarity"] == "positive" else "neg"
        for drv in row["drivers"] or []:
            by_driver[drv][f"{side}_studies"].add(row["study_id"])
            for ctx in row["contexts"] or []:
                by_driver[drv][f"{side}_ctx"].add(ctx)

    conflicts = []
    for driver, sides in by_driver.items():
        if sides["pos_studies"] and sides["neg_studies"]:
            conflicts.append(Contradiction(
                driver_concept=driver,
                positive_studies=sorted(sides["pos_studies"]),
                negative_studies=sorted(sides["neg_studies"]),
                positive_contexts=sorted(sides["pos_ctx"]),
                negative_contexts=sorted(sides["neg_ctx"]),
            ))
    return sorted(conflicts,
                  key=lambda c: -(len(c.positive_studies) + len(c.negative_studies)))


def persist_synthesis(run_id: str) -> dict:
    """Compute and persist demi-regularities + contradictions; returns summary."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS demi_regularities (
                id BIGSERIAL PRIMARY KEY,
                context_concept TEXT NOT NULL, driver_concept TEXT NOT NULL,
                outcome_concept TEXT NOT NULL, polarity TEXT NOT NULL,
                study_ids TEXT[] NOT NULL, cmoc_ids TEXT[] NOT NULL,
                run_id TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
            CREATE TABLE IF NOT EXISTS contradictions (
                id BIGSERIAL PRIMARY KEY,
                driver_concept TEXT NOT NULL,
                positive_studies TEXT[] NOT NULL, negative_studies TEXT[] NOT NULL,
                positive_contexts TEXT[] NOT NULL, negative_contexts TEXT[] NOT NULL,
                resolution TEXT, resolved_by TEXT,
                run_id TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
            """
        )
        conn.execute("DELETE FROM demi_regularities")
        conn.execute("DELETE FROM contradictions")

        motifs = find_demi_regularities()
        for m in motifs:
            conn.execute(
                "INSERT INTO demi_regularities (context_concept, driver_concept, "
                "outcome_concept, polarity, study_ids, cmoc_ids, run_id) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (m.context_concept, m.driver_concept, m.outcome_concept, m.polarity,
                 m.study_ids, m.cmoc_ids, run_id),
            )
        conflicts = find_contradictions()
        for c in conflicts:
            conn.execute(
                "INSERT INTO contradictions (driver_concept, positive_studies, "
                "negative_studies, positive_contexts, negative_contexts, run_id) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                (c.driver_concept, c.positive_studies, c.negative_studies,
                 c.positive_contexts, c.negative_contexts, run_id),
            )

    log_audit_event(run_id, "synthesis_agent", "synthesis_computed",
                    detail={"demi_regularities": len(motifs),
                            "contradictions": len(conflicts)})
    return {"demi_regularities": len(motifs), "contradictions": len(conflicts)}
