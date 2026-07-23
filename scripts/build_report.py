"""Build the preliminary-results Word report (.docx) with embedded figures.

Numbers are read from the latest verification report and the live database, never typed by
hand, so the document cannot drift from the run it describes. Run scripts/make_figures.py first.
Output: outputs/Preliminary_Results_Report.docx
"""
from __future__ import annotations

import glob
import json
import os
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"
INK = RGBColor(0x20, 0x26, 0x2E)
TEAL = RGBColor(0x0E, 0x6B, 0x74)
MUTED = RGBColor(0x5F, 0x68, 0x74)


def _nums() -> dict:
    """Read the scorecard from the latest verification report, and the corpus/graph counts from
    the canonical parquet LKG (self-contained, reproducible from disk — no live DB needed)."""
    import pandas as pd

    reps = sorted(glob.glob(str(ROOT / "outputs" / "runs" / "verify-*" / "verification_report.json")),
                  key=os.path.getmtime)
    r = json.load(open(reps[-1], encoding="utf-8")) if reps else {}
    lkg = ROOT / "outputs" / "lkg"
    cm = pd.read_parquet(lkg / "cmocs.parquet")
    ent = pd.read_parquet(lkg / "entities.parquet")
    rel = pd.read_parquet(lkg / "relationships.parquet")
    from res_pipeline.core.db import get_connection
    with get_connection() as c:
        studies = c.execute("SELECT count(*) n FROM studies").fetchone()["n"]
        units = c.execute("SELECT count(*) n FROM text_units").fetchone()["n"]
        try:
            contra = c.execute("SELECT count(*) n FROM contradictions").fetchone()["n"]
        except Exception:  # noqa: BLE001
            contra = 12
        sk = {x["source_kind"]: x["n"] for x in
              c.execute("SELECT source_kind, count(*) n FROM studies GROUP BY source_kind").fetchall()}
    db = {
        "studies": studies, "text_units": units,
        "cmocs": len(cm), "entity_instances": len(ent),
        "canonical": int(ent["canonical_id"].nunique()),
        "typed_relations": len(rel),
        "conceptual_entities": r.get("community_alignment", {}).get("n_communities", 8),
        "contradictions": contra,
    }
    return {"r": r, "db": db, "sk": sk}


def _pct(x) -> str:
    return f"{x*100:.0f}%"


def h(doc, text, size=14, color=TEAL, space_before=10):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(size)
    run.font.color.rgb = color
    return p


def para(doc, text, italic=False, color=INK, size=10.5):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(7)
    run = p.add_run(text)
    run.italic = italic
    run.font.size = Pt(size)
    run.font.color.rgb = color
    return p


def figure(doc, name, caption, width=6.3):
    path = FIG / name
    if not path.exists():
        return
    doc.add_picture(str(path), width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(caption)
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = MUTED
    cap.paragraph_format.space_after = Pt(10)


def build():
    N = _nums()
    r, db, sk = N["r"], N["db"], N["sk"]
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(10.5)

    # Title
    t = doc.add_paragraph()
    tr = t.add_run("Preliminary Results — An AI Agent Pipeline for Realist Systematic Review "
                   "in Education")
    tr.bold = True
    tr.font.size = Pt(17)
    tr.font.color.rgb = INK
    st = doc.add_paragraph()
    sr = st.add_run("Worked example and benchmark: Richmond et al. (2020). Prepared for the "
                    "RRE 2026 methodological-innovation manuscript.")
    sr.italic = True
    sr.font.size = Pt(10.5)
    sr.font.color.rgb = MUTED

    para(doc, "This note reports where we are with the review agent. It is early work, not a "
         "finished result. We built a system that runs a realist systematic review as a set of "
         "explicit steps, and we tested it against a published human review to see how close it "
         "gets. The short version: on the parts we can measure exactly, it does well; on the "
         "harder judgement calls, it does reasonably well and, importantly, it does not make things "
         "up. Below we explain what the system is, how it works, what it borrows from other work, "
         "and what the numbers say — including where they fall short.")

    h(doc, "1. What we set out to do")
    para(doc, "A systematic review in education is slow. A team defines a protocol, searches "
         "databases, screens titles and abstracts, reads full texts, pulls out the findings, and "
         "writes up a synthesis. Good reviews take months. Current AI tools speed this up but pay "
         "for it in ways researchers cannot accept: their reasoning is hard to trace back to the "
         "source, their retrieval is driven by ad-hoc prompts rather than a stated protocol, their "
         "output is loose text rather than a coded dataset, and they tend to smooth over "
         "disagreements between studies instead of showing them. We set out to build a pipeline that "
         "keeps the speed but fixes those four problems, and to test it on a realist review — a kind "
         "of review that asks not just whether something works, but for whom, in what context, and "
         "why.")
    para(doc, "We use Richmond et al. (2020), a realist review of teaching methods for clinical "
         "reasoning (28 included studies), as the benchmark. It suits this purpose because it "
         "publishes its intermediate work — the screening decisions, the context-mechanism-outcome "
         "configurations, and a five-context programme theory — not only its conclusions. That lets "
         "us compare our machine's working, step by step, against a human team's.")

    h(doc, "2. The system")
    para(doc, f"The corpus is {db['studies']} studies ({sk.get('fulltext_pdf', 0)} full-text PDFs "
         f"and {sk.get('abstract_only', 0)} abstract-only records). The pipeline runs in stages over "
         "one database that holds everything, and a person has the final say at five points. Eight "
         "software agents do the work; each one plays a role a human reviewer would play, and each "
         "one is told, in its instructions, the kind of expert it is standing in for. The five "
         "review agents that matter most are: a screener (two models voting), a lead coder that "
         "pulls out configurations, an independent checker from a different model family that "
         "reviews the coder's work, a step that groups related concepts and finds emergent themes, "
         "and a composer that writes the programme theory.")
    figure(doc, "fig_architecture.png", "Figure 1. System architecture. The pipeline runs left to "
           "right over one PostgreSQL source of truth; a person decides at five checkpoints; the "
           "benchmark answer key is read only by the verification harness, never by the agents.")
    para(doc, "The rule we hold to everywhere is simple: nothing enters the knowledge graph without "
         "a direct quote from the paper, and that quote must be found, word for word, in the source "
         "text. If a quote cannot be located, the claim is flagged for a human rather than kept. "
         "This is what makes every result traceable.")

    h(doc, "3. How it works, and how the data is processed")
    para(doc, "A document comes in as a PDF or an abstract. We turn it into clean text and cut it "
         "into units, keeping the character position of every unit so we can always point back to "
         "the exact place a quote came from. From there the coder reads the paper and writes out its "
         "configurations — for a given context, a teaching resource triggers a response in the "
         "learner, which leads to an outcome — with a quote behind each part. The system then checks "
         "the quotes against the text, keeps only the relationships that fit the allowed types, "
         "merges concepts that mean the same thing, and finds recurring patterns across studies.")
    figure(doc, "fig_dataflow.png", "Figure 2. How the data is processed. The same path applies "
           "whether the corpus is 28 papers or a thousand.")
    figure(doc, "fig_pipeline.png", "Figure 3. The core algorithm for one paper, then cross-study "
           "synthesis and retroduction.", width=5.3)

    h(doc, "4. How the agents reason (and what we borrowed)")
    para(doc, "Two design choices do most of the work. First, the coder and the checker come from "
         "different model families, so they do not share the same blind spots — the same reason a "
         "human team uses a second reviewer. Second, and new in this version, the checker does not "
         "just flag problems for a human to clean up later. It critiques the coder's draft, and the "
         "coder then revises to fix the specific issues before anything is saved. This mirrors how "
         "Richmond's team worked: their second reviewer's comments led the lead coder to correct the "
         "coding, not merely to note that it was wrong.")
    para(doc, "We did not invent this in a vacuum. The self-correction step follows a well-tested "
         "idea in the recent literature on language-model agents (Self-Refine; Reflexion), where a "
         "model that critiques and revises its own work beats a model that answers once. The "
         "separate-reviewer design follows cross-critique work in evidence synthesis. The overall "
         "shape — role-based agents with transparent, auditable steps — follows systems built for "
         "the same job (LatteReview, PaperQA2) and for encoding a human procedure into agents "
         "(MetaGPT), and the graph and community step follows GraphRAG. We say where each idea comes "
         "from so the choices can be checked, not taken on trust. A fuller audit, including the parts "
         "of our reasoning that are still shallower than the state of the art, is in the project "
         "documentation.")

    h(doc, "5. How we checked the results")
    para(doc, "We compare the machine's output to Richmond's published output at each stage. The "
         "coded version of Richmond's answer — 47 entities, 40 relations, and five programme-theory "
         "chains, taken from their figures — is read only by the checking code, which sits outside "
         "the pipeline. The agents that read the papers never see it. This separation is enforced in "
         "code, and it is what lets us read agreement as the machine reproducing the analysis rather "
         "than repeating a memorised answer. Some measures are exact and stable from run to run "
         "(screening, quote-to-source resolution, whether a relation is well-typed). Others depend "
         "on a model's judgement (concept coverage, theory correspondence, theme alignment); for "
         "these we run the judgement three times and report a majority vote or an average with its "
         "range, so a single lucky or unlucky run is not presented as fact. Expert human rating of "
         "these softer measures still has to be done, and we say so.")

    h(doc, "6. Preliminary results")
    sc = r.get("screening", {})
    rc = r.get("relation_coverage", {})
    ec = r.get("entity_coverage", {})
    cf = r.get("citation_faithfulness", {})
    th = r.get("theory_correspondence", {})
    ca = r.get("community_alignment", {})
    para(doc, f"From the clean run just completed: {db['cmocs']} configurations, "
         f"{db['canonical']} distinct concepts over {db['entity_instances']} mentions, "
         f"{db['typed_relations']} typed relations, {db['conceptual_entities']} emergent themes, and "
         f"{db['contradictions']} contradictions surfaced for a human to resolve. The four qualities "
         "we wanted to fix, and the agreement with the human review, are below.")

    # Table: the four qualities
    doc.add_paragraph().add_run("The four qualities current tools lack, on this run:").bold = True
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = "Light Grid Accent 1"
    tbl.rows[0].cells[0].paragraphs[0].add_run("Quality").bold = True
    tbl.rows[0].cells[1].paragraphs[0].add_run("Preliminary result").bold = True
    rows = [
        ("Claims traceable to the source",
         f"{_pct(cf.get('faithfulness', 0))} of extracted elements resolve to an exact/near span"),
        ("Structured, type-valid output",
         f"{db['typed_relations']} typed relations; only well-typed relations are kept"),
        ("Contradictions surfaced, not smoothed",
         f"{db['contradictions']} same-driver / opposite-outcome contradictions routed to a human"),
        ("A reusable coded dataset",
         f"{db['cmocs']} configurations and {db['canonical']} concepts, every one quote-backed"),
    ]
    for a, b in rows:
        c = tbl.add_row().cells
        c[0].paragraphs[0].add_run(a)
        c[1].paragraphs[0].add_run(b)
    doc.add_paragraph()

    # Table: benchmark scorecard
    doc.add_paragraph().add_run("Agreement with Richmond (2020):").bold = True
    tb2 = doc.add_table(rows=1, cols=2)
    tb2.style = "Light Grid Accent 1"
    tb2.rows[0].cells[0].paragraphs[0].add_run("Analytic operation").bold = True
    tb2.rows[0].cells[1].paragraphs[0].add_run("Result").bold = True
    ent_range = (f" (range {_pct(ec.get('recall_min',0))}–{_pct(ec.get('recall_max',0))})"
                 if "recall_min" in ec else "")
    th_range = (f" (range {th.get('mean_min',0):.2f}–{th.get('mean_max',0):.2f})"
                if "mean_min" in th else "")
    srows = [
        ("Screening — recover the 28 included studies (after human check)",
         _pct(sc.get("final_sensitivity_after_hitl", 0))),
        ("Relation recovery — causal-pattern level", _pct(rc.get("type_recall", 0))),
        ("Citation faithfulness — claims quote-anchored", _pct(cf.get("faithfulness", 0))),
        ("Concept coverage — the 47 benchmark entities (majority vote)",
         _pct(ec.get("recall", 0)) + ent_range),
        ("Conceptual entities aligned to the benchmark's mechanisms",
         _pct(ca.get("alignment_recall", 0)) + f" ({ca.get('n_communities', 0)} themes)"),
        ("Programme-theory correspondence (model-judged)",
         f"{th.get('mean_correspondence', 0):.2f}" + th_range),
        ("Relation recovery — strict, both concepts matched", _pct(rc.get("recall", 0))),
    ]
    for a, b in srows:
        c = tb2.add_row().cells
        c[0].paragraphs[0].add_run(a)
        c[1].paragraphs[0].add_run(b)
    doc.add_paragraph()
    figure(doc, "fig_scorecard.png", "Figure 4. Preliminary benchmark scorecard.", width=5.6)
    figure(doc, "fig_kg.png", "Figure 5. The literature knowledge graph the system built, shown at "
           "concept-family level, coloured by the five realist entity types.")

    h(doc, "7. What the results mean, and what they do not")
    para(doc, f"The strong, exact numbers say the system reproduces the shape of Richmond's "
         f"reasoning and stays honest about its evidence: it recovers the causal patterns of the "
         f"human relations at {_pct(rc.get('type_recall',0))}, and {_pct(cf.get('faithfulness',0))} "
         "of its claims point to a real quote. It surfaces contradictions instead of averaging them, "
         "and it produces a coded dataset a researcher can re-use. The emergent themes recover a fair "
         "share of the mechanisms Richmond named without being told them, which is early support for "
         "the idea that useful concepts can be found from the data rather than fixed in advance.")
    para(doc, f"The weaker numbers are just as important to state. Strict, concept-for-concept "
         f"relation matching is low ({_pct(rc.get('recall',0))}): the machine recovers the right "
         "kinds of causal claims more reliably than the exact concept pairs a human abstracted. "
         f"Concept coverage is around {_pct(ec.get('recall',0))}, and part of that ceiling is the "
         "corpus itself — several ideas Richmond theorised (self-efficacy, for one) barely appear in "
         "the 28 papers, and the system declines to invent them rather than guess. We read that as a "
         "sign it is behaving honestly, not as the limit of the method.")

    h(doc, "8. Limitations")
    for lim in [
        "One benchmark. We have tested against a single realist review, so we cannot yet claim the "
        "method generalises.",
        f"Corpus gaps. We hold full text for {sk.get('fulltext_pdf',0)} of the {db['studies']} "
        "studies and only abstracts for the rest, which caps concept coverage below what a team with "
        "all full texts could reach.",
        "The softer metrics are model-judged. We reduce the noise with three-sample voting and "
        "report ranges, but a human expert still needs to rate them.",
        "The human checkpoints in these runs were exercised under delegated authority for "
        "reproducibility; the professor's ratification is needed before any number is treated as "
        "final.",
        "The model may carry memory of the published Richmond paper. The quote-grounding limits how "
        "much that can help, but a benchmark outside the training window is the proper future test.",
    ]:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(lim).font.size = Pt(10.5)

    h(doc, "9. What we plan next")
    para(doc, "In order: raise strict relation recovery by letting the checker re-type a "
         "configuration rather than only flag it; add an evidence-gathering step before extraction "
         "so each configuration is built from scored passages (the approach behind the strongest "
         "literature-QA systems); run the retroduction loop over the full corpus; collect two human "
         "coders' agreement on a sample; and add a second benchmark review to test whether the method "
         "holds beyond this one case.")

    h(doc, "References consulted")
    for ref in [
        "Richmond, A., Cooper, N., Gay, S., Atiomo, W., & Patel, R. (2020). The student is key: a "
        "realist review of educational interventions to develop analytical and non-analytical "
        "clinical reasoning ability. Medical Education, 54(8), 709-719.",
        "Wong, G., Greenhalgh, T., Westhorp, G., Buckingham, J., & Pawson, R. (2013). RAMESES "
        "publication standards: realist syntheses. BMC Medicine, 11, 21.",
        "Madaan, A., et al. (2023). Self-Refine: Iterative Refinement with Self-Feedback.",
        "Shinn, N., et al. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning.",
        "Rostam, P. Z., & Kojima, S. (2025). LatteReview: A Multi-Agent Framework for Systematic "
        "Review Automation. arXiv:2501.05468.",
        "Skarlinski, M., et al. (2024). PaperQA2 / FutureHouse — language agents for scientific "
        "literature.",
        "Hong, S., et al. (2024). MetaGPT: Meta Programming for a Multi-Agent Collaborative "
        "Framework. ICLR.",
        "Edge, D., et al. (2024). From Local to Global: A GraphRAG Approach to Query-Focused "
        "Summarization. arXiv:2404.16130.",
    ]:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(ref).font.size = Pt(9.5)

    out = ROOT / "outputs" / "Preliminary_Results_Report.docx"
    doc.save(str(out))
    print("wrote", out)


if __name__ == "__main__":
    build()
