"""Export the typed knowledge layer to the canonical Literature Knowledge Graph.

Emits GraphRAG-compatible parquet tables (the "bring-your-own-graph" contract,
ARCHITECTURE D1/D5) plus a self-describing manifest. These parquet files are the
reproducible, inspectable LKG artifact that ships as the paper's online supplement
and is the single input to the Neo4j and (optional) GraphRAG-index layers.

Tables written to ``outputs/lkg/``:
  * entities.parquet       — one row per entity instance (id, type, label,
                             canonical_id, family_id, quote, span, provenance)
  * relationships.parquet  — GraphRAG schema (source, target, description=predicate,
                             weight, text_unit_ids) for every valid typed relation
  * cmocs.parquet          — one row per CMOC (study, polarity, statement, support)
  * communities.parquet    — concept families as GraphRAG-style communities
  * manifest.json          — counts, schema notes, generation provenance
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from res_pipeline.core.config import OUTPUTS_DIR
from res_pipeline.core.db import get_connection, log_audit_event


def export_lkg(run_id: str, out_dir: Path | None = None) -> dict:
    out_dir = out_dir or (OUTPUTS_DIR / "lkg")
    out_dir.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        entities = pd.DataFrame(conn.execute(
            """
            SELECT e.entity_id AS id, e.entity_type AS type, e.label AS title,
                   e.canonical_id, f.family_id, f.family_label,
                   e.study_id, e.cmoc_id, e.verbatim_quote AS description,
                   e.char_start, e.char_end, e.quote_resolved, e.match_kind,
                   e.confidence, e.extractor_model, e.prompt_version
            FROM entity_instances e
            LEFT JOIN concept_families f ON f.canonical_id = e.canonical_id
            """
        ).fetchall())

        relationships = pd.DataFrame(conn.execute(
            """
            SELECT tr.relation_id AS id, se.canonical_id AS source, oe.canonical_id AS target,
                   tr.predicate AS description, 1.0 AS weight,
                   tr.study_id, tr.cmoc_id, tr.constraint_valid,
                   ARRAY[se.entity_id, oe.entity_id] AS text_unit_ids
            FROM typed_relations tr
            JOIN entity_instances se ON se.entity_id = tr.subject_entity_id
            JOIN entity_instances oe ON oe.entity_id = tr.object_entity_id
            """
        ).fetchall())

        cmocs = pd.DataFrame(conn.execute(
            "SELECT cmoc_id AS id, study_id, polarity, narrative_statement, "
            "verifier_support, verifier_notes FROM cmocs"
        ).fetchall())

        communities = pd.DataFrame(conn.execute(
            "SELECT family_id AS id, entity_type, family_label AS title, "
            "array_agg(canonical_id) AS members FROM concept_families "
            "GROUP BY family_id, entity_type, family_label"
        ).fetchall())

    for name, df in [("entities", entities), ("relationships", relationships),
                     ("cmocs", cmocs), ("communities", communities)]:
        df.to_parquet(out_dir / f"{name}.parquet", index=False)

    manifest = {
        "generated_run_id": run_id,
        "counts": {"entities": len(entities), "relationships": len(relationships),
                   "cmocs": len(cmocs), "communities": len(communities)},
        "schema": {
            "entities": "GraphRAG-compatible node table; type=realist entity type; "
                        "canonical_id/family_id = normalization layers; description=verbatim quote",
            "relationships": "GraphRAG-compatible edge table; description=typed predicate; "
                             "source/target = canonical concept ids",
        },
        "note": "Canonical Literature Knowledge Graph artifact (BYOG contract). "
                "Load into Neo4j via graph.neo4j_adapter, or into a GraphRAG index.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    log_audit_event(run_id, "lkg_export", "lkg_exported", detail=manifest["counts"])
    return manifest["counts"]
