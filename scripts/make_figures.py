"""Generate the figures used in the preliminary-results report (PNG, 200 dpi).

Structural diagrams (architecture, pipeline, data flow) need no run data and are drawn with
matplotlib primitives for full styling control. The scorecard and knowledge-graph figures are
drawn from the live database / latest verification report. Output: outputs/figures/*.png.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#20262e"
MUTED = "#5f6874"
MACHINE = "#0e6b74"
HUMAN = "#a8482f"
LINE = "#c9c4b8"
PAPER = "#f7f5f0"
TYPE_COLORS = {"Context": "#8a5a12", "Intervention": "#0e6b74",
               "Mechanism_Resource": "#3a6ea5", "Mechanism_Response": "#7b4397",
               "Outcome": "#2c6e49"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})


def _box(ax, x, y, w, h, text, fc="#ffffff", ec=LINE, tc=INK, fs=10, bold=False, round=0.02):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.01,rounding_size={round}",
                                fc=fc, ec=ec, lw=1.2, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc, fontsize=fs,
            fontweight="bold" if bold else "normal", zorder=3, wrap=True)


def _arrow(ax, x1, y1, x2, y2, color=MUTED, style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=13,
                                 color=color, lw=1.3, zorder=1))


def architecture():
    fig, ax = plt.subplots(figsize=(10, 6.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.4); ax.axis("off")
    ax.text(0.1, 6.15, "System architecture", fontsize=15, fontweight="bold", color=INK)
    ax.text(0.1, 5.85, "Staged multi-agent pipeline over one typed source of truth; human sovereign "
            "at five checkpoints", fontsize=9.5, color=MUTED)
    # Core pipeline band
    stages = ["Ingest", "Screen", "Extract\n+ self-refine", "Normalise\n+ communities",
              "Synthesise", "Programme\ntheory"]
    x = 0.2
    for i, s in enumerate(stages):
        _box(ax, x, 3.7, 1.42, 0.95, s, fc=PAPER, ec=MACHINE, tc=MACHINE, fs=9.2, bold=True)
        if i:
            _arrow(ax, x - 0.18, 4.17, x, 4.17, MACHINE)
        x += 1.6
    ax.text(0.2, 4.8, "CORE PIPELINE (method-agnostic + realist plugin)", fontsize=9,
            color=MACHINE, fontweight="bold")
    # HITL band
    for i, (hx, hk) in enumerate([(0.9, "HITL-0"), (2.5, "HITL-1"), (4.1, "HITL-2"),
                                  (7.3, "HITL-3"), (8.9, "HITL-2/4")]):
        _box(ax, hx, 2.75, 1.0, 0.55, hk, fc="#f4e4e1", ec=HUMAN, tc=HUMAN, fs=8.3, bold=True)
        _arrow(ax, hx + 0.5, 3.32, hx + 0.5, 3.68, HUMAN)
    ax.text(0.2, 3.4, "HUMAN-IN-THE-LOOP", fontsize=9, color=HUMAN, fontweight="bold")
    # Data layer
    _box(ax, 0.2, 1.35, 4.7, 0.95, "PostgreSQL — single source of truth\n(studies · CMOCs · "
         "entities · relations · HITL · audit)", fc="#eef1f4", ec=LINE, fs=8.6)
    _box(ax, 5.1, 1.35, 2.3, 0.95, "Parquet LKG\n(canonical artifact)", fc="#eef1f4", ec=LINE, fs=8.6)
    _box(ax, 7.6, 1.35, 2.2, 0.95, "Neo4j\n(graph exploration)", fc="#eef1f4", ec=LINE, fs=8.6)
    ax.text(0.2, 2.45, "DATA LAYER — every claim carries {study, span, verbatim quote, model, "
            "confidence}", fontsize=9, color=INK, fontweight="bold")
    for sx in (2.5, 6.2, 8.6):
        _arrow(ax, sx, 3.68, sx, 2.32, LINE)
    # Verification (outside)
    _box(ax, 0.2, 0.2, 9.6, 0.8, "VERIFICATION HARNESS — compares outputs to the Richmond (2020) "
         "benchmark. The answer key is read only here, never by the agents (anti-contamination).",
         fc="#e4efe6", ec="#2c6e49", tc="#2c6e49", fs=8.8, bold=True)
    fig.savefig(OUT / "fig_architecture.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def pipeline_algorithm():
    fig, ax = plt.subplots(figsize=(7.6, 8.2))
    ax.set_xlim(0, 7.6); ax.set_ylim(0, 8.2); ax.axis("off")
    ax.text(0.1, 7.95, "The core algorithm", fontsize=15, fontweight="bold", color=INK)
    ax.text(0.1, 7.65, "One paper's path from text to a verified, typed CMOC; then cross-study "
            "synthesis and retroduction", fontsize=9, color=MUTED)
    steps = [
        ("1  Ingest", "PDF/abstract -> clean text -> units with character offsets", MACHINE),
        ("2  Screen", "two models vote on theory-relevance; disagreements -> human", MACHINE),
        ("3a  Draft CMOCs", "typed Context-Mechanism-Outcome, a verbatim quote per element", MACHINE),
        ("3b  Reflect", "independent checker (different model) critiques the draft", HUMAN),
        ("3c  Self-refine", "extractor REVISES to fix the issues (guarded against over-correction)",
         MACHINE),
        ("3d  Verify + ground", "score quote support; resolve each quote to an exact span", MACHINE),
        ("3e  Validate", "keep a relation only if it satisfies the ontology's domain/range", MACHINE),
        ("4  Normalise + communities", "merge synonyms; Leiden -> emergent conceptual entities",
         MACHINE),
        ("5  Synthesise", "recurring CMOC motifs + contradictions (deterministic graph queries)",
         MACHINE),
        ("6  Programme theory", "compose the five-context theory; human signs off", MACHINE),
        ("7  Retroduce", "re-read the weakest studies under the refined theory until stable", MACHINE),
    ]
    y = 7.0; h = 0.56
    for title, desc, col in steps:
        _box(ax, 0.3, y, 7.0, h, "", fc=PAPER, ec=col, round=0.015)
        ax.text(0.5, y + h / 2, title, ha="left", va="center", fontsize=9.6, fontweight="bold",
                color=col)
        ax.text(2.75, y + h / 2, desc, ha="left", va="center", fontsize=8.5, color=INK)
        if y < 7.0 - 0.01:
            _arrow(ax, 3.8, y + h + 0.03, 3.8, y + h + 0.005, LINE)
        y -= h + 0.075
    fig.savefig(OUT / "fig_pipeline.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def dataflow():
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3.6); ax.axis("off")
    ax.text(0.1, 3.35, "How the data is processed", fontsize=14, fontweight="bold", color=INK)
    ax.text(0.1, 3.05, "The same path for 28 or 1000 papers — nothing enters the graph without a "
            "quote that resolves to the source", fontsize=8.8, color=MUTED)
    nodes = [("A PDF or\nabstract", "#eef1f4", LINE),
             ("Clean text +\ntext units\n(char offsets)", "#eef1f4", LINE),
             ("CMOCs:\nC -> M -> O\n+ verbatim quotes", PAPER, MACHINE),
             ("Quotes resolved\nto exact spans\n(else flagged)", PAPER, MACHINE),
             ("Typed knowledge\ngraph + communities", "#e4efe6", "#2c6e49")]
    x = 0.25; w = 1.75
    for i, (t, fc, ec) in enumerate(nodes):
        _box(ax, x, 1.15, w, 1.35, t, fc=fc, ec=ec, fs=9)
        if i:
            _arrow(ax, x - 0.2, 1.82, x, 1.82, MUTED)
        x += 1.95
    ax.text(5.0, 0.55, "provenance is preserved end to end", ha="center", fontsize=8.5,
            color=MUTED, style="italic")
    fig.savefig(OUT / "fig_dataflow.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def scorecard(report_path: str | None = None):
    """Bar chart of the benchmark scorecard from a verification_report.json."""
    if report_path is None:
        reps = sorted((Path(__file__).resolve().parents[1] / "outputs" / "runs").glob(
            "verify-*/verification_report.json"), key=lambda p: p.stat().st_mtime)
        if not reps:
            return
        report_path = reps[-1]
    r = json.load(open(report_path, encoding="utf-8"))
    items = [
        ("Screening\nsensitivity", r["screening"]["final_sensitivity_after_hitl"] * 100, "#2c6e49"),
        ("Relation\npattern-level", r["relation_coverage"].get("type_recall", 0) * 100, "#2c6e49"),
        ("Citation\nfaithfulness", r["citation_faithfulness"]["faithfulness"] * 100, "#2c6e49"),
        ("Entity\ncoverage", r["entity_coverage"]["recall"] * 100, "#8a5a12"),
        ("Community-\nmechanism", r.get("community_alignment", {}).get("alignment_recall", 0) * 100,
         "#3a6ea5"),
        ("Relation\nstrict", r["relation_coverage"]["recall"] * 100, "#9e3328"),
    ]
    fig, ax = plt.subplots(figsize=(8, 4))
    labels = [i[0] for i in items]
    vals = [i[1] for i in items]
    cols = [i[2] for i in items]
    bars = ax.bar(labels, vals, color=cols, width=0.62, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.0f}%", ha="center", fontsize=10,
                fontweight="bold", color=INK)
    ax.set_ylim(0, 105); ax.set_ylabel("agreement with Richmond (2020)")
    ax.set_title("Preliminary benchmark scorecard", fontsize=13, fontweight="bold", loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e6e3db", zorder=0)
    ax.axhline(0, color=LINE)
    fig.savefig(OUT / "fig_scorecard.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def knowledge_graph():
    """Family-level knowledge-graph snapshot from the canonical parquet LKG (no DB needed)."""
    import networkx as nx
    import pandas as pd

    lkg = Path(__file__).resolve().parents[1] / "outputs" / "lkg"
    ent = pd.read_parquet(lkg / "entities.parquet")
    rel = pd.read_parquet(lkg / "relationships.parquet")
    ent = ent[ent["family_id"].notna()]
    # relationships reference CANONICAL ids (e.g. "mech:similarity-reasoning"), so map
    # canonical_id -> family_id, not the entity-instance id.
    canon2fam = dict(zip(ent["canonical_id"], ent["family_id"]))
    fam_meta = (ent.groupby("family_id").agg(t=("type", "first"),
                label=("family_label", "first")).reset_index())
    g = nx.DiGraph()
    for _, f in fam_meta.iterrows():
        g.add_node(f["family_id"], t=f["t"], label=str(f["label"] or "")[:22])
    for _, e in rel.iterrows():
        s, o = canon2fam.get(e["source"]), canon2fam.get(e["target"])
        if s and o and s != o and s in g and o in g:
            g.add_edge(s, o)
    if g.number_of_nodes() == 0:
        return
    fig, ax = plt.subplots(figsize=(11.5, 8.5))
    try:
        pos = nx.kamada_kawai_layout(g)
    except Exception:  # noqa: BLE001
        pos = nx.spring_layout(g, k=1.6, seed=7, iterations=400)
    deg = dict(g.degree())
    nx.draw_networkx_edges(g, pos, ax=ax, edge_color="#d3cfc4", arrows=True, arrowsize=7,
                           width=0.6, alpha=0.55, connectionstyle="arc3,rad=0.08")
    for t, col in TYPE_COLORS.items():
        nodes = [n for n, d in g.nodes(data=True) if d["t"] == t]
        sizes = [140 + 26 * deg.get(n, 1) for n in nodes]
        nx.draw_networkx_nodes(g, pos, nodelist=nodes, node_color=col, node_size=sizes,
                               ax=ax, edgecolors="white", linewidths=1.2)
    # Label only the better-connected families to avoid a wall of overlapping text.
    top = {n for n, _ in sorted(deg.items(), key=lambda kv: -kv[1])[:16]}
    labels = {n: d["label"] for n, d in g.nodes(data=True) if n in top}
    for n, lab in labels.items():
        x, y = pos[n]
        ax.text(x, y + 0.045, lab, fontsize=6.6, ha="center", va="bottom", color="#20262e",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.72))
    ax.legend(handles=[mpatches.Patch(color=c, label=t.replace("_", " "))
                       for t, c in TYPE_COLORS.items()], loc="upper left", fontsize=8, frameon=False)
    ax.set_title("Literature knowledge graph (concept-family view)", fontsize=13,
                 fontweight="bold", loc="left")
    ax.axis("off")
    fig.savefig(OUT / "fig_kg.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "structural"
    if which in ("structural", "all"):
        architecture(); pipeline_algorithm(); dataflow()
        print("structural figures written")
    if which in ("data", "all"):
        scorecard(); knowledge_graph()
        print("data figures written")
