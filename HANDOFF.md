# Project Handoff — Agentic Realist Evidence Synthesis

_A one-document orientation for the RA and professor. Written for a reader who has not followed
the build. Last updated 2026-07-14._

## 1. What this project is (in one paragraph)

This is the software and evidence behind a **methodological-innovation paper for Review of
Research in Education (RRE) 2026**. It proposes an **agentic, human-in-the-loop, GraphRAG-based
multi-agent pipeline** that automates the analytic operations of a **realist systematic review**
(RAMESES standards) in education. The pipeline is validated by reproducing **Richmond et al.
(2020)** — a realist review of educational interventions for clinical reasoning (28 included
studies) — and comparing its outputs to Richmond's human results. **The contribution is the
method; Richmond is the worked example. Human judgment stays sovereign at four checkpoints.**

## 2. What it does, stage by stage (plain language)

1. **Ingest** the 28 papers → clean text with exact character offsets (every later claim is
   traceable to its source span).
2. **Screen** each paper (include/exclude/uncertain) using two AI models that vote, tuned to never
   miss a relevant study; a human adjudicates the "uncertain" ones (**Checkpoint 1**).
3. **Extract CMOCs** (Context–Mechanism–Outcome Configurations) from each paper — the realist unit
   of analysis — with a mandatory verbatim quote for every element and an automatic
   quote-supports-claim check; a human spot-checks (**Checkpoint 2**).
4. **Build the knowledge graph** of typed concepts and causal relations; cluster synonymous
   concepts; detect **demi-regularities** (recurring patterns) and **contradictions** (same driver,
   opposite outcomes) — a human resolves contradictions (**Checkpoint 3**).
5. **Compose the programme theory** (why interventions work, for whom, in what circumstances); a
   human signs off (**Checkpoint 4**).
6. **Report**: PRISMA flow, CMOC evidence table, programme-theory diagram, verification dashboard,
   full audit trail — the same artifact genres Richmond published.

## 3. How well it reproduces the human review (the headline result)

See `outputs/MASTER_VERIFICATION_REPORT.md` for the full scorecard. Summary:

| Operation | Result vs Richmond |
|---|---|
| Recover the 28 included studies | **100%** (after human adjudication) |
| Reject irrelevant papers (72-distractor test) | 76% (recall-first) → **98.6%** (precision-first) |
| Recover Richmond's entities E01–E47 | **~72–79%** |
| Recover Richmond's causal-relation patterns R01–R40 | **97.5%** (39/40) |
| Claims anchored to a verbatim source quote | **98.3%** |
| Correspondence to Richmond's 5 programme-theory chains | 0.50–0.54 |

The programme theory independently reconstructs Richmond's core findings: *the student is key*,
dual-process (analytical/non-analytical) reasoning, and the expertise-reversal effect. Where the
system does not reach 100%, the honest reason is documented (e.g. the missing entities are
coping/emotion concepts with near-zero textual basis in the available corpus —
`outputs/corpus_coverage_analysis.json` — which the system correctly declines to invent).

## 4. How to run it (reproducible)

```powershell
cd "D:\Realist Evidence Synthesis\Realist Evidence Synthesis V2"
pip install -e ".[dev,viz]"      # first time
# credentials are in .env (OpenAI key, Postgres pwd, Neo4j pwd)

res init-db            # create the PostgreSQL schema
res ingest             # Phase 1: registry + text units
res screen             # Phase 2: dual-model screening
res adjudicate         # Checkpoint 1 (human)
res extract            # Phase 3: CMOC extraction (gpt-5.5)
res validate-cmocs     # Checkpoint 2 (human)
res synthesize         # normalization → motifs → contradictions → programme theory
res verify             # compare to Richmond gold standard
res precision-test     # distractor pool + specificity
res gold-code          # independent per-paper reference gold
res build-lkg          # canonical parquet knowledge graph
res load-neo4j         # load into Neo4j for exploration
res report             # generate all artifacts
res status             # overview
```

`res run-all` chains ingest→verify→report for a batch run (still run the human checkpoints).

## 5. Where everything lives

- **Code:** `src/res_pipeline/` (core/, plugins/realist/, graph/, verification/).
- **Config (researcher-editable):** `config/` — `protocol.yaml` (eligibility), `ontology.yaml`
  (entity/relation types), `models.yaml` (LLM tiers), `prompts/`.
- **Data (read-only input):** `data/` — the 28 papers + Richmond primary.
- **Gold standards:** `gold/richmond_gold.json` (review-level, verified) + `gold/per_paper_gold/`
  (per-paper reference coding) + `outputs/gold/per_paper_coding_coder_A/B.xlsx` (human κ workbooks).
- **Results:** `outputs/` — `MASTER_VERIFICATION_REPORT.md`, `precision_test_report.md`,
  `corpus_coverage_analysis.json`, `lkg/` (parquet graph), `runs/<id>/` (dashboards + reports).
- **Storage:** PostgreSQL `realist_synthesis` (D:/Appdata/pg) = single source of truth; parquet =
  canonical graph artifact; Neo4j = exploration layer.
- **Project memory:** `CLAUDE.md`, `docs/PROJECT_CONTEXT.md`, `docs/ARCHITECTURE.md`,
  `docs/DECISION_LOG.md`, `docs/research/SOTA_REPORT.md`, `WALKTHROUGH.md` (19 milestones).

## 6. What still needs a human (before journal submission)

1. **Two human coders** complete `outputs/gold/per_paper_coding_coder_A/B.xlsx` (blind) → compute
   Cohen's κ → replaces the AI-assisted per-paper reference with a true human gold standard.
2. **Professor ratifies** the delegated HITL decisions (logged in the `hitl_ratifications` table).
3. **Human ratification pass** on the LLM-judged metrics (entity coverage, theory correspondence).
4. Optional: expand the corpus with the missing simulation/emotion studies to lift entity coverage;
   move Neo4j data to D: (junction) when the app is closed.

## 7. Honest bottom line

The system reproduces the analytic structure of an expert human realist review — strongest on the
operations that most define such a review (recovering the studies, the causal-relation structure,
and span-grounded evidence), with every shortfall measured and explained rather than hidden. This
is defensible evidence for the RRE 2026 claim that agentic GraphRAG can reproduce realist synthesis
at a level comparable to expert human reviewers, with human oversight preserved throughout.
