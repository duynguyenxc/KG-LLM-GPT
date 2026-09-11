"""Transparent BM25 retrieval and an evidence graph; no semantic identity merging."""

from __future__ import annotations

import math
import re
from collections import Counter

import networkx as nx

STOP = set(
    "a an the of to and or in on for with as by from is are was were be that this it at students student learning reasoning clinical study reported not knowledge".split()
)


def terms(text: str) -> list[str]:
    return [
        word for word in re.findall(r"[a-z]+", text.lower()) if len(word) > 2 and word not in STOP
    ]


def retrieve_pages(
    query: str, pages: list[dict], top: int = 8, k1: float = 1.5, b: float = 0.75
) -> list[dict]:
    documents = [Counter(terms(page["text"])) for page in pages]
    lengths = [sum(doc.values()) for doc in documents]
    average = sum(lengths) / max(len(lengths), 1) or 1
    frequency = Counter(term for doc in documents for term in doc)
    ranked = []
    for page, document, length in zip(pages, documents, lengths):
        score = 0.0
        for term in set(terms(query)):
            count = document[term]
            if count:
                inverse = math.log(
                    1 + (len(pages) - frequency[term] + 0.5) / (frequency[term] + 0.5)
                )
                score += inverse * count * (k1 + 1) / (count + k1 * (1 - b + b * length / average))
        if score > 0:
            ranked.append({**page, "retrieval_score": score})
    return sorted(ranked, key=lambda row: (-row["retrieval_score"], row["paper_id"], row["page"]))[
        :top
    ]


def build_graph(
    findings: list[dict], seed: int, minimum_shared_terms: int
) -> tuple[dict, list[list[str]]]:
    """Reify each configuration. Similarity edges retrieve evidence; they do not assert causation."""
    nodes, edges = [], []
    projection = nx.Graph()
    bags = {}
    for finding in findings:
        identity = finding["finding_id"]
        projection.add_node(identity)
        nodes.append({"id": identity, "type": "finding", "paper_id": finding["paper_id"]})
        bags[identity] = set(
            terms(
                " ".join(finding[role] for role in ("context", "resource", "response", "outcome"))
            )
        )
        for role in ("context", "resource", "response", "outcome"):
            node_id = identity + ":" + role
            nodes.append(
                {
                    "id": node_id,
                    "type": role,
                    "label": finding[role],
                    "paper_id": finding["paper_id"],
                    "evidence_status": finding.get(role + "_status", "source_description"),
                }
            )
            edges.append({"source": identity, "target": node_id, "type": "has_" + role})
        for index, evidence in enumerate(finding["evidence"]):
            node_id = identity + f":evidence:{index}"
            nodes.append({"id": node_id, "type": "evidence", **evidence})
            edges.append(
                {
                    "source": identity + ":" + evidence["role"]
                    if evidence["role"] != "limitation"
                    else identity,
                    "target": node_id,
                    "type": "cites",
                }
            )
    identities = sorted(bags)
    for i, left in enumerate(identities):
        for right in identities[i + 1 :]:
            common = bags[left] & bags[right]
            if len(common) >= minimum_shared_terms:
                weight = len(common) / max(len(bags[left] | bags[right]), 1)
                projection.add_edge(left, right, weight=weight)
                edges.append(
                    {
                        "source": left,
                        "target": right,
                        "type": "lexical_retrieval_candidate",
                        "weight": weight,
                        "shared_terms": sorted(common),
                    }
                )
    if not findings:
        return {"nodes": nodes, "edges": edges}, []
    communities = (
        nx.community.louvain_communities(projection, seed=seed, weight="weight")
        if projection.number_of_edges()
        else [{node} for node in projection]
    )
    # Split disconnected subsets: Louvain itself does not guarantee connected communities.
    groups = [
        sorted(component)
        for group in communities
        for component in nx.connected_components(projection.subgraph(group))
    ]
    groups.sort(key=lambda group: group[0])
    return {
        "nodes": nodes,
        "edges": edges,
        "algorithm": "Louvain with connected-component split",
        "seed": seed,
        "causality_claim": "Similarity edges are retrieval aids only",
    }, groups
