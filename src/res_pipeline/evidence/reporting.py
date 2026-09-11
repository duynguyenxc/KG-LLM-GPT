"""Readable, self-contained HTML and correctly serialized machine/human comparison tables."""

from __future__ import annotations

import csv
import html
import json
from collections import Counter
from pathlib import Path

from res_pipeline.evidence.provenance import read_json, write_json
from res_pipeline.evidence.review import read_run_reviews


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    """DictWriter writes values, avoiding the legacy dict-row/pandas export defect."""
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def e(value) -> str:
    return html.escape(str(value))


def prose(value: dict) -> str:
    return (
        f"For {value['context']}, {value['resource']} may elicit {value['response']}, "
        f"with the following outcome: {value['outcome']}."
    )


def export_run(directory: Path) -> None:
    findings = read_json(directory / "findings.json")
    final = read_json(directory / "programme_theory.json")
    comparisons = read_json(directory / "comparison.json")
    reference = read_json(directory / "reference_snapshot.json")
    papers = read_json(directory / "corpus_manifest.json")["papers"]
    status = read_json(directory / "run_status.json")
    theories = {row["theory_id"]: row for row in final["theories"]}
    find_by_id = {row["finding_id"]: row for row in findings}
    reference_by_id = {row["claim_id"]: row for row in reference["claims"]}
    coder_a, coder_b, adjudicated, human_summary = read_run_reviews(directory, set(reference_by_id))
    usage = [json.loads(line) for line in (directory / "usage.jsonl").read_text().splitlines()]
    completed = [row for row in usage if row["status"] == "completed"]
    evidence = [item for finding in findings for item in finding["evidence"]]
    metrics = {
        **status,
        "ai_comparison_counts": dict(Counter(row["verdict"] for row in comparisons)),
        "human_adjudicated_rows": human_summary["adjudicated_rows"],
        "human_agreement_kappa": human_summary["kappa"],
        "human_configuration_recall": human_summary["configuration_recovery"],
        "quoted_spans": len(evidence),
        "located_spans": sum(item["located"] for item in evidence),
        "source_availability": dict(Counter(paper["availability"] for paper in papers)),
        "api_calls": len(completed),
        "input_tokens": sum(row["input_tokens"] for row in completed),
        "output_tokens": sum(row["output_tokens"] for row in completed),
        "estimated_api_cost_usd": round(sum(row["estimated_cost_usd"] for row in completed), 4),
        "cost_note": "Standard uncached-token estimate; final provider billing may be lower with caching",
        "support_note": "Quote location, AI claim audit and human evidence support are different measurements",
    }
    write_json(directory / "metrics.json", metrics)
    write_json(directory / "human_review_summary.json", human_summary)
    matrix = []
    human = []
    for result in comparisons:
        claim = reference_by_id[result["claim_id"]]
        row = {
            "reference_id": claim["claim_id"],
            "context_group": claim["context_group"],
            "richmond_context": claim["context"],
            "richmond_resource": claim["resource"],
            "richmond_response": claim["response"],
            "richmond_outcome": claim["outcome"],
            "richmond_direction": claim["direction"],
            "reference_location": f"PDF p. {claim['pdf_page']}; {claim['source_anchor']}",
            "system_theory_ids": "; ".join(result["theory_ids"]),
            "system_finding_ids": "; ".join(result["finding_ids"]),
            "system_explanations": "\n".join(prose(theories[key]) for key in result["theory_ids"]),
            "source_evidence": "\n".join(
                f"{fid}, p. {item['page']}, {item['role']}: {item['quote']}"
                for fid in result["finding_ids"]
                for item in find_by_id[fid]["evidence"]
            ),
            "ai_verdict": result["verdict"],
            "ai_rationale": result["rationale"],
            "critical_difference": result["critical_difference"],
            "review_question": result["review_question"],
            "human_coder_a": coder_a.get(claim["claim_id"], {}).get("verdict", ""),
            "human_coder_b": coder_b.get(claim["claim_id"], {}).get("verdict", ""),
            "adjudicated_verdict": adjudicated.get(claim["claim_id"], {}).get("verdict", ""),
            "adjudication_reason": adjudicated.get(claim["claim_id"], {}).get("rationale", ""),
        }
        for dimension in result["dimensions"]:
            row["match_" + dimension["dimension"]] = dimension["match"] + ": " + dimension["reason"]
        matrix.append(row)
        human.append(
            {
                "reference_id": claim["claim_id"],
                "reference_configuration": prose(claim),
                "reference_location": row["reference_location"],
                "system_theory_ids": "",
                "system_finding_ids": "",
                "context": "",
                "resource": "",
                "response": "",
                "outcome": "",
                "direction": "",
                "qualifiers": "",
                "verdict": "",
                "rationale": "",
                "reviewer": "",
                "reviewed_at": "",
                "minutes": "",
            }
        )
    write_csv(directory / "comparison_matrix.csv", matrix, list(matrix[0]))
    for filename in [
        "human_review_coder_A.csv",
        "human_review_coder_B.csv",
        "human_review_adjudication.csv",
    ]:
        if not (directory / filename).exists():
            write_csv(directory / filename, human, list(human[0]))
    finding_rows = [
        {
            "finding_id": finding["finding_id"],
            "paper_id": finding["paper_id"],
            "study_family_id": finding["study_family_id"],
            "availability": finding["availability"],
            **{
                key: finding[key]
                for key in [
                    "context",
                    "resource",
                    "response",
                    "outcome",
                    "direction",
                    "comparator",
                    "timepoint",
                    "response_status",
                    "outcome_status",
                ]
            },
            "ai_critic_verdict": finding["critic"]["verdict"],
            "all_quotes_located": finding["all_quotes_located"],
            "eligible_for_synthesis": finding["eligible_for_synthesis"],
            "limitations": "\n".join(finding["limitations"]),
            "evidence": json.dumps(finding["evidence"], ensure_ascii=False),
            "human_verdict": "",
        }
        for finding in findings
    ]
    write_csv(directory / "evidence_matrix.csv", finding_rows, list(finding_rows[0]))
    theory_rows = [
        {
            "theory_id": theory["theory_id"],
            "title": theory["title"],
            **{
                key: theory[key]
                for key in [
                    "context",
                    "resource",
                    "response",
                    "outcome",
                    "direction",
                    "explanation",
                ]
            },
            "finding_ids": "; ".join(theory["finding_ids"]),
            "rival_explanations": "\n".join(theory["rival_explanations"]),
            "limitations": "\n".join(theory["limitations"]),
            "evidence_gaps": "\n".join(theory["evidence_gaps"]),
            "human_approval": "",
        }
        for theory in final["theories"]
    ]
    write_csv(directory / "programme_theory.csv", theory_rows, list(theory_rows[0]))
    content = [
        "<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<title>Evidence synthesis and Richmond comparison</title><style>body{font:17px/1.6 system-ui,sans-serif;color:#202020;background:white;max-width:1180px;margin:40px auto;padding:0 24px}h1{font-size:34px;line-height:1.2}h2{margin-top:2.5em}h3{font-size:20px}a{color:#164570}table{border-collapse:collapse;width:100%;font-size:15px;margin:20px 0}th,td{border:1px solid #ccc;padding:12px;text-align:left;vertical-align:top}th{background:#eee}details{border-top:1px solid #bbb;padding:14px 0}summary{font-weight:650;cursor:pointer}blockquote{margin:12px 0;padding-left:16px;border-left:3px solid #ccc;white-space:pre-wrap}nav a{margin-right:20px}input{font:inherit;padding:8px;width:95%;margin:16px 0}.status{background:#eee;padding:16px}small{color:#555}code{word-break:break-all} .comparison td:first-child{width:47%}@media print{body{font-size:11px}details>*{display:block}input,nav{display:none}}</style>",
        "<h1>Evidence synthesis and Richmond comparison</h1>",
        "<p class='status'><strong>Exploratory machine run completed. Human validation pending.</strong> These results are inspectable research candidates. Automated agreement with Richmond is not evidence of human-level performance or causal validity.</p>",
        "<nav><a href='#results'>System results</a><a href='#comparison'>Richmond comparison</a><a href='#evidence'>Source evidence</a><a href='#files'>Files and human review</a></nav>",
        f"<p>Run: <code>{e(directory.name)}</code>. {len(papers)} included-paper records; {metrics['eligible_findings']} of {len(findings)} extracted findings passed the machine evidence gate; {len(theories)} provisional theory statements. Human-adjudicated comparison rows: <strong>{human_summary['adjudicated_rows']}/{len(comparisons)}</strong>.</p>",
        f"<p>Sources: {e(metrics['source_availability'])}. A supplied PDF is not a guarantee of complete or error-free text extraction. S013 and S020 share a study family. Source shortages and quarantined evidence limit recovery.</p>",
        f"<p>AI-assisted comparison: {e(metrics['ai_comparison_counts'])}. Estimated API cost: ${metrics['estimated_api_cost_usd']:.2f}. Quote location: {metrics['located_spans']}/{metrics['quoted_spans']}; this is a text-location check, not an entailment score.</p>",
        "<h2 id='results'>What the system concluded</h2>",
        f"<p>{e(final['overview'])}</p>",
    ]
    for theory in final["theories"]:
        refs = " ".join(f"<a href='#{e(fid)}'>{e(fid)}</a>" for fid in theory["finding_ids"])
        content.extend(
            [
                f"<details id='{e(theory['theory_id'])}' open><summary>{e(theory['theory_id'])}: {e(theory['title'])}</summary>",
                f"<p>{e(prose(theory))}</p><p>{e(theory['explanation'])}</p><p>Evidence: {refs}</p>",
                f"<p><strong>Rivals:</strong> {e('; '.join(theory['rival_explanations']))}</p>",
                f"<p><strong>Limits:</strong> {e('; '.join(theory['limitations']))}</p>",
                f"<p><strong>Still unknown:</strong> {e('; '.join(theory['evidence_gaps']))}</p></details>",
            ]
        )
    content.extend(
        [
            "<h2 id='comparison'>How to compare with Richmond</h2>",
            "<p>Read each reference explanation beside the system explanation. Check the context, resource, response, outcome, direction and qualifiers. The 18 rows are a project decomposition of Richmond's published branches, awaiting human ratification. They are not Richmond's published CMOC count. A shared label is insufficient for equivalence.</p>",
            "<input id='search' aria-label='Filter comparison rows' placeholder='Filter by context, claim ID or keyword'>",
        ]
    )
    for result in comparisons:
        claim = reference_by_id[result["claim_id"]]
        counterpart = "".join(
            f"<p><a href='#{e(tid)}'>{e(tid)}</a>: {e(prose(theories[tid]))}</p>"
            for tid in result["theory_ids"]
        )
        dimensions = "".join(
            f"<li><strong>{e(row['dimension'])}</strong> - {e(row['match'])}: {e(row['reason'])}</li>"
            for row in result["dimensions"]
        )
        content.extend(
            [
                f"<details class='comparison'><summary>{e(claim['claim_id'])} | {e(claim['context_group'])} | AI: {e(result['verdict'])} | Human: pending</summary>",
                f"<table><tr><th>Richmond</th><th>System</th></tr><tr><td>{e(prose(claim))}<p><small>PDF p. {claim['pdf_page']}; {e(claim['source_anchor'])}</small></p></td><td>{counterpart or 'No counterpart identified by the AI comparator.'}</td></tr></table>",
                f"<p>{e(result['rationale'])}</p><ul>{dimensions}</ul><p><strong>Critical difference:</strong> {e(result['critical_difference'])}</p>",
                f"<p><strong>Human review question:</strong> {e(result['review_question'])}</p></details>",
            ]
        )
    content.append("<h2 id='evidence'>Inspect the evidence behind every finding</h2>")
    for finding in findings:
        content.extend(
            [
                f"<details id='{e(finding['finding_id'])}'><summary>{e(finding['finding_id'])} | {e(finding['resource'])} | critic: {e(finding['critic']['verdict'])} | eligible: {finding['eligible_for_synthesis']}</summary>",
                f"<p>{e(prose(finding))}</p><p>Comparator: {e(finding['comparator'])}; time: {e(finding['timepoint'])}; direction: {e(finding['direction'])}.</p>",
                f"<p>Response status: {e(finding['response_status'])}; outcome status: {e(finding['outcome_status'])}. {e(finding['critic']['rationale'])}</p>",
                f"<p>Source: <code>{e(finding['source_path'])}</code>. Availability: {e(finding['availability'])}.</p>",
            ]
        )
        for item in finding["evidence"]:
            content.append(
                f"<p><strong>{e(item['role'])}</strong>, PDF/text page {item['page']}; location {e(item['method'])}; characters {item['start']}:{item['end']}.</p><blockquote>{e(item['quote'])}</blockquote>"
            )
        content.append(f"<p>Limits: {e('; '.join(finding['limitations']))}</p></details>")
    content.extend(
        [
            "<h2 id='files'>Files and human review</h2>",
            "<p>Two reviewers should independently inspect the source evidence and all system theories using the blank coder files, before viewing the AI verdicts. Record reasons and time spent. Resolve disagreements in an adjudication meeting. A different defensible interpretation may be useful; agreement alone does not establish truth.</p>",
            "<ul>"
            + "".join(
                f"<li><a href='{name}'>{label}</a></li>"
                for name, label in [
                    (
                        "blind_review.html",
                        "Independent review packet without AI comparison verdicts",
                    ),
                    ("comparison_matrix.csv", "Richmond comparison matrix"),
                    ("evidence_matrix.csv", "Paper-level evidence matrix"),
                    ("programme_theory.csv", "System programme theory"),
                    ("human_review_coder_A.csv", "Blank human coder A form"),
                    ("human_review_coder_B.csv", "Blank human coder B form"),
                    ("metrics.json", "Machine-readable metrics"),
                    ("human_review_adjudication.csv", "Human adjudication form"),
                    ("programme_theory.json", "Complete programme theory JSON"),
                    ("evidence_graph.json", "Evidence graph JSON"),
                    ("corpus_manifest.json", "Source manifest"),
                    ("retrieval_trace.json", "Return-to-source retrieval trace"),
                ]
            )
            + "</ul>",
            "<p>Screening/search replication was not run in this fixed-corpus experiment. A single refinement pass is not proof of theoretical saturation. Model training may contain the public Richmond paper; prompt isolation cannot rule out contamination. No human precision, recall, kappa or scientific-validity score is asserted.</p>",
            "<script>document.getElementById('search').addEventListener('input',function(){const q=this.value.toLowerCase();document.querySelectorAll('details.comparison').forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(q));});</script></html>",
        ]
    )
    (directory / "report.html").write_text("\n".join(content), encoding="utf-8")
    blind = [
        content[0],
        content[1],
        "<h1>Independent human review packet</h1><p>Review the reference and system outputs before opening the AI comparison. Record judgments in your assigned coder CSV. The reference decomposition itself also requires ratification.</p>",
        "<h2>Published reference configurations</h2>",
    ]
    for claim in reference["claims"]:
        blind.append(
            f"<h3>{e(claim['claim_id'])}</h3><p>{e(prose(claim))}</p><p>PDF p. {claim['pdf_page']}; {e(claim['source_anchor'])}</p>"
        )
    blind.append("<h2>System programme theory</h2>")
    for theory in final["theories"]:
        blind.append(
            f"<h3>{e(theory['theory_id'])}: {e(theory['title'])}</h3><p>{e(prose(theory))}</p><p>{e(theory['explanation'])}</p><p>Evidence: {e(', '.join(theory['finding_ids']))}</p><p>Limits: {e('; '.join(theory['limitations']))}</p><p>Rivals: {e('; '.join(theory['rival_explanations']))}</p>"
        )
    blind.append("<h2>Source evidence</h2>")
    for finding in findings:
        blind.append(
            f"<details><summary>{e(finding['finding_id'])}</summary><p>{e(prose(finding))}</p><p>Time: {e(finding['timepoint'])}; comparator: {e(finding['comparator'])}; response status: {e(finding['response_status'])}; outcome status: {e(finding['outcome_status'])}.</p>"
        )
        for item in finding["evidence"]:
            location = (
                "Located source text"
                if item["located"]
                else "UNLOCATED model-proposed quotation; verify against the original"
            )
            blind.append(
                f"<p>{e(finding['source_path'])}, page {item['page']}, {e(item['role'])}. {location}.</p><blockquote>{e(item.get('source_span') or item['quote'])}</blockquote>"
            )
        blind.append("</details>")
    blind.append("</html>")
    (directory / "blind_review.html").write_text("\n".join(blind), encoding="utf-8")
    (directory / "README.md").write_text(
        "# Evidence run\n\nOpen `report.html` for the readable result. Use `comparison_matrix.csv` for the external comparison and `evidence_matrix.csv` for source-level findings. All human verdicts are pending.\n\n"
        + "```json\n"
        + json.dumps(metrics, indent=2)
        + "\n```\n",
        encoding="utf-8",
    )
