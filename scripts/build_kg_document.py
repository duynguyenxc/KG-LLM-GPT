"""Build the knowledge-graph reference document (HTML) — the entities, relationships,
and GraphRAG big concepts the system produced, in a readable, submittable form.

Everything is pulled live from the database for the current run. Output:
outputs/Knowledge_Graph_Report.html  (convert to PDF separately).
"""
from __future__ import annotations

import html
from pathlib import Path

from res_pipeline.core.db import get_connection

ROOT = Path(__file__).resolve().parents[1]

TYPES = [
    ("Context", "t-ctx", "Pre-existing conditions of the learner, group, or setting."),
    ("Intervention", "t-int", "The educational methods and resources studied."),
    ("Mechanism_Resource", "t-mres", "What an intervention offers into the context."),
    ("Mechanism_Response", "t-mresp", "How learners cognitively or emotionally react."),
    ("Outcome", "t-out", "The reasoning and learning results."),
]

CSS = """
:root{--paper:#faf9f6;--ink:#1b2430;--muted:#5c6672;--line:#d9d5cc;--accent:#0f5b6b;
--accent2:#14788c;--red:#8a2b34;--chip:#eef1ee;--ctx:#9a6b18;--int:#0f6b74;--mres:#2f6bad;
--mresp:#7a4b93;--out:#2e7d52;}
@media (prefers-color-scheme:dark){:root{--paper:#14181e;--ink:#e7e6e1;--muted:#9aa2ad;
--line:#2c333c;--accent:#4bb6c9;--accent2:#5cc4d6;--red:#e0868f;--chip:#1e242c;}}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);
font-family:Georgia,Cambria,"Times New Roman",serif;line-height:1.6;font-size:16px}
.wrap{max-width:840px;margin:0 auto;padding:52px 28px 90px}
.kicker{font-family:system-ui,sans-serif;font-size:12px;letter-spacing:.14em;text-transform:uppercase;
color:var(--accent);font-weight:600;margin:0 0 10px}
h1{font-size:27px;margin:0 0 10px;font-weight:600;line-height:1.2}
.byline{font-family:system-ui,sans-serif;font-size:13px;color:var(--muted);margin:0 0 4px}
h2{font-size:20px;color:var(--accent);margin:40px 0 4px;font-weight:600;padding-bottom:6px;
border-bottom:1px solid var(--line)}
h2 .n{color:var(--muted);font-weight:400;margin-right:.5em}
h3{font-size:15px;margin:22px 0 2px;font-family:system-ui,sans-serif}
p{margin:10px 0}.muted{color:var(--muted)}
header.title{border-bottom:2px solid var(--accent);padding-bottom:18px;margin-bottom:6px}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:13.5px;font-family:system-ui,sans-serif}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
thead th{color:var(--accent);border-bottom:1.5px solid var(--accent);font-size:12px;text-transform:uppercase}
td .q{color:var(--muted);font-style:italic;font-family:Georgia,serif}
.tag{display:inline-block;font-family:system-ui,sans-serif;font-size:10px;font-weight:600;
padding:2px 7px;border-radius:10px;color:#fff}
.t-ctx{background:var(--ctx)}.t-int{background:var(--int)}.t-mres{background:var(--mres)}
.t-mresp{background:var(--mresp)}.t-out{background:var(--out)}
.bigcard{border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:0 8px 8px 0;
padding:12px 16px;margin:14px 0;background:var(--chip)}
.bigcard h3{margin:0 0 4px;font-size:15.5px;color:var(--ink)}
.bigcard .role{font-family:system-ui,sans-serif;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.bigcard .mem{font-family:system-ui,sans-serif;font-size:12px;color:var(--muted);margin-top:6px}
.statband{display:flex;flex-wrap:wrap;gap:12px;margin:16px 0}
.stat{flex:1 1 120px;border:1px solid var(--line);border-radius:9px;padding:10px 13px;background:var(--chip)}
.stat .v{font-family:system-ui,sans-serif;font-size:21px;font-weight:700;color:var(--accent)}
.stat .l{font-family:system-ui,sans-serif;font-size:11px;color:var(--muted);margin-top:2px}
.mono{font-family:ui-monospace,Consolas,monospace;font-size:12px}
.foot{margin-top:54px;padding-top:14px;border-top:1px solid var(--line);
font-family:system-ui,sans-serif;font-size:11.5px;color:var(--muted)}
@media print{body{background:#fff;color:#000;font-size:11pt}.wrap{max-width:none;padding:0}
.bigcard,table,tr{break-inside:avoid}h2{break-after:avoid}.stat{background:#f4f4f2}}
"""


def esc(s):
    return html.escape(str(s or ""))


def build():
    with get_connection() as c:
        bigs = c.execute(
            "SELECT community_label, realist_role, entity_type, definition, description, "
            "member_labels, member_count, study_ids FROM conceptual_entities "
            "ORDER BY member_count DESC"
        ).fetchall()
        concepts = {}
        for t, _, _ in TYPES:
            concepts[t] = c.execute(
                """SELECT (array_agg(DISTINCT label))[1] label,
                          (array_agg(verbatim_quote ORDER BY confidence DESC NULLS LAST))[1] quote,
                          count(DISTINCT study_id) ns
                   FROM entity_instances WHERE canonical_id IS NOT NULL AND entity_type=%s
                   GROUP BY canonical_id ORDER BY ns DESC, 1""", (t,)
            ).fetchall()
        rel_counts = c.execute(
            "SELECT predicate, count(*) n FROM typed_relations GROUP BY predicate ORDER BY 2 DESC"
        ).fetchall()
        rels = c.execute(
            """SELECT tr.predicate, se.label sl, se.entity_type st, oe.label ol, oe.entity_type ot
               FROM typed_relations tr
               JOIN entity_instances se ON se.entity_id=tr.subject_entity_id
               JOIN entity_instances oe ON oe.entity_id=tr.object_entity_id
               WHERE tr.constraint_valid ORDER BY tr.predicate LIMIT 45"""
        ).fetchall()
    n_concepts = sum(len(v) for v in concepts.values())
    n_rel = sum(r["n"] for r in rel_counts)
    tagmap = {t: cls for t, cls, _ in TYPES}

    L = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'>",
         "<meta name='viewport' content='width=device-width, initial-scale=1'>",
         "<title>Knowledge Graph — Entities, Relationships, Big Concepts</title>",
         f"<style>{CSS}</style></head><body><div class='wrap'>"]
    L.append("<header class='title'><p class='kicker'>Literature knowledge graph · companion to the "
             "progress report</p><h1>Entities, relationships, and big concepts</h1>"
             "<p class='byline'>The full structure the system extracted and the GraphRAG community "
             "detection produced, from the current run. Every entity is grounded in a verbatim quote "
             "from a source paper.</p></header>")
    L.append("<div class='statband'>"
             f"<div class='stat'><div class='v'>{n_concepts}</div><div class='l'>Canonical entities (concepts)</div></div>"
             f"<div class='stat'><div class='v'>{n_rel}</div><div class='l'>Typed causal relations</div></div>"
             f"<div class='stat'><div class='v'>{len(bigs)}</div><div class='l'>Big concepts (Leiden communities)</div></div>"
             "</div>")

    # ---- Big concepts (GraphRAG community reports) ----
    L.append("<h2><span class='n'>1</span>Big concepts (GraphRAG community reports)</h2>")
    L.append("<p class='muted'>Entities that recur together across studies are clustered by Leiden "
             "community detection; each cluster is summarised into one higher-level concept. This is "
             "the emergent, data-driven layer — not a predefined list.</p>")
    for b in bigs:
        role = esc(b["realist_role"] or b["entity_type"])
        cls = tagmap.get(b["entity_type"], "t-int")
        mem = ", ".join((b["member_labels"] or [])[:8])
        L.append(f"<div class='bigcard'><span class='tag {cls}'>{esc(b['entity_type'])}</span> "
                 f"<span class='role'>&nbsp;{esc(b['member_count'])} members · {len(b['study_ids'] or [])} studies</span>"
                 f"<h3>{esc(b['community_label'])}</h3>"
                 f"<p style='margin:4px 0'>{esc(b['description'] or b['definition'])}</p>"
                 f"<div class='mem'>Members include: {esc(mem)}</div></div>")

    # ---- Entities by type ----
    L.append("<h2><span class='n'>2</span>Entities, by realist type</h2>")
    L.append("<p class='muted'>All canonical concepts, with the number of studies each appears in and "
             "one representative source quote. Entities are the nodes of the knowledge graph.</p>")
    for t, cls, desc in TYPES:
        rows = concepts[t]
        L.append(f"<h3><span class='tag {cls}'>{esc(t.replace('_',' '))}</span> &nbsp;{len(rows)} concepts "
                 f"<span class='muted' style='font-weight:400'>— {esc(desc)}</span></h3>")
        L.append("<table><thead><tr><th>Concept</th><th>Studies</th><th>Representative quote</th></tr></thead><tbody>")
        for r in rows:
            q = (r["quote"] or "").strip().replace("\n", " ")
            if len(q) > 130:
                q = q[:130] + "…"
            L.append(f"<tr><td><strong>{esc(r['label'])}</strong></td><td>{r['ns']}</td>"
                     f"<td class='q'>{esc(q)}</td></tr>")
        L.append("</tbody></table>")

    # ---- Relationships ----
    L.append("<h2><span class='n'>3</span>Relationships</h2>")
    counts = " · ".join(f"{esc(r['predicate'])} {r['n']}" for r in rel_counts if r['predicate'] != 'UNTYPED_CANDIDATE')
    L.append(f"<p class='muted'>{n_rel} directed, typed causal links. Distribution: {counts}. "
             "A sample of the links follows; the full set is in the interactive console and the "
             "canonical data files.</p>")
    L.append("<table><thead><tr><th>Subject</th><th>Predicate</th><th>Object</th></tr></thead><tbody>")
    for r in rels:
        sc = tagmap.get(r["st"], "t-int")
        oc = tagmap.get(r["ot"], "t-int")
        L.append(f"<tr><td><span class='tag {sc}'>{esc(r['st'][:4])}</span> {esc(r['sl'])}</td>"
                 f"<td class='mono'>{esc(r['predicate'])}</td>"
                 f"<td><span class='tag {oc}'>{esc(r['ot'][:4])}</span> {esc(r['ol'])}</td></tr>")
    L.append("</tbody></table>")

    L.append("<p class='foot'>Generated live from the current run's database. Entities carry a verbatim "
             "quote resolved to a character span in the source; relations that violate the ontology's "
             "domain/range are demoted, not shown here. The full graph is interactive in the review "
             "console (Knowledge graph tab).</p>")
    L.append("</div></body></html>")

    out = ROOT / "outputs" / "Knowledge_Graph_Report.html"
    out.write_text("\n".join(L), encoding="utf-8")
    return out


if __name__ == "__main__":
    print("wrote", build())
