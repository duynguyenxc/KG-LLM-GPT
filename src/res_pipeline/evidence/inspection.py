"""Build an offline, identifiable inspection snapshot from real saved outputs.

This exporter does not extract, merge, validate or invent semantic relationships.
It keeps the legacy semantic graph separate from the evidence attribution graph.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pyarrow.parquet as pq

from res_pipeline.evidence.provenance import digest, write_json
from res_pipeline.evidence.reporting import write_csv


def serializable(value):
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(item) for item in value]
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def load_inspection(run: Path, legacy: Path, root: Path) -> dict:
    """Read actual records and retain hashes of every input used in the snapshot."""
    inputs = {}

    def load(path: Path):
        raw = path.read_bytes()
        inputs[path.resolve().as_posix()] = digest(raw)
        if path.suffix == ".parquet":
            return serializable(pq.read_table(path).to_pylist())
        return json.loads(raw)

    entities = load(legacy / "entities.parquet")
    relationships = load(legacy / "relationships.parquet")
    cmocs = load(legacy / "cmocs.parquet")
    manifest = load(run / "corpus_manifest.json")
    findings = [
        finding
        for path in sorted((run / "papers").glob("*.json"))
        for finding in load(path)["findings"]
    ]
    graph_path = run / "evidence_graph.json"
    if not graph_path.exists():
        graph_path = run / "partial_evidence_graph.json"
    graph = load(graph_path) if graph_path.exists() else {"nodes": [], "edges": []}
    status_path = run / "run_status.json"
    if not status_path.exists():
        status_path = run / "progress.json"
    status = load(status_path)
    # A run may have advanced since the last progress export. Inspect paper files directly.
    audited_papers = len(list((run / "papers").glob("*.json")))
    theory_path = run / "programme_theory.json"
    theories = load(theory_path).get("theories", []) if theory_path.exists() else []
    comparison_path = run / "comparison.json"
    comparison = load(comparison_path) if comparison_path.exists() else []
    theory_by_id = {row["theory_id"]: row for row in theories}
    comparison_issues = []
    for row in comparison:
        selected_evidence = {
            fid
            for tid in row["theory_ids"]
            for fid in theory_by_id.get(tid, {}).get("finding_ids", [])
        }
        unlinked = sorted(set(row["finding_ids"]) - selected_evidence)
        if unlinked:
            comparison_issues.append(
                {
                    "claim_id": row["claim_id"],
                    "unlinked_finding_ids": unlinked,
                    "issue": "These findings are not linked to the selected theory statements. The original AI verdict is preserved, but must not be used as validated theory-recovery evidence.",
                }
            )
    reference_path = run / "reference_snapshot.json"
    reference = load(reference_path).get("claims", []) if reference_path.exists() else []
    nodes = {node["id"] for node in graph["nodes"]}
    if len(nodes) != len(graph["nodes"]):
        raise ValueError("Duplicate evidence graph node IDs")
    if any(edge["source"] not in nodes or edge["target"] not in nodes for edge in graph["edges"]):
        raise ValueError("Evidence graph has unresolved endpoints")
    by_id = {row["id"]: row for row in entities}
    if len(by_id) != len(entities):
        raise ValueError("Duplicate legacy entity IDs")
    cmoc_ids = {row["id"] for row in cmocs}
    # Retain bad historical records, but make referential defects explicit.
    relationship_issues = []
    for relation in relationships:
        refs = relation.get("text_unit_ids") or []
        if not refs or any(identity not in by_id for identity in refs):
            relationship_issues.append({"id": relation["id"], "issue": "missing_entity_reference"})
        else:
            endpoints = {by_id[identity]["canonical_id"] for identity in refs}
            if relation["source"] not in endpoints or relation["target"] not in endpoints:
                relationship_issues.append({"id": relation["id"], "issue": "endpoint_mismatch"})
        if relation["cmoc_id"] not in cmoc_ids:
            relationship_issues.append({"id": relation["id"], "issue": "missing_configuration"})
    source_links = {}
    for paper in manifest["papers"]:
        path = (root / paper["source_path"]).resolve()
        source_links[paper["paper_id"]] = {
            "title": paper["title"],
            "availability": paper["availability"],
            "url": path.as_uri() if path.is_file() and path.suffix.lower() == ".pdf" else None,
        }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run": run.name,
        "status": status,
        "audited_papers_observed": audited_papers,
        "entities": entities,
        "relationships": relationships,
        "cmocs": cmocs,
        "findings": findings,
        "graph_nodes": graph["nodes"],
        "graph_edges": graph["edges"],
        "graph_file": graph_path.name if graph_path.exists() else None,
        "graph_edge_types": dict(Counter(edge["type"] for edge in graph["edges"])),
        "theories": theories,
        "comparisons": comparison,
        "comparison_reference_issues": comparison_issues,
        "reference_claims": reference,
        "source_links": source_links,
        "relationship_reference_issues": relationship_issues,
        "input_sha256": inputs,
        "interpretation": {
            "legacy": "Historical machine output; canonicalization and semantic support are not ratified.",
            "evidence_graph": "Attribution and retrieval graph; edges are not all causal relations.",
            "human_validation": "No human validation is inferred from displaying these records.",
        },
    }


def export_inspection(run: Path, legacy: Path, destination: Path, root: Path) -> dict:
    data = load_inspection(run, legacy, root)
    # A snapshot is not overwritten, including if the previous export was interrupted.
    destination.mkdir(parents=True, exist_ok=False)
    write_json(destination / "inspection_data.json", data)
    for key in [
        "entities",
        "relationships",
        "cmocs",
        "findings",
        "graph_nodes",
        "graph_edges",
        "theories",
        "comparisons",
    ]:
        rows = data[key]
        fields = sorted({field for row in rows for field in row})
        if fields:
            flattened = [
                {
                    field: json.dumps(row[field], ensure_ascii=False)
                    if isinstance(row.get(field), (dict, list))
                    else row.get(field)
                    for field in fields
                }
                for row in rows
            ]
            write_csv(destination / (key + ".csv"), flattened, fields)
    payload = json.dumps(data, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c")
    (destination / "index.html").write_text(
        HTML.replace("__INSPECTION_DATA__", payload), encoding="utf-8"
    )
    summary = {
        "run": data["run"],
        "legacy_entity_instances": len(data["entities"]),
        "legacy_canonical_ids": len({row["canonical_id"] for row in data["entities"]}),
        "legacy_relationship_records": len(data["relationships"]),
        "legacy_cmocs": len(data["cmocs"]),
        "new_findings": len(data["findings"]),
        "evidence_graph_nodes": len(data["graph_nodes"]),
        "evidence_graph_edge_types": data["graph_edge_types"],
        "relationship_reference_issues": data["relationship_reference_issues"],
        "comparison_reference_issues": data["comparison_reference_issues"],
        "human_validation": "not established by this inspection",
        "input_sha256": data["input_sha256"],
    }
    write_json(destination / "inspection_manifest.json", summary)
    return summary


HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Research output explorer</title>
<style>
:root{font:16px/1.55 system-ui,sans-serif;color:#20313a;background:#f4f6f8}*{box-sizing:border-box}
body{margin:0}header{background:#143a49;color:#fff;padding:28px 4vw}h1{font-size:30px;margin:0}header p{max-width:1050px;margin:10px 0 0}
main{padding:24px 4vw}nav{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}button,select,input{font:inherit;padding:9px;border:1px solid #aab7bd;border-radius:5px;background:white;color:#20313a}
button{cursor:pointer}button[aria-pressed=true]{background:#143a49;color:white}input{width:100%}
.cards{display:flex;flex-wrap:wrap;gap:12px}.card{background:white;border:1px solid #dce2e5;border-radius:8px;padding:14px;flex:1;min-width:180px}.card strong{display:block;font-size:25px}
.notice{padding:14px;background:#fff4d8;border-left:4px solid #967000;margin:15px 0}.layout{display:grid;grid-template-columns:minmax(340px,1fr) minmax(420px,1.3fr);gap:20px}
.panel{background:white;border:1px solid #dce2e5;border-radius:8px;padding:18px;min-width:0}.results{max-height:670px;overflow:auto;margin-top:14px}
.record{display:block;text-align:left;width:100%;border:0;border-bottom:1px solid #dce2e5;border-radius:0;padding:12px;overflow-wrap:anywhere}.record:hover{background:#edf4f6}.record small{display:block;color:#52636c}
h2{font-size:22px;margin-top:0}h3{font-size:18px}dl{display:grid;grid-template-columns:130px 1fr;gap:9px}dt{font-weight:650}dd{margin:0;white-space:pre-wrap;overflow-wrap:anywhere}
blockquote{margin:12px 0;padding:12px 15px;background:#f4f6f8;border-left:3px solid #7997a4;white-space:pre-wrap}a{color:#005980}code{overflow-wrap:anywhere;font-size:13px}svg{width:100%;height:auto;background:#f8fafb}svg text{font:12px system-ui;fill:#20313a}.downloads{display:flex;gap:14px;flex-wrap:wrap;margin-top:20px}
@media(max-width:950px){.layout{grid-template-columns:1fr}.results{max-height:380px}}@media print{.results{max-height:none}nav,input{display:none}.layout{display:block}}
</style></head><body><header><h1>Research output explorer</h1><p>Inspect what was actually saved: entities, relationships, findings and their evidence. The July semantic graph and September evidence graph are different representations. Their counts are not quality scores.</p></header>
<main><div id="cards" class="cards"></div><div id="state" class="notice"></div>
<nav id="tabs" aria-label="Output datasets"></nav><p id="meaning"></p>
<div class="layout"><section class="panel"><label for="search">Search records, concepts, paper IDs or evidence</label><input id="search" placeholder="Try S006, feedback, fear, or a record ID"><p id="count" aria-live="polite"></p><div id="records" class="results"></div></section>
<section class="panel" id="detail" aria-live="polite"><h2>Select a record</h2><p>Each item opens its actual fields, links and source evidence here.</p></section></div>
<div class="downloads"><a href="inspection_data.json">Complete snapshot JSON</a><a href="inspection_manifest.json">Source hashes</a><a id="download" href="entities.csv">Current dataset CSV</a></div>
<p>This snapshot makes records inspectable. It does not certify source entailment, causal validity or human agreement. Historical canonical labels and prior machine judgments are retained for scrutiny.</p></main>
<script id="data" type="application/json">__INSPECTION_DATA__</script><script>
const data=JSON.parse(document.getElementById('data').textContent);
const $=id=>document.getElementById(id);
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const datasets={
 entities:['July entities','Entity instances from the historical machine extraction. Canonical IDs group instances; those merges are not independently validated.'],
 relationships:['July relationships','Actual historical source → predicate → target records. Open a row to inspect both endpoint mentions, its CMOC and the prior machine critique.'],
 cmocs:['July configurations','Historical conditional explanations. A CMOC count is not a count of independently supported causal mechanisms.'],
 findings:['September findings','Paper-level findings, including findings that failed the machine gate. A finding is not yet a cross-paper programme theory.'],
 graph_nodes:['September graph nodes','Finding, C/resource/response/O and evidence nodes. Component nodes are attributed descriptions, not a new canonical entity inventory.'],
 graph_edges:['September graph edges','has_* and cites encode attribution. lexical_retrieval_candidate encodes word overlap, not support, agreement or causation.'],
 theories:['System conclusions','Actual generated cross-paper explanations, with finding IDs, rival explanations and unresolved evidence gaps. Empty means this stage has not produced a result.'],
 comparisons:['Richmond comparison','Actual AI-assisted configuration comparisons. These do not establish human validation. The 18 reference branches are a project operationalization, not the 47/40 concept/relation evaluation.']};
let selected='entities';
const cmocs=new Map(data.cmocs.map(x=>[x.id,x]));const entities=new Map(data.entities.map(x=>[x.id,x]));const nodes=new Map(data.graph_nodes.map(x=>[x.id,x]));
$('cards').innerHTML=[['July entity instances',data.entities.length],['July relation records',data.relationships.length],['September findings',data.findings.length],['New theory statements',data.theories.length]].map(([t,n])=>`<div class="card"><strong>${n}</strong>${esc(t)}</div>`).join('');
$('state').textContent=`Run ${data.run}. ${data.audited_papers_observed}/28 saved paper audits. New synthesis: ${data.theories.length?'available':'not generated'}. New comparison: ${data.comparisons.length?'available':'not generated'}. Comparison rows with evidence-link warnings: ${data.comparison_reference_issues.length}. Human validation is not established by this inspection. Snapshot: ${data.generated_at}.`;
$('tabs').innerHTML=Object.entries(datasets).map(([key,v])=>`<button data-tab="${key}" aria-pressed="${key===selected}">${v[0]} (${data[key].length})</button>`).join('');
function title(row){return row.title||row.resource||row.narrative_statement||row.label||[row.source,row.type||row.description,row.target].filter(Boolean).join(' → ')||row.id;}
function recordId(row,index){return row.id||row.finding_id||row.theory_id||row.claim_id||`edge-${index+1}`;}
function fields(row,exclude=[]){return '<dl>'+Object.entries(row).filter(([k])=>!exclude.includes(k)).map(([k,v])=>`<dt>${esc(k.replaceAll('_',' '))}</dt><dd>${esc(typeof v==='object'?JSON.stringify(v,null,2):v)}</dd>`).join('')+'</dl>';}
function sourceLink(paper,page){const p=data.source_links[paper];return p?`<p><strong>${esc(paper)}</strong>: ${esc(p.title)} (${esc(p.availability)}) ${p.url?`<a href="${esc(p.url+(page?'#page='+page:''))}" target="_blank" rel="noopener">Open original PDF${page?' p. '+page:''}</a>`:' — full PDF unavailable'}</p>`:'';}
function legacyEvidence(entity){return `<h3>${esc(entity.title)} (${esc(entity.type)})</h3><code>${esc(entity.id)}</code><blockquote>${esc(entity.description)}</blockquote><p>Historical quote-location flag: ${esc(entity.quote_resolved)}. This display does not independently verify entailment.</p>`;}
function diagram(edges,lookup){
 const ids=[...new Set(edges.flatMap(x=>[x.source,x.target]))];if(!ids.length)return '';
 const width=700,height=Math.max(210,ids.length*72),positions=new Map(ids.map((id,i)=>[id,{x:i%2?510:180,y:45+i*65}]));
 let svg=`<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Saved graph neighborhood"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#62808d"/></marker></defs>`;
 edges.forEach(edge=>{const a=positions.get(edge.source),b=positions.get(edge.target);svg+=`<line x1="${a.x}" y1="${a.y+12}" x2="${b.x}" y2="${b.y-12}" stroke="#62808d" marker-end="url(#arrow)"/><text x="${(a.x+b.x)/2+8}" y="${(a.y+b.y)/2}">${esc(edge.type||edge.description)}</text>`;});
 ids.forEach(id=>{const p=positions.get(id),label=lookup(id)||id;svg+=`<rect x="${p.x-155}" y="${p.y-16}" width="310" height="32" rx="6" fill="#e0edf1"/><text x="${p.x}" y="${p.y+4}" text-anchor="middle"><title>${esc(label)}</title>${esc(label.length>42?label.slice(0,39)+'…':label)}</text>`;});return svg+'</svg>';
}
function show(index){const row=data[selected][index];if(!row)return;history.replaceState(null,'','#'+selected+'/'+encodeURIComponent(recordId(row,index)));let body=`<h2>${esc(recordId(row,index))}</h2>`;
 if(selected==='entities'||selected==='relationships'||selected==='cmocs'){
  const cmoc=cmocs.get(row.cmoc_id||row.id);const edges=data.relationships.filter(r=>r.cmoc_id===(row.cmoc_id||row.id));
  body+=sourceLink(row.study_id)+diagram(edges,id=>data.entities.find(x=>x.canonical_id===id&&x.cmoc_id===(row.cmoc_id||row.id))?.title);
  body+=fields(row,['description','text_unit_ids']);
  if(selected==='entities')body+=legacyEvidence(row);
  if(selected==='relationships'){body+=`<h3>Predicate: ${esc(row.description)}</h3>`;for(const id of row.text_unit_ids||[])body+=entities.has(id)?legacyEvidence(entities.get(id)):`<p>Unresolved entity reference: ${esc(id)}</p>`;}
  if(cmoc)body+=`<h3>Configuration and original machine critique</h3><p>${esc(cmoc.narrative_statement)}</p><blockquote>${esc(cmoc.verifier_notes)}</blockquote><p>These are historical machine judgments, not human validation.</p>`;
 }else if(selected==='findings'){
  body+=sourceLink(row.paper_id)+fields(row,['evidence','critic']);
  body+=`<h3>Machine audit</h3>${fields(row.critic)}<h3>Source evidence</h3>`;
  row.evidence.forEach(ev=>body+=`<p><strong>${esc(ev.role)}</strong>: page ${ev.page}; ${ev.located?'located text':'UNLOCATED model quotation'}; offsets ${esc(ev.start)}:${esc(ev.end)}</p><blockquote>${esc(ev.source_span||ev.quote)}</blockquote>${sourceLink(row.paper_id,ev.page)}`);
 }else if(selected==='theories'||selected==='comparisons'){
  if(selected==='comparisons'){
   const issue=data.comparison_reference_issues.find(x=>x.claim_id===row.claim_id);
   if(issue)body+=`<div class="notice"><strong>Evidence-link warning</strong><p>${esc(issue.issue)}</p><p>${esc(issue.unlinked_finding_ids.join(', '))}</p></div>`;
   const ref=data.reference_claims.find(x=>x.claim_id===row.claim_id);
   if(ref)body+=`<h3>Richmond reference (awaiting ratification)</h3>${fields(ref)}`;
   body+=`<h3>AI comparison verdict: ${esc(row.verdict)}</h3>`;
   for(const id of row.theory_ids||[])body+=`<p><a href="#theories/${encodeURIComponent(id)}">Open system conclusion ${esc(id)}</a></p>`;
  }
  body+=fields(row);
  for(const id of row.finding_ids||[])body+=`<p><a href="#findings/${encodeURIComponent(id)}">Inspect evidence ${esc(id)}</a></p>`;
 }else{
  const edges=selected==='graph_edges'?[row]:data.graph_edges.filter(edge=>edge.type!=='lexical_retrieval_candidate'&&(edge.source===row.id||edge.target===row.id));
  body+=diagram(edges,id=>nodes.get(id)?.label||id)+fields(row);
  if(selected==='graph_edges')for(const id of [row.source,row.target])body+=`<h3>Endpoint ${esc(id)}</h3>${fields(nodes.get(id)||{})}`;
  const fid=(row.id||row.source||'').split(':')[0];const f=data.findings.find(x=>x.finding_id===fid);
  if(f)body+=`<button id="open-finding">Open originating finding ${esc(fid)}</button>`;
 }
 $('detail').innerHTML=body;const go=$('open-finding');if(go)go.onclick=()=>{const fid=(row.id||row.source).split(':')[0];switchDataset('findings');show(data.findings.findIndex(x=>x.finding_id===fid));};
}
function render(){const query=$('search').value.toLowerCase();const rows=data[selected].map((row,index)=>({row,index})).filter(({row})=>JSON.stringify(row).toLowerCase().includes(query));$('count').textContent=`${rows.length} of ${data[selected].length} records shown`;
 $('records').innerHTML=rows.map(({row,index})=>`<button class="record" data-index="${index}"><small>${esc(recordId(row,index))} · ${esc(row.study_id||row.paper_id||row.type||'')}</small>${esc(title(row))}</button>`).join('');
 $('records').querySelectorAll('button').forEach(button=>button.onclick=()=>show(Number(button.dataset.index)));
}
function switchDataset(key){selected=key;$('search').value='';$('meaning').textContent=datasets[key][1];$('download').href=key+'.csv';$('download').hidden=!data[key].length;document.querySelectorAll('[data-tab]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.tab===key)));render();$('detail').innerHTML='<h2>Select a record</h2><p>Click a row to inspect its actual fields and evidence.</p>';}
function followHash(){const [key,...parts]=location.hash.slice(1).split('/');if(!datasets[key])return;let id;try{id=decodeURIComponent(parts.join('/'));}catch{return;}switchDataset(key);const index=data[key].findIndex((row,i)=>recordId(row,i)===id);if(index>=0)show(index);}
$('tabs').querySelectorAll('button').forEach(button=>button.onclick=()=>switchDataset(button.dataset.tab));$('search').oninput=render;switchDataset('entities');
window.addEventListener('hashchange',followHash);followHash();
</script></body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--legacy-dir", type=Path, default=Path("outputs/lkg"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    from res_pipeline.core.config import PROJECT_ROOT

    summary = export_inspection(args.run_dir, args.legacy_dir, args.output_dir, PROJECT_ROOT)
    print(
        json.dumps(
            {key: value for key, value in summary.items() if key != "input_sha256"}, indent=2
        )
    )


if __name__ == "__main__":
    main()
