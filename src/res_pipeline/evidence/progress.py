"""Export observed progress without inventing results for unexecuted stages."""

from __future__ import annotations

import json
from pathlib import Path

from res_pipeline.evidence.provenance import read_json, write_json
from res_pipeline.evidence.reporting import e, prose, write_csv


def export_progress(directory: Path, reference_path: Path) -> dict:
    papers = read_json(directory / "corpus_manifest.json")["papers"]
    completed = {
        path.stem: read_json(path) for path in sorted((directory / "papers").glob("*.json"))
    }
    findings = [finding for paper in completed.values() for finding in paper["findings"]]
    rows = []
    for paper in papers:
        identity = paper["paper_id"]
        extracted = directory / "calls" / ("extract_" + identity) / "parsed.json"
        rows.append(
            {
                "paper_id": identity,
                "title": paper["title"],
                "availability": paper["availability"],
                "extraction": "complete" if extracted.exists() else "pending",
                "source_audit": "complete" if identity in completed else "pending",
                "audited_findings": len(completed[identity]["findings"])
                if identity in completed
                else "",
                "eligible_findings": sum(
                    f["eligible_for_synthesis"] for f in completed[identity]["findings"]
                )
                if identity in completed
                else "",
            }
        )
    usage_path = directory / "usage.jsonl"
    usage = (
        [json.loads(line) for line in usage_path.read_text().splitlines()]
        if usage_path.exists()
        else []
    )
    status = {
        "machine_stages": "incomplete",
        "human_validation": "pending",
        "corpus_records": len(papers),
        "extracted_papers": sum(r["extraction"] == "complete" for r in rows),
        "audited_papers": len(completed),
        "audited_findings": len(findings),
        "eligible_findings_in_audited_subset": sum(f["eligible_for_synthesis"] for f in findings),
        "programme_theory_available": (directory / "programme_theory.json").exists(),
        "comparison_available": (directory / "comparison.json").exists(),
        "estimated_completed_call_cost_usd": round(
            sum(r.get("estimated_cost_usd", 0) for r in usage), 4
        ),
        "budget_charge_including_unresolved_usd": round(
            sum(r["budget_charge_usd"] for r in usage), 4
        ),
        "failure": read_json(directory / "failure.json")
        if (directory / "failure.json").exists()
        else None,
        "human_configuration_recovery": None,
        "human_kappa": None,
    }
    write_json(directory / "progress.json", status)
    write_csv(directory / "paper_progress.csv", rows, list(rows[0]))
    fields = [
        "finding_id",
        "paper_id",
        "context",
        "resource",
        "response",
        "outcome",
        "direction",
        "comparator",
        "timepoint",
        "response_status",
        "outcome_status",
        "all_quotes_located",
        "eligible_for_synthesis",
    ]
    evidence_rows = [
        {
            **{key: f[key] for key in fields},
            "ai_critic_verdict": f["critic"]["verdict"],
            "evidence": json.dumps(f["evidence"], ensure_ascii=False),
            "human_verdict": "",
        }
        for f in findings
    ]
    write_csv(
        directory / "partial_evidence_matrix.csv",
        evidence_rows,
        fields + ["ai_critic_verdict", "evidence", "human_verdict"],
    )
    reference = read_json(reference_path)
    plan = [
        {
            "reference_id": c["claim_id"],
            "reference_context": c["context"],
            "reference_resource": c["resource"],
            "reference_response": c["response"],
            "reference_outcome": c["outcome"],
            "reference_direction": c["direction"],
            "reference_page": c["pdf_page"],
            "system_theory_ids": "",
            "system_finding_ids": "",
            "context_match": "",
            "resource_match": "",
            "response_match": "",
            "outcome_match": "",
            "direction_match": "",
            "qualifiers_match": "",
            "comparison_status": "not_run"
            if not status["comparison_available"]
            else "see comparison.json",
            "ai_verdict": "",
            "human_coder_a": "",
            "human_coder_b": "",
            "adjudicated_verdict": "",
        }
        for c in reference["claims"]
    ]
    write_csv(directory / "comparison_plan.csv", plan, list(plan[0]))
    content = [
        "<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Research run progress</title>",
        "<style>body{font:17px/1.6 system-ui,sans-serif;max-width:1100px;margin:36px auto;padding:0 24px;color:#222}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:9px;border:1px solid #ccc;text-align:left;vertical-align:top}details{border-top:1px solid #ccc;padding:12px 0}summary{cursor:pointer;font-weight:bold}blockquote{white-space:pre-wrap;border-left:3px solid #bbb;padding-left:15px;margin-left:0}.status{background:#eee;padding:18px}a{color:#174b78}</style>",
        "<h1>What the system has produced so far</h1><p class='status'><strong>Incomplete run. Human validation pending.</strong> Extraction findings are available below. A final synthesis and Richmond comparison must not be inferred from this partial evidence.</p>",
        f"<p>Run: {e(directory.name)}. {status['extracted_papers']}/{len(papers)} papers extracted; {len(completed)}/{len(papers)} paper audits complete. {len(findings)} audited findings; {status['eligible_findings_in_audited_subset']} pass the machine evidence gate. A machine pass is not human validation.</p>",
        f"<p>Estimated completed-call cost: ${status['estimated_completed_call_cost_usd']:.4f}. This excludes the separate pilot. Unresolved calls retain conservative budget reservations.</p>",
        f"<p>Recorded interruption: {e((status['failure'] or {}).get('message', 'No failure record available.'))} See the progress JSON for technical details.</p>",
        "<p><a href='#evidence'>Inspect the findings</a> | <a href='#S016-F03'>Example: the one-week reflection result</a></p>",
        "<ul><li><a href='partial_evidence_matrix.csv'>Actual partial evidence matrix</a></li><li><a href='paper_progress.csv'>Progress for all 28 paper records</a></li><li><a href='comparison_plan.csv'>Richmond comparison layout: unexecuted fields remain blank</a></li><li><a href='progress.json'>Machine-readable progress</a></li></ul>",
        "<h2>How the final comparison will work</h2><p>Each reference row will place Richmond's conditional explanation beside an actual system theory, its finding IDs and source quotations. Review context, resource, learner response, outcome, direction and qualifiers. An unexecuted comparison is not a failure to recover a finding. The 18 reference rows are our explicit decomposition awaiting expert ratification, not Richmond's published CMOC count.</p>",
        "<h2>Paper coverage</h2><table><tr>"
        + "".join(f"<th>{e(k)}</th>" for k in rows[0])
        + "</tr>",
    ]
    content.extend(
        "<tr>" + "".join(f"<td>{e(v)}</td>" for v in row.values()) + "</tr>" for row in rows
    )
    content.append(
        "</table><h2 id='evidence'>Actual source-linked findings</h2><p>Each entry explains who was studied, what teaching resource was offered, how learners responded and what outcome was reported. Expand an entry to inspect its exact source passages.</p><input id='finding-search' aria-label='Search findings' placeholder='Search by finding ID, topic or phrase' style='font:inherit;padding:10px;width:95%;margin:12px 0'>"
    )
    for finding in findings:
        content.extend(
            [
                f"<details class='finding' id='{e(finding['finding_id'])}'><summary>{e(finding['finding_id'])}: {e(finding['resource'])}</summary>",
                f"<p>{e(prose(finding))}</p><p>Direction: {e(finding['direction'])}; comparator: {e(finding['comparator'])}; time: {e(finding['timepoint'])}.</p>",
                f"<p>Response: {e(finding['response_status'])}; outcome: {e(finding['outcome_status'])}; AI audit: {e(finding['critic']['verdict'])}; eligible: {finding['eligible_for_synthesis']}.</p><p>{e(finding['critic']['rationale'])}</p>",
            ]
        )
        for item in finding["evidence"]:
            location = (
                "Located source span" if item["located"] else "UNLOCATED model-proposed quotation"
            )
            content.append(
                f"<p>{e(finding['source_path'])}, p. {item['page']}, {e(item['role'])}: {location}; offsets {item['start']}:{item['end']}.</p><blockquote>{e(item.get('source_span') or item['quote'])}</blockquote>"
            )
        content.append(f"<p>Limits: {e('; '.join(finding['limitations']))}</p></details>")
    content.append(
        "<script>document.getElementById('finding-search').addEventListener('input',function(){const q=this.value.toLowerCase();document.querySelectorAll('details.finding').forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(q));});function reveal(){const el=document.getElementById(location.hash.slice(1));if(el&&el.tagName==='DETAILS')el.open=true;}window.addEventListener('hashchange',reveal);reveal();</script></html>"
    )
    (directory / "progress.html").write_text("\n".join(content), encoding="utf-8")
    return status
