"""Entity Normalization Agent: cluster synonymous entity labels across studies.

Cross-study synthesis requires knowing that "self-efficacy", "self-confidence
calibrated to performance" and "confidence" refer to one concept. This agent
canonicalizes entity instances per entity type:

  * exact/near-exact string matches are merged mechanically;
  * remaining labels are clustered by an LLM pass constrained to the labels it is
    given (it may only group and name, never invent members);
  * every instance receives a ``canonical_id``; the mapping is persisted and
    audited (a merge is an analytic decision under RAMESES II transparency).

Canonical concepts are the nodes of the cross-study knowledge graph;
per-study instances (with their quotes/spans) remain the provenance layer.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from res_pipeline.core.db import get_connection, log_audit_event
from res_pipeline.core.llm import call_structured

PROMPT_VERSION = "normalization-v1.0"


class ConceptCluster(BaseModel):
    canonical_label: str = Field(description="Short canonical noun phrase for the concept.")
    member_labels: list[str] = Field(
        min_length=1,
        description="Labels from the provided list belonging to this concept. Copy exactly.",
    )


class ClusteringResult(BaseModel):
    clusters: list[ConceptCluster]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def build_concept_families(run_id: str) -> dict[str, int]:
    """Second-level clustering: canonical concepts -> broader concept FAMILIES.

    Richmond's analysis operates at family granularity (5 broad student contexts,
    ~12 intervention types). Demi-regularity detection therefore runs over
    families; the concept and instance layers below remain intact for provenance.
    """
    stats: dict[str, int] = {}
    with get_connection() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS concept_families ("
            " canonical_id TEXT PRIMARY KEY, entity_type TEXT NOT NULL,"
            " family_id TEXT NOT NULL, family_label TEXT NOT NULL,"
            " run_id TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now())"
        )
        conn.execute("DELETE FROM concept_families")
        types = [r["entity_type"] for r in conn.execute(
            "SELECT DISTINCT entity_type FROM entity_instances"
        ).fetchall()]

    for entity_type in types:
        with get_connection() as conn:
            concepts = [r["canonical_id"] for r in conn.execute(
                "SELECT DISTINCT canonical_id FROM entity_instances "
                "WHERE entity_type=%s AND canonical_id IS NOT NULL ORDER BY 1",
                (entity_type,),
            ).fetchall()]
        if not concepts:
            continue
        result = call_structured(
            tier="normalization",
            system_prompt=(
                f"You are grouping {entity_type} concepts from a realist synthesis of "
                "clinical-reasoning education into BROAD analytic families, at the "
                "granularity a published realist review would use for cross-study "
                "patterns (e.g., contexts like 'low prior knowledge' vs 'high prior "
                "knowledge' vs 'confidence/coping'; interventions like 'simulation/"
                "virtual patients', 'self-explanation', 'reasoning-strategy instruction', "
                "'feedback', 'worked examples', 'test-enhanced learning'). Rules: every "
                "provided concept id appears in exactly one family; copy ids exactly; "
                "prefer 4-12 families; name each family with a short analytic label."
            ),
            user_prompt="CONCEPT IDS:\n" + "\n".join(f"- {c}" for c in concepts),
            schema=ClusteringResult,
            run_id=run_id,
        )
        assigned: dict[str, tuple[str, str]] = {}
        for cluster in result.clusters:
            family_id = f"fam:{entity_type[:4].lower()}:{_slug(cluster.canonical_label)}"
            for member in cluster.member_labels:
                if member in concepts:
                    assigned[member] = (family_id, cluster.canonical_label)
        for concept in concepts:
            assigned.setdefault(concept, (f"fam:{concept}", concept))
        with get_connection() as conn:
            for canonical_id, (family_id, family_label) in assigned.items():
                conn.execute(
                    "INSERT INTO concept_families (canonical_id, entity_type, family_id, "
                    "family_label, run_id) VALUES (%s,%s,%s,%s,%s) "
                    "ON CONFLICT (canonical_id) DO UPDATE SET family_id=EXCLUDED.family_id, "
                    "family_label=EXCLUDED.family_label",
                    (canonical_id, entity_type, family_id, family_label, run_id),
                )
        stats[entity_type] = len({v[0] for v in assigned.values()})
        log_audit_event(run_id, "normalization_agent", "families_built",
                        subject_ref=entity_type,
                        detail={"n_concepts": len(concepts),
                                "n_families": stats[entity_type]})
    return stats


def normalize_entities(run_id: str) -> dict[str, int]:
    """Assign canonical_id to every entity instance, per entity type."""
    stats: dict[str, int] = {}
    with get_connection() as conn:
        types = [r["entity_type"] for r in conn.execute(
            "SELECT DISTINCT entity_type FROM entity_instances"
        ).fetchall()]

    for entity_type in types:
        with get_connection() as conn:
            labels = [r["label"] for r in conn.execute(
                "SELECT DISTINCT label FROM entity_instances WHERE entity_type=%s "
                "ORDER BY label",
                (entity_type,),
            ).fetchall()]
        if not labels:
            continue

        result = call_structured(
            tier="normalization",
            system_prompt=(
                "You are canonicalizing concept labels for a realist-synthesis knowledge "
                f"graph. All labels below are of type {entity_type}. Group labels that refer "
                "to the SAME underlying concept (synonyms, paraphrases, granularity variants) "
                "into clusters and give each cluster a short canonical label. Rules: every "
                "provided label appears in EXACTLY one cluster; copy member labels exactly; "
                "do NOT invent labels; when unsure, keep labels in separate clusters "
                "(over-merging corrupts the analysis, under-merging is recoverable)."
            ),
            user_prompt="LABELS:\n" + "\n".join(f"- {label}" for label in labels),
            schema=ClusteringResult,
            run_id=run_id,
        )

        # Build mapping with safety: unassigned/hallucinated labels fall back to themselves.
        assigned: dict[str, str] = {}
        for cluster in result.clusters:
            canonical_id = f"{entity_type[:4].lower()}:{_slug(cluster.canonical_label)}"
            for member in cluster.member_labels:
                if member in labels:
                    assigned[member] = canonical_id
        for label in labels:
            assigned.setdefault(label, f"{entity_type[:4].lower()}:{_slug(label)}")

        with get_connection() as conn:
            for label, canonical_id in assigned.items():
                conn.execute(
                    "UPDATE entity_instances SET canonical_id=%s "
                    "WHERE entity_type=%s AND label=%s",
                    (canonical_id, entity_type, label),
                )
        stats[entity_type] = len(set(assigned.values()))
        log_audit_event(
            run_id, "normalization_agent", "entity_type_normalized",
            subject_ref=entity_type,
            detail={"n_labels": len(labels), "n_concepts": len(set(assigned.values())),
                    "prompt_version": PROMPT_VERSION},
        )
    return stats
