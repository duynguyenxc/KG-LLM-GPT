"""Calculate human-review metrics only from attributable, completed coding records."""

from __future__ import annotations

import csv
import html
import json
from collections import Counter
from pathlib import Path

from res_pipeline.evidence.provenance import digest, read_json, write_json

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


def export_reference_packet(root: Path, destination: Path) -> dict:
    """Prepare source-ratification forms without machine-suggested human decisions.

    Reference ratification precedes scoring; it is distinct from evaluating system output.
    This snapshot is never overwritten, preserving any subsequently entered reviews.
    """
    legacy_path = root / "gold/richmond_gold.json"
    configuration_path = root / "gold/richmond_reference_v1.json"
    original_path = root / "data/paper-Richmond-original.pdf"
    legacy = read_json(legacy_path)
    configurations = read_json(configuration_path)
    concepts = legacy["entities"]
    rows = {"concepts": [], "relations": [], "configurations": []}
    for identity, item in concepts.items():
        rows["concepts"].append(
            {
                "reference_id": identity,
                "reference_text": item["label"],
                "reference_role": item["category"],
                "reference_location": item["location"],
                "reference_context": "",
                "reference_condition_note": "Check the complete source passage, not just the label",
            }
        )
    for item in legacy["relationships"]:
        subject, target = concepts[item["subject_code"]], concepts[item["object_code"]]
        rows["relations"].append(
            {
                "reference_id": item["id"],
                "reference_text": f"{item['subject_code']} ({subject['label']}) --{item['predicate']}--> {item['object_code']} ({target['label']})",
                "reference_role": item["predicate"],
                "reference_location": f"Endpoint locators only: {subject['location']}; {target['location']}",
                "reference_context": "",
                "reference_condition_note": "Legacy relation lacks an explicit context/time record and relation-specific source anchor. Locate and qualify the actual connection before ratification.",
            }
        )
    for item in configurations["claims"]:
        rows["configurations"].append(
            {
                "reference_id": item["claim_id"],
                "reference_text": json.dumps(
                    {
                        key: item[key]
                        for key in ["context", "resource", "response", "outcome", "direction"]
                    },
                    ensure_ascii=False,
                ),
                "reference_role": "conditional_explanation",
                "reference_location": f"PDF page {item['pdf_page']}; {item['source_anchor']}",
                "reference_context": item["context"],
                "reference_condition_note": "Project decomposition; not a published count of CMOCs. Check inference status and scope against the original.",
            }
        )
    blank = {
        key: ""
        for key in [
            "decision",
            "corrected_text",
            "corrected_role",
            "corrected_context",
            "source_page",
            "source_quote",
            "direction_and_qualifiers",
            "inference_status",
            "rationale",
            "reviewer",
            "reviewed_at",
            "minutes",
            "disagreement_resolution",
        ]
    }
    destination.mkdir(parents=True, exist_ok=False)
    escaped = html.escape
    content = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Richmond reference ratification</title>",
        "<style>body{font:17px/1.6 system-ui;max-width:1100px;margin:40px auto;padding:0 24px;color:#20313a}h1{line-height:1.2}details{padding:14px 0;border-bottom:1px solid #bbb}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit;background:#f4f6f8;padding:15px}.notice{background:#fff4d8;padding:16px}a{color:#005980}nav{display:flex;gap:18px;flex-wrap:wrap}li{margin:8px 0}</style></head><body>",
        "<h1>Check the reference before scoring the system</h1>",
        "<p class='notice'>Preparation only. All reviewer decisions are blank. The 47 concepts, 40 relations and 18 configuration branches are project coding of Richmond, not an author-supplied gold dataset. These are three different units of evaluation.</p>",
        f"<p><a href='{escaped(original_path.resolve().as_uri())}'>Open the original Richmond paper</a>. PDF page 1 is journal page 709. Figure 2 is PDF page 5; Figure 3 is PDF page 7.</p>",
        "<ol><li>Reviewer A and reviewer B work independently with separate forms and the original paper. Do not consult each other's decisions or AI comparison scores.</li><li>For each row, choose retain, revise, reject or uncertain. Record the source page, quote, qualifiers and reason. A word appearing in the paper does not establish a relation.</li><li>For relations, verify the actual connection, context and direction. An endpoint locator alone is insufficient. Record revisions explicitly, preserving the old row.</li><li>Record reviewer identity, date and time spent. Only after both reviews, resolve differences in the adjudication form.</li><li>Freeze a ratified reference version. Then evaluate frozen system entities/relations and complete explanations against it. Separately judge whether generated claims are supported by primary sources. This packet prepares the reference; it does not report system scores.</li></ol>",
        "<nav><a href='#concepts'>47 concepts</a><a href='#relations'>40 relations</a><a href='#configurations'>18 configurations</a><a href='reference_packet_manifest.json'>Source identities</a></nav>",
    ]
    for kind, records in rows.items():
        fields = list(records[0]) + list(blank)
        content.append(f"<h2 id='{kind}'>{len(records)} {kind}</h2><p>")
        for role in ["A", "B", "adjudication"]:
            filename = f"reference_{kind}_{role}.csv"
            with (destination / filename).open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows({**record, **blank} for record in records)
            content.append(f"<a href='{filename}'>Form {role}</a> &nbsp; ")
        content.append("</p>")
        for row in records:
            content.append(
                f"<details><summary>{escaped(row['reference_id'])} | {escaped(row['reference_role'])}</summary><pre>{escaped(row['reference_text'])}</pre><p>{escaped(row['reference_location'])}</p><p>{escaped(row['reference_condition_note'])}</p></details>"
            )
    content.append("</body></html>")
    (destination / "index.html").write_text("\n".join(content), encoding="utf-8")
    manifest = {
        "stage": "reference_ratification_preparation",
        "human_reviews_completed": 0,
        "counts": {key: len(value) for key, value in rows.items()},
        "input_sha256": {
            path.relative_to(root).as_posix(): digest(path.read_bytes())
            for path in [legacy_path, configuration_path, original_path]
        },
        "allowed_decisions": ["retain", "revise", "reject", "uncertain"],
        "system_evaluation": "separate stage; no recovery or precision score inferred here",
    }
    write_json(destination / "reference_packet_manifest.json", manifest)
    return manifest
