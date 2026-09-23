"""Freeze source-support review packets without exposing machine audit verdicts."""

from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path

from res_pipeline.evidence.provenance import digest, read_json, write_json

FINDING_FIELDS = (
    "finding_id",
    "paper_id",
    "study_family_id",
    "availability",
    "source_path",
    "context",
    "resource",
    "response",
    "outcome",
    "direction",
    "comparator",
    "timepoint",
    "response_status",
    "outcome_status",
    "explanation",
    "limitations",
    "evidence",
)
THEORY_FIELDS = (
    "theory_id",
    "title",
    "context",
    "resource",
    "response",
    "outcome",
    "direction",
    "finding_ids",
    "explanation",
    "rival_explanations",
    "limitations",
    "evidence_gaps",
)
REVIEW_FIELDS = (
    "context_support",
    "resource_support",
    "response_support",
    "outcome_support",
    "direction_support",
    "comparator_and_time_support",
    "inference_labelling",
    "overall_support",
    "supporting_or_conflicting_source",
    "rationale",
    "proposed_correction",
    "reviewer",
    "reviewed_at",
    "minutes",
    "adjudication_reason",
)


def export_source_review(run: Path, destination: Path) -> dict:
    """Export every finding and final theory; preserve originals and entered human work."""
    inputs = [run / "findings.json", run / "programme_theory.json", run / "corpus_manifest.json"]
    findings = [{key: row[key] for key in FINDING_FIELDS} for row in read_json(inputs[0])]
    theories = [
        {key: row[key] for key in THEORY_FIELDS} for row in read_json(inputs[1])["theories"]
    ]
    identities = [row["finding_id"] for row in findings]
    if len(set(identities)) != len(identities):
        raise ValueError("Duplicate finding IDs")
    theory_ids = [row["theory_id"] for row in theories]
    if len(set(theory_ids)) != len(theory_ids):
        raise ValueError("Duplicate theory IDs")
    if any(set(row["finding_ids"]) - set(identities) for row in theories):
        raise ValueError("Theory refers to absent findings")
    destination.mkdir(parents=True, exist_ok=False)
    safe = html.escape
    content = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Source support review</title>",
        "<style>body{font:17px/1.6 system-ui;max-width:1100px;margin:40px auto;padding:0 24px;color:#20313a}details{padding:14px 0;border-bottom:1px solid #bbb}summary{cursor:pointer;font-weight:600}dt{font-weight:650;margin-top:12px}dd{margin:0;white-space:pre-wrap;overflow-wrap:anywhere}blockquote{border-left:3px solid #aab;padding-left:16px;margin-left:0;white-space:pre-wrap}.notice{background:#fff4d8;padding:16px}a{color:#005980}</style></head><body>",
        "<h1>Does the source support what the system says?</h1>",
        "<p class='notice'>Prepared forms; no human judgments entered. Machine critic verdicts, eligibility decisions and Richmond matching scores are withheld. This reviews source support, not reference recovery.</p>",
        f"<p>Run: {safe(run.name)}. Review population: all {len(findings)} extracted findings, including machine-excluded findings, and all {len(theories)} final theory statements. No statistical sample is claimed.</p>",
        "<ol><li>Reviewers A and B use separate forms independently. Review the original source passage, its design and limitations; a displayed quote alone is insufficient.</li><li>For each component, choose supported, partial, unsupported, unclear or not_applicable. Use unclear when the available source cannot resolve the claim; do not interpret missing full text as evidence against it.</li><li>For inference_labelling, choose appropriate, overclaimed, unclear or not_applicable. Distinguish an observed learner response, an author's interpretation and the system's hypothesis.</li><li>For overall_support, choose supported, partial, unsupported or unclear. A material error in context, causal direction, comparator, time or inference status prevents fully supported. Record a source locator and rationale; do not infer support from matching words.</li><li>For theories, inspect the linked findings and whether the cross-paper inference is warranted. Different papers may describe different conditions or the same study family. Record rivals and scope errors.</li><li>Record identity, date and time. After independent review, resolve disagreements in the adjudication form. Keep corrections separate from the frozen system output; a corrected output requires a new version and a separate after-intervention evaluation.</li></ol>",
        "<p>No precision or agreement score is reported before attributable reviews exist. Source-supported proportion and source assessability must use separately declared denominators; an unclear record is not automatically correct. Reference coverage requires the separate Richmond packet.</p>",
        "<p><a href='#findings'>Findings</a> · <a href='#theories'>Theories</a> · <a href='manifest.json'>Frozen input identities</a></p>",
    ]
    for kind, records, identity in [
        ("findings", findings, "finding_id"),
        ("theories", theories, "theory_id"),
    ]:
        content.append(f"<h2 id='{kind}'>{len(records)} {kind}</h2><p>")
        for reviewer in ("A", "B", "adjudication"):
            filename = f"source_support_{kind}_{reviewer}.csv"
            with (destination / filename).open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(
                    stream, fieldnames=["record_id", "packet_location", *REVIEW_FIELDS]
                )
                writer.writeheader()
                writer.writerows(
                    {
                        "record_id": row[identity],
                        "packet_location": f"index.html#{row[identity]}",
                        **dict.fromkeys(REVIEW_FIELDS, ""),
                    }
                    for row in records
                )
            content.append(f"<a href='{filename}'>Reviewer {reviewer}</a> &nbsp; ")
        content.append("</p>")
        for row in records:
            content.append(
                f"<details id='{safe(row[identity])}'><summary>{safe(row[identity])} | {safe(row.get('title', row.get('resource', '')))}</summary><dl>"
            )
            for key, value in row.items():
                if key in {"evidence", "source_path"}:
                    continue
                display = (
                    json.dumps(value, ensure_ascii=False, indent=2)
                    if isinstance(value, (dict, list))
                    else str(value)
                )
                content.append(f"<dt>{safe(key.replace('_', ' '))}</dt><dd>{safe(display)}</dd>")
            content.append("</dl>")
            for finding_id in row.get("finding_ids", []):
                content.append(
                    f"<a href='#{safe(finding_id)}'>Inspect {safe(finding_id)}</a> &nbsp; "
                )
            for evidence in row.get("evidence", []):
                source = Path(row["source_path"])
                if not source.is_absolute():
                    from res_pipeline.core.config import PROJECT_ROOT

                    source = PROJECT_ROOT / source
                link = (
                    f"<a href='{safe(source.resolve().as_uri())}#page={evidence['page']}'>Open original source</a>"
                    if source.is_file()
                    else "Original source file unavailable; inspect the run's supplied source text"
                )
                location = (
                    "Located passage"
                    if evidence["located"]
                    else "UNLOCATED model-proposed quotation; check original"
                )
                content.append(
                    f"<p>{safe(evidence['role'])}, page {evidence['page']}. {location}. {link}</p><blockquote>{safe(evidence.get('source_span') or evidence['quote'])}</blockquote>"
                )
            content.append("</details>")
    content.append(
        "<script>function reveal(){let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}const item=document.getElementById(id);if(item?.tagName==='DETAILS'){item.open=true;item.scrollIntoView();}}window.addEventListener('hashchange',reveal);reveal();</script></body></html>"
    )
    (destination / "index.html").write_text("\n".join(content), encoding="utf-8")
    write_json(destination / "review_data.json", {"findings": findings, "theories": theories})
    manifest = {
        "run": run.name,
        "stage": "source_support_review_preparation",
        "population": {"findings": len(findings), "theories": len(theories)},
        "human_reviews_completed": 0,
        "machine_verdicts_withheld": True,
        "reference_recovery": "Separate assessment; no Richmond reference included in this packet",
        "input_sha256": {path.name: digest(path.read_bytes()) for path in inputs},
    }
    write_json(destination / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export_source_review(args.run_dir, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
