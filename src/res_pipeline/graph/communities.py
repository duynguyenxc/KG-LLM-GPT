"""Community detection over the CMOC graph → community-defined conceptual entities.

This is the professor's *named key novelty* (RRE abstract §3.1; verification plan
Step 3-4): rather than predefining every construct, the recurrent, cross-study
structure of the knowledge graph is partitioned by **Leiden community detection**,
and each community is read as an *emergent conceptual entity* (e.g. "cognitive-load
regulation"). These communities are then compared to Richmond's human-articulated
mechanisms (community_alignment).

Graph model:
  * nodes  = canonical entities (post-normalisation), typed C/I/Mres/Mresp/O;
  * edges  = (a) co-occurrence within the same CMOC (weight 1) and
             (b) typed causal relations between entities (weight 2, stronger signal).
Leiden runs via graspologic (the same implementation Microsoft GraphRAG uses); if
graspologic is unavailable the code falls back to NetworkX's built-in Louvain and
records which algorithm ran (transparency — no silent substitution).
"""

from __future__ import annotations

import itertools
import json

import networkx as nx
from pydantic import BaseModel, Field

from res_pipeline.core.agents import persona
from res_pipeline.core.db import get_connection, log_audit_event
from res_pipeline.core.llm import call_structured

RESOLUTION = 1.0
_SEED = 20260714


class ConceptLabel(BaseModel):
    label: str = Field(description="Concise concept name for this cluster (<=6 words).")
    definition: str = Field(description="One sentence defining what the members share.")


def _load_graph() -> tuple[nx.Graph, dict]:
    """Build the undirected weighted CMOC graph over canonical entities."""
    with get_connection() as conn:
        ents = conn.execute(
            "SELECT entity_id, canonical_id, entity_type, label, study_id, cmoc_id "
            "FROM entity_instances WHERE canonical_id IS NOT NULL"
        ).fetchall()
        rels = conn.execute(
            "SELECT subject_entity_id, object_entity_id FROM typed_relations"
        ).fetchall()

    # canonical node metadata + entity_id -> canonical_id map
    meta: dict[str, dict] = {}
    eid_to_canon: dict[str, str] = {}
    cmoc_members: dict[str, set[str]] = {}
    for r in ents:
        cid = r["canonical_id"]
        eid_to_canon[r["entity_id"]] = cid
        m = meta.setdefault(cid, {"type": r["entity_type"], "labels": {}, "studies": set()})
        m["labels"][r["label"]] = m["labels"].get(r["label"], 0) + 1
        m["studies"].add(r["study_id"])
        cmoc_members.setdefault(r["cmoc_id"], set()).add(cid)

    g = nx.Graph()
    for cid, m in meta.items():
        rep = max(m["labels"], key=m["labels"].get)  # most frequent surface label
        g.add_node(cid, entity_type=m["type"], label=rep, studies=sorted(m["studies"]))

    def _bump(a: str, b: str, w: float) -> None:
        if a == b or a not in meta or b not in meta:
            return
        if g.has_edge(a, b):
            g[a][b]["weight"] += w
        else:
            g.add_edge(a, b, weight=w)

    for members in cmoc_members.values():           # co-occurrence edges
        for a, b in itertools.combinations(sorted(members), 2):
            _bump(a, b, 1.0)
    for r in rels:                                   # typed causal edges (stronger)
        a = eid_to_canon.get(r["subject_entity_id"])
        b = eid_to_canon.get(r["object_entity_id"])
        if a and b:
            _bump(a, b, 2.0)
    return g, meta


def _partition(g: nx.Graph) -> tuple[dict[str, int], str]:
    """Return {node: community_id} and the algorithm name actually used."""
    if g.number_of_edges() == 0:
        return {n: i for i, n in enumerate(g.nodes())}, "singletons(no-edges)"
    try:
        from graspologic.partition import leiden
        return leiden(g, resolution=RESOLUTION, random_seed=_SEED,
                      weight_attribute="weight", check_directed=False), "leiden(graspologic)"
    except Exception:  # noqa: BLE001 — fall back transparently
        communities = nx.community.louvain_communities(
            g, weight="weight", resolution=RESOLUTION, seed=_SEED
        )
        return ({n: i for i, comm in enumerate(communities) for n in comm},
                "louvain(networkx-fallback)")


def detect_communities(run_id: str, min_size: int = 2) -> dict:
    """Detect communities, label each as a conceptual entity, and persist."""
    g, _meta = _load_graph()
    node_comm, algo = _partition(g)

    groups: dict[int, list[str]] = {}
    for node, comm in node_comm.items():
        groups.setdefault(comm, []).append(node)

    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conceptual_entities (
                id BIGSERIAL PRIMARY KEY,
                community_key INT NOT NULL,
                community_label TEXT NOT NULL,
                definition TEXT NOT NULL,
                entity_type TEXT NOT NULL,          -- dominant type in the community
                member_canonical_ids TEXT[] NOT NULL,
                member_labels TEXT[] NOT NULL,
                study_ids TEXT[] NOT NULL,
                member_count INT NOT NULL,
                algorithm TEXT NOT NULL,
                run_id TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        conn.execute("DELETE FROM conceptual_entities")

        kept = 0
        for comm_key, nodes in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            if len(nodes) < min_size:
                continue
            labels = [g.nodes[n]["label"] for n in nodes]
            types = [g.nodes[n]["entity_type"] for n in nodes]
            dominant_type = max(set(types), key=types.count)
            studies = sorted({s for n in nodes for s in g.nodes[n]["studies"]})

            named = call_structured(
                tier="normalization",
                system_prompt=persona("community_analyst"),
                user_prompt=(
                    f"This community clusters {len(nodes)} entities (dominant type "
                    f"{dominant_type}) that recur together across {len(studies)} studies:\n"
                    + ", ".join(labels[:40])
                    + "\n\nGive the cluster a concept label and one-line definition."
                ),
                schema=ConceptLabel, run_id=run_id,
            )
            conn.execute(
                "INSERT INTO conceptual_entities (community_key, community_label, definition, "
                "entity_type, member_canonical_ids, member_labels, study_ids, member_count, "
                "algorithm, run_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (comm_key, named.label, named.definition, dominant_type, nodes, labels,
                 studies, len(nodes), algo, run_id),
            )
            kept += 1

    summary = {"algorithm": algo, "nodes": g.number_of_nodes(),
               "edges": g.number_of_edges(), "communities_total": len(groups),
               "conceptual_entities": kept}
    log_audit_event(run_id, "community_analyst", "communities_detected", detail=summary)
    return summary
