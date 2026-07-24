"""Build the Richmond content-correspondence report.

This is the deliverable that verifies the system the way a realist review is
actually verified: NOT a self-assigned score, but a line-by-line correspondence
between the analytic content Richmond et al. (2020) published (contexts,
interventions, mechanisms, outcomes, causal links, and programme-theory chains,
each with its page location in the paper) and the content this system produced
(concepts, studies, verbatim quotes). A reader can hold Richmond's paper open and
check every row.

Numbers appear only as an honest tally of that correspondence at the end; every
tallied item is traceable to a specific Richmond location and a specific extracted
quote. LLM-judged matches are labelled as such and flagged for human ratification.

Inputs:
  * gold/richmond_gold.json            — the standard derived from Richmond's paper
  * outputs/runs/verify-*/verification_report.json — the per-item match decisions
  * PostgreSQL                         — to enrich a matched concept id with its
                                         actual label, a representative quote, and
                                         the studies it came from
Output:
  * outputs/Richmond_Correspondence.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from res_pipeline.core.config import GOLD_DIR, OUTPUTS_DIR  # noqa: E402
from res_pipeline.core.db import get_connection  # noqa: E402

_CATS = [
    ("Context", "Contexts — the student and setting conditions Richmond identified"),
    ("Intervention", "Interventions — the educational resources/activities"),
    ("Mechanism_Resource", "Mechanisms (Resource) — what the intervention offers"),
    ("Mechanism_Response", "Mechanisms (Response) — how students reason/react"),
    ("Outcome", "Outcomes — the reasoning/learning results"),
]


def _latest_verification() -> dict:
    runs = sorted((OUTPUTS_DIR / "runs").glob("verify-*/verification_report.json"),
                  key=lambda p: p.stat().st_mtime, reverse=True)
    if not runs:
        raise SystemExit("No verification_report.json found — run `res verify` first.")
    return json.loads(runs[0].read_text(encoding="utf-8")), runs[0]


def _enrich_concepts(concept_ids: set[str]) -> dict[str, dict]:
    """Look up each matched canonical concept id -> label, quote, studies."""
    if not concept_ids:
        return {}
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT canonical_id,
                   (array_agg(DISTINCT label))[1] AS label,
                   (array_agg(verbatim_quote ORDER BY confidence DESC NULLS LAST))[1] AS quote,
                   array_agg(DISTINCT study_id) AS studies
            FROM entity_instances
            WHERE canonical_id = ANY(%s)
            GROUP BY canonical_id
            """,
            (list(concept_ids),),
        ).fetchall()
    return {r["canonical_id"]: {"label": r["label"], "quote": r["quote"],
                                "studies": r["studies"]} for r in rows}


def _fmt_match(code: str, per_entity: dict, enrich: dict) -> str:
    info = per_entity.get(code, {})
    if not info.get("matched"):
        return "**not recovered**"
    cid = info.get("concept", "")
    # When our extractor filed the same construct under a different realist role than
    # Richmond, flag it honestly rather than silently counting a clean match.
    role_note = ""
    if info.get("cross_type") or (info.get("concept") and info.get("type_agrees") is False):
        role_note = " ⟂ *(role differs from Richmond)*"
    e = enrich.get(cid)
    if not e:
        return f"recovered (concept `{cid}`){role_note}"
    studies = ", ".join(e["studies"][:4]) + ("…" if len(e["studies"]) > 4 else "")
    quote = (e["quote"] or "").strip().replace("\n", " ")
    if len(quote) > 160:
        quote = quote[:160] + "…"
    q = f' — quote: *"{quote}"*' if quote else ""
    return f'our concept **{e["label"]}** (studies {studies}){q}{role_note}'


def build() -> Path:
    gold = json.loads((GOLD_DIR / "richmond_gold.json").read_text(encoding="utf-8"))
    report, report_path = _latest_verification()
    ent_cov = report.get("entity_coverage", {})
    per_entity = ent_cov.get("per_entity", {})
    rel_cov = report.get("relation_coverage", {})
    theory = report.get("theory_correspondence", {})

    matched_concepts = {info.get("concept") for info in per_entity.values()
                        if info.get("matched") and info.get("concept")}
    enrich = _enrich_concepts(matched_concepts)

    L: list[str] = []
    L.append("# Content correspondence: this system vs. Richmond et al. (2020)")
    L.append("")
    L.append(f"> Source of the standard: **{gold['source'].strip()}**  ")
    L.append("> The reference below is the analytic content Richmond's human team "
             "published — every item cites its location in their paper. Each row shows "
             "whether this system independently recovered that content, and from which "
             "study and verbatim quote, so the correspondence can be checked directly "
             "against the paper. Semantic matches are LLM-judged and flagged for human "
             "ratification; they are not a self-assigned grade.")
    L.append("")
    L.append(f"_Verification data: `{report_path.name}` — entity matcher sampled "
             f"{ent_cov.get('samples','?')}× and majority-voted._")
    L.append("")

    # ---- Entities, per realist category ----
    ents = gold["entities"]
    for cat, heading in _CATS:
        codes = [c for c, s in ents.items() if s["category"] == cat]
        if not codes:
            continue
        L.append(f"## {heading}")
        L.append("")
        L.append("| Richmond (code · location) | Richmond describes | This system recovered |")
        L.append("|---|---|---|")
        for c in codes:
            spec = ents[c]
            loc = spec.get("location", "")
            label = spec["label"].replace("\n", " ")
            L.append(f"| `{c}` · {loc} | {label} | {_fmt_match(c, per_entity, enrich)} |")
        L.append("")

    # ---- Causal relationships ----
    L.append("## Causal relationships Richmond asserts")
    L.append("")
    recovered = set(rel_cov.get("recovered_ids", []))
    anchored = set(rel_cov.get("anchored_ids", []))
    gr = rel_cov.get("gold_relations", "?")
    L.append("Three fairness levels, all reported (a realist review cares most about the "
             "**pattern**, not exact concept-string identity):")
    L.append("")
    L.append(f"- **Type-level pattern** (e.g. *Context CONSTRAINS Outcome* exists in our graph): "
             f"**{rel_cov.get('type_recovered','?')}/{gr}**")
    L.append(f"- **Anchored** (same predicate, one endpoint the exact matched concept, other of "
             f"the right role): **{rel_cov.get('anchored_recovered','?')}/{gr}**")
    L.append(f"- **Concept-exact** (both endpoints the exact matched concepts — deliberately "
             f"harsh): **{rel_cov.get('recovered','?')}/{gr}**")
    L.append("")
    L.append("| Richmond relation | Subject → predicate → object | Concept-exact | Anchored |")
    L.append("|---|---|---|---|")
    for rel in gold["relationships"]:
        s_lab = ents.get(rel["subject_code"], {}).get("label", rel["subject_code"])[:40]
        o_lab = ents.get(rel["object_code"], {}).get("label", rel["object_code"])[:40]
        exact = "✅" if rel["id"] in recovered else "—"
        anch = "✅" if rel["id"] in anchored else "—"
        L.append(f"| `{rel['id']}` | {s_lab} —{rel['predicate']}→ {o_lab} | {exact} | {anch} |")
    L.append("")

    # ---- Programme-theory chains ----
    L.append("## Programme-theory chains (the heart of the realist review)")
    L.append("")
    L.append("Richmond's five context-specific C→M→O chains, and how closely this "
             "system's programme theory corresponds to each (model-judged, human rating "
             "required before publication).")
    L.append("")
    per_chain = theory.get("per_chain", {})
    L.append("| Chain | Richmond context | Canonical chain | Correspondence | Assessor note |")
    L.append("|---|---|---|---|---|")
    for pid, spec in gold["programme_theory_statements"].items():
        sc = per_chain.get(pid, {})
        corr = sc.get("correspondence", "—")
        note = (sc.get("rationale", "") or "").replace("\n", " ")
        if len(note) > 140:
            note = note[:140] + "…"
        L.append(f"| `{pid}` | {spec.get('context_label','')} | "
                 f"`{spec.get('canonical_chain','')}` | {corr} | {note} |")
    L.append("")

    # ---- Honest tally ----
    L.append("## Honest tally (a summary OF the correspondence above, not a grade)")
    L.append("")
    L.append(f"- Contexts/interventions/mechanisms/outcomes Richmond describes: "
             f"**{ent_cov.get('matched','?')} of {ent_cov.get('gold_entities','?')}** "
             f"independently recovered "
             f"(of which {ent_cov.get('matched_within_type','?')} with the same realist role "
             f"as Richmond, {ent_cov.get('matched_cross_type','?')} the same construct under a "
             f"different role).")
    L.append(f"- Causal relationships: type-level pattern "
             f"**{rel_cov.get('type_recovered','?')}/{rel_cov.get('gold_relations','?')}**, "
             f"anchored **{rel_cov.get('anchored_recovered','?')}/"
             f"{rel_cov.get('gold_relations','?')}**, "
             f"concept-exact **{rel_cov.get('recovered','?')}/"
             f"{rel_cov.get('gold_relations','?')}**.")
    L.append(f"- Programme-theory correspondence (mean, model-judged): "
             f"**{theory.get('mean_correspondence','?')}** "
             f"(range {theory.get('mean_min','?')}–{theory.get('mean_max','?')}).")
    ff = report.get("citation_faithfulness", {})
    L.append(f"- Citation faithfulness (quotes that resolve exactly to source text): "
             f"**{ff.get('quotes_resolved','?')}/{ff.get('entities','?')}**.")
    L.append("")
    L.append("_Every recovered item above is traceable to a Richmond page location and an "
             "extracted verbatim quote; every semantic match is LLM-judged and awaits human "
             "ratification. This report is the verification — the numbers only summarise it._")
    L.append("")

    out = OUTPUTS_DIR / "Richmond_Correspondence.md"
    out.write_text("\n".join(L), encoding="utf-8")
    return out


if __name__ == "__main__":
    path = build()
    print(f"wrote {path}")
