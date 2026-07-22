"""Load the canonical LKG (parquet) into Neo4j for motif queries and visualization.

Neo4j is the DERIVED query/visualization layer (ARCHITECTURE D5) — rebuilt from
parquet at any time, never a source of truth. It enables Cypher motif queries over
typed C→M→O chains (the professor's "MOTIF detection") and Bloom/Browser exploration.

Setup: create a local DBMS in Neo4j Desktop 2, start it, and set NEO4J_URI /
NEO4J_USER / NEO4J_PASSWORD in ``.env``. This module is a no-op-safe import; it only
connects when :func:`load_lkg_into_neo4j` is called.

Graph model:
  (:Concept {id, type, label, family})  // canonical concept nodes
  (:Study  {id})
  (:CMOC   {id, polarity, statement, support})
  (Concept)-[:PROVIDES|TRIGGERS|ENABLES|LEADS_TO|CONSTRAINS {study_id, cmoc_id}]->(Concept)
  (Study)-[:REPORTS]->(CMOC)-[:HAS_ELEMENT]->(Concept)
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pandas as pd

from res_pipeline.core.config import OUTPUTS_DIR, get_settings


def _sanitize(records: list[dict]) -> list[dict]:
    """Coerce values to Neo4j-safe primitives (Decimal->float, NaN->None, arrays->list)."""
    import numpy as np

    out = []
    for rec in records:
        clean = {}
        for key, value in rec.items():
            if isinstance(value, Decimal):
                clean[key] = float(value)
            elif isinstance(value, (list, tuple, np.ndarray)):
                clean[key] = [float(x) if isinstance(x, Decimal) else x for x in value]
            elif isinstance(value, float) and value != value:  # NaN
                clean[key] = None
            elif value is None:
                clean[key] = None
            else:
                try:
                    clean[key] = None if pd.isna(value) else value
                except (TypeError, ValueError):
                    clean[key] = value
        out.append(clean)
    return out

_MOTIF_QUERIES = {
    "expertise_reversal": (
        "// Same driver concept with opposite-polarity outcomes across contexts\n"
        "MATCH (c1:Concept)-[r1]->(o1:Concept {type:'Outcome'})\n"
        "MATCH (c1)-[r2]->(o2:Concept {type:'Outcome'})\n"
        "WHERE r1.polarity='positive' AND r2.polarity='negative'\n"
        "RETURN c1.label AS driver, collect(DISTINCT o1.label) AS positive_outcomes,\n"
        "       collect(DISTINCT o2.label) AS negative_outcomes"
    ),
    "cmo_chains": (
        "// Full Context->Mechanism->Outcome chains\n"
        "MATCH (ctx:Concept {type:'Context'})-[:ENABLES]->(resp:Concept "
        "{type:'Mechanism_Response'})-[:LEADS_TO]->(out:Concept {type:'Outcome'})\n"
        "RETURN ctx.label, resp.label, out.label LIMIT 50"
    ),
}


def load_lkg_into_neo4j(lkg_dir: Path | None = None) -> dict:
    from neo4j import GraphDatabase

    settings = get_settings()
    import os

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")
    if not password:
        raise RuntimeError(
            "NEO4J_PASSWORD is empty. Create a DBMS in Neo4j Desktop, start it, and set "
            "NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD in .env before loading the graph."
        )

    lkg_dir = lkg_dir or (OUTPUTS_DIR / "lkg")
    entities = pd.read_parquet(lkg_dir / "entities.parquet")
    relationships = pd.read_parquet(lkg_dir / "relationships.parquet")
    cmocs = pd.read_parquet(lkg_dir / "cmocs.parquet")

    # Concept-level nodes: one per canonical_id, typed, with a representative label.
    concepts = (
        entities.dropna(subset=["canonical_id"])
        .sort_values("confidence", ascending=False)
        .groupby("canonical_id")
        .agg(type=("type", "first"), label=("title", "first"),
             family=("family_label", "first"))
        .reset_index()
    )

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        session.run("CREATE CONSTRAINT concept_id IF NOT EXISTS "
                    "FOR (c:Concept) REQUIRE c.id IS UNIQUE")
        session.run(
            "UNWIND $rows AS row CREATE (c:Concept) SET c=row",
            rows=_sanitize(concepts.rename(columns={"canonical_id": "id"}).to_dict("records")),
        )
        session.run(
            "UNWIND $rows AS row MERGE (s:Study {id: row.study_id}) "
            "CREATE (m:CMOC {id: row.id, polarity: row.polarity, "
            "statement: row.narrative_statement, support: row.verifier_support}) "
            "MERGE (s)-[:REPORTS]->(m)",
            rows=_sanitize(cmocs.to_dict("records")),
        )
        for predicate in ("PROVIDES", "TRIGGERS", "ENABLES", "LEADS_TO", "CONSTRAINS"):
            subset = relationships[relationships["description"] == predicate]
            if subset.empty:
                continue
            session.run(
                f"UNWIND $rows AS row MATCH (a:Concept {{id: row.source}}), "
                f"(b:Concept {{id: row.target}}) "
                f"CREATE (a)-[:{predicate} {{study_id: row.study_id, cmoc_id: row.cmoc_id}}]->(b)",
                rows=_sanitize(subset.to_dict("records")),
            )
    driver.close()
    return {"concepts": len(concepts), "cmocs": len(cmocs),
            "relationships": len(relationships)}
