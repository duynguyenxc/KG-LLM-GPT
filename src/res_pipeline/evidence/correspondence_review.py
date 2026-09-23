"""Offline reference-to-output review packets with explicit linked record identities.

Preparing forms is not reviewing them. No model matching or human verdict is generated here.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path

from res_pipeline.evidence.provenance import digest, locate_quote, read_json, write_json

VERDICTS = {
    "equivalent",
    "partial",
    "contradictory",
    "not_recovered",
    "uncertain",
    "reference_problem",
}
DIMENSIONS = [
    "subject_match",
    "object_match",
    "predicate_match",
    "context_match",
    "qualifiers_match",
    "inference_match",
]
FIELDS = [
    "reference_id",
    "verdict",
    "candidate_ids",
    "match_unit",
    *DIMENSIONS,
    "source_support",
    "source_locator_and_note",
    "reference_scope_note",
    "rationale",
    "reviewer",
    "reviewed_at",
    "minutes",
    "adjudication_reason",
]


def references(gold: dict) -> dict:
    return {
        "concepts": [{"id": k, **v} for k, v in gold["entities"].items()],
        "relations": [
            {
                **r,
                "subject_label": gold["entities"][r["subject_code"]]["label"],
                "object_label": gold["entities"][r["object_code"]]["label"],
                "location": "Inspect the whole Richmond configuration; endpoint label locations alone are insufficient.",
            }
            for r in gold["relationships"]
        ],
    }


def legacy_records(inspection: dict, pages: list[dict]) -> dict:
    """Keep historical predictions, omit machine review scores and later benchmark mappings."""
    entities, relations = [], []
    cmocs = {r["id"]: r for r in inspection["cmocs"]}
    by_id = {e["id"]: e for e in inspection["entities"]}
    if len(by_id) != len(inspection["entities"]):
        raise ValueError("Duplicate entity identifiers")
    for entity in inspection["entities"]:
        matches = []
        for page in pages:
            if page["paper_id"] != entity["study_id"]:
                continue
            located = locate_quote(page["text"], entity["description"])
            if located["located"]:
                matches.append({"page": page["page"], "quote": entity["description"], **located})
        entities.append(
            {
                "id": entity["id"],
                "label": entity["title"],
                "role": entity["type"],
                "paper_id": entity["study_id"],
                "scope_id": entity["cmoc_id"],
                "predicted_canonical_id": entity["canonical_id"],
                "evidence": matches
                or [{"page": None, "quote": entity["description"], "located": False}],
                "evidence_note": "Historical endpoint quotation located anew in the frozen September source text where possible. Location does not prove support or identity with July input text.",
            }
        )
    for relation in inspection["relationships"]:
        issues = []
        endpoints = {}
        for field in ("source", "target"):
            matches = [
                by_id[e]
                for e in relation.get("text_unit_ids", [])
                if e in by_id and by_id[e]["canonical_id"] == relation[field]
            ]
            if len(matches) != 1:
                endpoints[field] = None
                issues.append("unresolved_or_ambiguous_" + field)
            else:
                entity = matches[0]
                endpoints[field] = entity["id"]
                if (
                    entity["study_id"] != relation["study_id"]
                    or entity["cmoc_id"] != relation["cmoc_id"]
                ):
                    issues.append("endpoint_scope_mismatch")
        cmoc = cmocs.get(relation["cmoc_id"])
        if cmoc is None or cmoc["study_id"] != relation["study_id"]:
            issues.append("configuration_scope_mismatch")
        relations.append(
            {
                "id": relation["id"],
                "subject_id": endpoints["source"],
                "object_id": endpoints["target"],
                "endpoint_candidate_ids": relation.get("text_unit_ids", []),
                "legacy_canonical_source": relation["source"],
                "legacy_canonical_target": relation["target"],
                "predicate": relation["description"],
                "paper_id": relation["study_id"],
                "scope_id": relation["cmoc_id"],
                "narrative": cmoc["narrative_statement"] if cmoc else None,
                "polarity": cmoc["polarity"] if cmoc else None,
                "evidence": [],
                "evidence_note": "No relation-specific quotation is stored in this historical edge. Endpoint quotations and CMOC narrative are not independent proof of the relation.",
                "structural_issues": sorted(set(issues)),
            }
        )
    return {"entities": entities, "relations": relations}


def semantic_records(directory: Path) -> dict:
    status = read_json(directory / "run_status.json")
    if status["machine_stage"] != "complete":
        raise ValueError(
            "Semantic output has not completed its selected-paper pass; do not interpret unexecuted rows as non-recovery"
        )
    entities = [
        {
            "id": e["entity_id"],
            "label": e["label"],
            "role": e["role"],
            "paper_id": e["paper_id"],
            "scope_id": e["paper_id"],
            "representation": e["representation"],
            "evidence": e["evidence"],
            "interpretation_note": e["interpretation_note"],
        }
        for e in read_json(directory / "entities.json")
    ]
    allowed = {e["id"] for e in entities}
    relations = []
    for a in read_json(directory / "assertions.json"):
        relations.append(
            {
                "id": a["assertion_id"],
                "paper_id": a["paper_id"],
                "scope_id": a["paper_id"],
                "subject_id": a["subject_entity_id"],
                "object_id": a["object_entity_id"],
                **{
                    k: a[k]
                    for k in (
                        "predicate",
                        "context",
                        "comparator",
                        "timepoint",
                        "outcome_definition",
                        "statistical_direction",
                        "educational_interpretation",
                        "inference_status",
                        "explanation",
                        "limitations",
                        "evidence",
                    )
                },
                "structural_issues": ["unresolved_endpoint"]
                if {a["subject_entity_id"], a["object_entity_id"]} - allowed
                else [],
            }
        )
    return {"entities": entities, "relations": relations}


def validate_selection(row: dict, kind: str, candidates: dict) -> list[str]:
    """Structural admission only. Never infer semantic correspondence from a valid path."""
    issues = []
    ids = [v.strip() for v in row.get("candidate_ids", "").split(";") if v.strip()]
    if len(ids) != len(set(ids)):
        issues.append("duplicate_candidate_ids")
    if set(ids) - set(candidates):
        issues.append("unknown_candidate_ids")
        return issues
    verdict = row["verdict"]
    if verdict in {"equivalent", "partial", "contradictory"} and not ids:
        issues.append("correspondence_requires_actual_output_ids")
    if verdict == "not_recovered" and ids:
        issues.append("not_recovered_must_not_select_a_counterpart")
    if kind == "concepts" and ids and row.get("match_unit") != "entity":
        issues.append("concept_requires_entity_unit")
    if kind == "relations" and ids:
        selected = [candidates[i] for i in ids]
        if any(c.get("structural_issues") for c in selected):
            issues.append("selected_relation_has_unresolved_structure")
        unit = row.get("match_unit")
        if len(ids) == 1 and unit != "single_assertion":
            issues.append("single_relation_requires_single_assertion_unit")
        if len(ids) > 1:
            if unit != "connected_path":
                issues.append("multiple_relations_require_ordered_connected_path")
            if len({(c["paper_id"], c["scope_id"]) for c in selected}) != 1:
                issues.append("path_crosses_source_or_configuration_scope")
            if any(
                left["object_id"] != right["subject_id"]
                for left, right in zip(selected, selected[1:])
            ):
                issues.append("path_not_connected_by_actual_entity_ids")
        if verdict == "equivalent" and any(row.get(k) != "equivalent" for k in DIMENSIONS):
            issues.append("equivalence_requires_all_six_dimensions")
    return issues


def read_form(path: Path, kind: str, packet: dict) -> dict:
    expected = {r["id"] for r in packet["references"][kind]}
    candidates = {
        r["id"]: r for r in packet["candidates"]["entities" if kind == "concepts" else "relations"]
    }
    completed, seen = {}, set()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            key = row["reference_id"]
            if key in seen or key not in expected:
                raise ValueError("Unknown or duplicate reference ID: " + key)
            seen.add(key)
            if not row.get("verdict", "").strip():
                continue
            if row["verdict"] not in VERDICTS:
                raise ValueError("Unknown verdict: " + key)
            if not all(
                row.get(k, "").strip()
                for k in (
                    "reviewer",
                    "reviewed_at",
                    "rationale",
                    "reference_scope_note",
                    "source_locator_and_note",
                    "source_support",
                )
            ):
                raise ValueError("Incomplete attributable review: " + key)
            datetime.fromisoformat(row["reviewed_at"])
            if (
                not row.get("minutes")
                or not math.isfinite(float(row["minutes"]))
                or not float(row["minutes"]) >= 0
            ):
                raise ValueError("Missing or invalid review time: " + key)
            allowed_matches = {
                "",
                "equivalent",
                "partial",
                "different",
                "uncertain",
                "not_reported",
                "not_applicable",
            }
            if any(row.get(k, "") not in allowed_matches for k in DIMENSIONS):
                raise ValueError("Unknown dimension judgment: " + key)
            if row["source_support"] not in {
                "supported",
                "partial",
                "unsupported",
                "uncertain",
                "not_assessed",
            }:
                raise ValueError("Unknown source-support judgment: " + key)
            issues = validate_selection(row, kind, candidates)
            if issues:
                raise ValueError(f"Invalid correspondence record {key}: {issues}")
            completed[key] = row
    if seen != expected:
        raise ValueError("Form does not preserve the complete reference population")
    return completed


def validate_packet_forms(directory: Path) -> dict:
    packet = read_json(directory / "packet.json")
    manifest = read_json(directory / "manifest.json")
    if digest((directory / "packet.json").read_bytes()) != manifest["packet_sha256"]:
        raise ValueError("Frozen review packet changed")
    result = {}
    for kind in ("concepts", "relations"):
        forms = {
            role: read_form(directory / f"{kind}_{role}.csv", kind, packet)
            for role in ("A", "B", "adjudication")
        }
        paired = set(forms["A"]) & set(forms["B"])
        for key in paired:
            if (
                forms["A"][key]["reviewer"].strip().casefold()
                == forms["B"][key]["reviewer"].strip().casefold()
            ):
                raise ValueError("Independent A/B reviews must not name the same reviewer")
        for key, row in forms["adjudication"].items():
            if key not in paired or not row.get("adjudication_reason", "").strip():
                raise ValueError("Adjudication requires paired reviews and a recorded reason")
        result[kind] = {
            "reference_rows": len(packet["references"][kind]),
            "completed": {role: len(rows) for role, rows in forms.items()},
            "adjudicated_counts": dict(
                Counter(r["verdict"] for r in forms["adjudication"].values())
            ),
            "ratified_reference_recovery": None,
            "source_precision": None,
            "interpretation": "Reference is unratified; these forms cannot establish source precision over all generated claims. Attribution fields do not authenticate human identity.",
        }
    return result


def export_packet(
    root: Path,
    baseline: Path,
    destination: Path,
    *,
    inspection: Path | None = None,
    semantic_run: Path | None = None,
) -> dict:
    if (inspection is None) == (semantic_run is None):
        raise ValueError("Choose exactly one legacy inspection or semantic run")
    pages_path = baseline / "source_pages.json"
    corpus_path = baseline / "corpus_manifest.json"
    gold_path = root / "gold/richmond_gold.json"
    pdf_path = root / "data/paper-Richmond-original.pdf"
    files = [pages_path, corpus_path, gold_path, pdf_path]
    pages = read_json(pages_path)
    corpus = read_json(corpus_path)["papers"]
    if inspection is not None:
        files.append(inspection)
        candidates = legacy_records(read_json(inspection), pages)
        system_label = (
            "Historical July semantic output; not new September entity/relation extraction"
        )
    else:
        files += [
            semantic_run / n
            for n in (
                "entities.json",
                "assertions.json",
                "run_status.json",
                "manifest.json",
                "inputs/source_pages.json",
            )
        ]
        if digest((semantic_run / "inputs/source_pages.json").read_bytes()) != digest(
            pages_path.read_bytes()
        ):
            raise ValueError("Semantic output and displayed source text differ")
        candidates = semantic_records(semantic_run)
        system_label = "Conditional semantic assertions: " + semantic_run.name
    for rows in candidates.values():
        if len({r["id"] for r in rows}) != len(rows):
            raise ValueError("Duplicate candidate IDs")
    frozen = {str(p.resolve()): digest(p.read_bytes()) for p in files}
    packet = {
        "system_label": system_label,
        "reference_status": "historical operationalization, human ratification pending",
        "references": references(read_json(gold_path)),
        "candidates": candidates,
        "pages": pages,
        "sources": {
            p["paper_id"]: {
                "title": p["title"],
                "availability": p["availability"],
                "url": (root / p["source_path"]).resolve().as_uri()
                if p["source_path"].lower().endswith(".pdf")
                else None,
            }
            for p in corpus
        },
        "richmond_url": pdf_path.resolve().as_uri(),
        "independence_note": "No AI correspondence verdicts, match suggestions, confidence or source-critic judgments are included. Original generated labels/narratives remain the object being evaluated.",
    }
    destination.mkdir(parents=True, exist_ok=False)
    write_json(destination / "packet.json", packet)
    for kind in ("concepts", "relations"):
        for role in ("A", "B", "adjudication"):
            with (destination / f"{kind}_{role}.csv").open(
                "w", encoding="utf-8-sig", newline=""
            ) as stream:
                writer = csv.DictWriter(stream, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows({"reference_id": r["id"]} for r in packet["references"][kind])
    template_path = Path(__file__).with_name("correspondence_review.html")
    template = template_path.read_text(encoding="utf-8")
    serialized = json.dumps(packet, ensure_ascii=False).replace("<", "\\u003c")
    (destination / "index.html").write_text(
        template.replace("__PACKET_JSON__", serialized), encoding="utf-8"
    )
    manifest = {
        "stage": "reference_to_output_review_preparation",
        "system_label": system_label,
        "input_sha256": frozen,
        "packet_sha256": digest((destination / "packet.json").read_bytes()),
        "builder_sha256": digest(Path(__file__).read_bytes()),
        "template_sha256": digest(template_path.read_bytes()),
        "reference_counts": {k: len(v) for k, v in packet["references"].items()},
        "candidate_counts": {k: len(v) for k, v in candidates.items()},
        "human_reviews_completed": 0,
        "api_calls": 0,
    }
    if any(digest(Path(p).read_bytes()) != h for p, h in frozen.items()):
        raise ValueError("Inputs changed during packet generation")
    write_json(destination / "manifest.json", manifest)
    write_json(destination / "review_status.json", validate_packet_forms(destination))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--inspection", type=Path)
    parser.add_argument("--semantic-run", type=Path)
    args = parser.parse_args()
    if args.validate:
        print(json.dumps(validate_packet_forms(args.validate), indent=2))
        return
    if not args.baseline or not args.output_dir:
        parser.error("--baseline and --output-dir are required for preparation")
    from res_pipeline.core.config import PROJECT_ROOT

    result = export_packet(
        PROJECT_ROOT,
        args.baseline,
        args.output_dir,
        inspection=args.inspection,
        semantic_run=args.semantic_run,
    )
    print(json.dumps({k: v for k, v in result.items() if k != "input_sha256"}, indent=2))


if __name__ == "__main__":
    main()
