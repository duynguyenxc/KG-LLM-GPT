# SOTA Research Report — Grounding the V2 Architecture

_Date: 2026-07-14. Method: multi-angle web research (5 parallel search angles → source fetch →
claim extraction). The adversarial cross-verification stage was interrupted by infrastructure
rate limits, so each claim below carries an explicit **source-quality label** (primary =
official docs / peer-reviewed / arXiv full text read; secondary = reputable technical write-up;
blog = engineering blog, treat as directional). Claims marked ⚠ should be re-verified before
being cited verbatim in the manuscript._

---

## Q1. GraphRAG variants & imposing a typed ontology

**Findings**
- Microsoft GraphRAG's extraction prompt is a single unified prompt (instructions + few-shot
  examples + "gleanings" re-ask loop). Default entity examples are only person/organization/geo,
  and `entity_types` **is configurable per domain**. Microsoft's *auto-tuning* generates
  domain-adapted extraction prompts from a corpus sample. [primary — Microsoft Research blog,
  microsoft.github.io/graphrag]
- GraphRAG's native output is **Parquet tables** (`entities`, `relationships`, `text_units`,
  `communities`) where relationships carry `text_unit_ids` → **built-in provenance to source
  chunks**. It also supports **BYOG (bring-your-own-graph)**: you can supply your own
  entities/relationships tables and still use its community detection + global/local search.
  [primary — official docs]
- **Ontology-guided extraction beats schema-free**: OMD-GraphRAG (arXiv 2603.25152) injects a
  formal schema S=(E,R,Φ) with domain/range constraints Φ(r)=(dom(r),range(r)) into the prompt
  and **post-hoc validates every triple**, discarding violations; reports +3.17% F1 over
  schema-free and +9.21% over LightRAG on MultiHop-RAG. [primary — arXiv] ⚠ verify numbers
- OG-RAG reports ~40% hallucination reduction from schema-constrained extraction. [blog] ⚠
- Known trade-off of fixed typologies: an "extraction miss rate" for entities outside defined
  types. [blog — TrustGraph]
- HippoRAG builds a **schemaless** graph via OpenIE + Personalized PageRank — optimized for
  multi-hop retrieval, a **poor fit** for a fixed relation typology. nano-graphrag is a ~1.1k-LOC
  hackable reimplementation (typed entities, file-based storage) — attractive for hacking but
  loses the professor-named Microsoft lineage. [secondary/blog]
- Cost: GraphRAG indexing carries a 10–40× premium over vector RAG at scale, but for **28
  papers the absolute cost is trivial** (single-digit dollars with a mini-tier model). GraphRAG
  shines on multi-hop/connected reasoning (one blog benchmark: 86% vs 32% vs vector RAG) and
  *underperforms* plain RAG on single-hop factoids — fine for us, realist synthesis is
  inherently multi-hop. [blog — directional only] ⚠

**Recommendation** — Keep **Microsoft GraphRAG** (professor's named choice, provenance model,
community detection) but do **not** rely on its default free-text extraction for the scientific
core. Use a **two-layer design**: (1) our own **CMOC Extraction Agent** produces typed,
span-grounded, Pydantic-validated triples under the fixed relation typology (OMD-GraphRAG
pattern: schema in prompt + post-hoc domain/range validation); (2) load them via **BYOG** into
GraphRAG's parquet model to get Leiden communities + GraphRAG query on top of a *clean typed
graph*. Custom `entity_types` + tuned prompts for the exploratory emergent layer.

## Q2. Prior art on LLM/agentic systematic-review automation

**Findings**
- **Title/abstract screening** is the most mature stage. A 2025 meta-analysis (J Med AI) of
  LLM screening: AUROC 0.922, pooled sensitivity 0.812 (95% CI 0.617–0.920), heterogeneity
  I²=91.6–99.7% (performance wildly inconsistent across studies). Their GPT-4o-mini config hit
  100% sensitivity at 81% specificity / 14% precision — the canonical pattern: **tune for
  recall, let humans clear false positives**. [primary — peer-reviewed]
- A dual-model LLM **ensemble reaches near-perfect sensitivity** for SR screening across
  domains (medRxiv 2025). [primary preprint]
- **Extraction**: Collaborative two-LLM cross-critique (GPT-4-turbo + Claude-3-Opus, JAMIA
  2025): accuracy 0.85, precision 0.78, **recall 0.63**, F1 0.70 — concordance ensembling beat
  either single model; recall is the weak spot. [primary]
- **ExtractBench (2026)**: frontier models achieve only **4.6% overall field-level pass rate**
  on complex schemas; a 13-field schema got 56.3% while a 369-field schema got 0%. Lesson:
  **keep extraction schemas narrow** (one CMOC at a time, few fields), valid JSON ≠ correct
  content, use per-field scoring + semantic alignment for lists. [primary — arXiv] ⚠ verify
- LLM+HITL validation for SR extraction exists as prior art (arXiv 2501.11840). Multi-agent
  screening architectures (LLM-MAS) argue single models have bias/misalignment. [primary preprints]
- **Gap confirmed**: no published framework reproduces **realist/RAMESES synthesis** (CMOC
  extraction → programme theory). Surveys of LLM-assisted reviews don't cover it. **This is the
  paper's novelty claim — and it appears genuine.** [supported across sources]

**Recommendation** — Cite screening meta-analysis + ensemble evidence to justify a
recall-first screening design with human adjudication; cite ExtractBench + JAMIA to justify
narrow-schema, span-grounded, self-checked extraction with HITL validation; claim the realist
gap explicitly in the manuscript.

## Q3. Ontology & relation-typology design

**Findings**
- **RAMESES II** (BMC Medicine, Delphi, 20 items) *mandates explicitly labelling what is
  Context vs Mechanism vs Outcome* in reported CMOCs, and demands transparency of analytic
  reasoning ("what was done, why and how"). Our fixed C/I/M_res/M_resp/O typology is therefore
  not just the professor's preference — it is **the reporting standard**. [primary]
- Span-grounded extraction: anchor every entity/relation to character-level spans with a
  predefined taxonomy (MDPI Computers 2026 anchor-constrained framework). Provenance-statement
  patterns: RDF-star / named graphs / **nanopublications** (assertion, provenance, publication
  info as separate graphs); provenance-driven nanopublications handle **multi-source assertions**
  — exactly our case where one programme-theory edge is supported/contradicted by several
  papers. [primary]
- Ontology-grounded KG construction under a fixed schema (Wikidata-schema paper, arXiv
  2412.20942) and evidence-KGs from curated full-text corpora (arXiv 2603.28325) provide citable
  precedents. TRACE-KG argues the emergent counter-position — useful to cite-and-bound. [primary]

**Recommendation** — **Hybrid ontology**: fixed **5 entity types + 5 relation predicates with
domain/range constraints**; emergent free-text entity *instances* (labels) that are normalized
by a dedicated agent and mapped to Richmond E-codes **only in the verification layer** (never
hard-coded into extraction, avoiding the old version's circularity). Every node/edge carries
`{study_id, text_unit_id, char_span, verbatim_quote}` (nanopublication-style separation of
assertion vs provenance). Proposed domain/range map:
`PROVIDES: Intervention→Mechanism_Resource · TRIGGERS: {Intervention,Mechanism_Resource}→Mechanism_Response ·
ENABLES: Context→{Mechanism_Response,Outcome} · LEADS_TO: Mechanism_Response→{Mechanism_Response,Outcome} ·
CONSTRAINS: Context→Outcome` (validated against all 40 gold relations R01–R40 — fits).

## Q4. Model selection & ensembling

**Findings** — see Q2 metrics. Additional: LLM-Ensemble survey (arXiv 2502.18036) taxonomizes
before/during/after-inference ensembling; gains vary by task ("not a guaranteed win"); token-level
ensembling impractical across vendors; LLM-judge ensembles can suffer multicollinearity.
GPT-4o was the most balanced extractor in a 2026 Frontiers benchmark vs Claude 3 Haiku/GPT-3.5.
[primary/secondary]

**Recommendation (cost-tiered, single-vendor first)**
| Task | Model | Rationale |
|---|---|---|
| T/A screening (28→ or ~100-paper pool) | `gpt-5.4-mini`, temp 0, recall-tuned rubric | cheap, meta-analysis supports mini-tier at 100% sens config |
| Screening 2nd vote (ensemble) | `gpt-4.1-mini` (different family lineage) | dual-model union → near-perfect sensitivity evidence |
| CMOC extraction (per-paper, narrow schema) | `gpt-5.4` | extraction is the hard task (ExtractBench); strongest sensible tier |
| Extraction self-check / verifier pass | `gpt-5.4-mini` quote-support check | JAMIA cross-critique pattern, cheap |
| Cross-study synthesis + contradiction | `gpt-5.4` (escalate to `gpt-5.4-pro` only if needed) | reasoning-heavy, low volume |
| Embeddings | `text-embedding-3-small` | GraphRAG default, sufficient at this scale |

Multi-vendor (Claude/Gemini) ensembling: **defer to an optional robustness experiment** —
evidence shows dual-model helps screening recall, but complexity/cost isn't justified for the
core pipeline; note it in the paper as a sensitivity analysis. Estimated full-corpus cost at
this scale: **single-digit to low-tens of USD per full pipeline run** (28 papers ≈ 1–2M tokens
total through extraction) — verify empirically on a 3-paper pilot before full runs.

## Q5. Storage backend

**Findings** — GraphRAG emits parquet with provenance columns [primary]; documented import path
parquet→Neo4j for motif/subgraph Cypher queries [secondary — Neo4j dev blog]; Neo4j reported
~85–135× faster multi-hop traversal vs Postgres in a 2026 comparison [blog ⚠]; LangGraph
production HITL requires a persistent checkpointer, `AsyncPostgresSaver` recommended [primary —
LangChain docs].

**Recommendation** — **All three, each in its lane** (all already available on this machine):
- **Parquet (GraphRAG-native)** = canonical, reproducible, publishable KG artifact (ships as
  online supplement).
- **PostgreSQL** = pipeline single-source-of-truth: LangGraph checkpoints (AsyncPostgresSaver),
  study registry, decisions, HITL feedback, audit log.
- **Neo4j** = derived query/visualization layer for motif (CMOC-pattern) queries and the
  interface; rebuilt from parquet at any time (never the source of truth).

## Q6. Verification methodology (non-circular)

**Findings** — RAMESES II: transparency of analytic reasoning is *the* rigour criterion; CMO
labelling must be explicit; standards "supplement rather than replace" human judgement (direct
justification for HITL sovereignty). [primary] Screening meta-analysis warns gold-standard
human labels themselves contain errors → report IRR. Low-prevalence screening validation used a
500-record human gold standard with sensitivity/specificity/precision (MDPI Information 2026) —
a good template. ExtractBench's per-field scoring + semantic alignment is the right fidelity
model for CMO slots. [primary]

**Recommendation**
1. **Gold standards**: (a) review-level gold = E01–E47/R01–R40/PTS1–5 (verified against the
   published paper — external, non-circular); (b) **per-paper CMOC gold = fresh independent
   human coding** (Duy + second coder; Cohen's κ; adjudicate disagreements; the old AI-adjudicated
   xlsx may be used as *candidate suggestions shown after* human first-pass, never as truth).
2. **Stage metrics**: search overlap (recall of the 28 within retrieved pool); screening
   sensitivity/specificity/precision/F1 + κ vs human; extraction per-slot P/R/F1 (typed C, I,
   M_res, M_resp, O) with semantic-equivalence matching + relation-level P/R vs R01–R40 +
   **citation faithfulness** (does the quoted span actually support the triple — automated
   quote-check + human sample); community↔mechanism alignment (expert mapping); programme-theory
   correspondence (structured rubric against PTS1–5 chains, rated by ≥2 humans); contradiction
   detection vs known conflicts (e.g., expertise-reversal cases).
3. **Reporting**: per-stage results table + PRISMA-style flow + full audit trail as RAMESES II
   demands; explicitly state what is NOT automated (final interpretive judgement).

## Q7. LangGraph HITL patterns

**Findings** — `interrupt()` pauses the graph, persists state via checkpointer, resumes with
`Command(resume=...)`; interrupted threads cost nothing while paused and can resume months
later; the checkpoint is an *editable* shared workspace (human can edit state before resume);
four canonical patterns: approve/reject, review-&-edit-state, review tool calls, multi-turn;
conditional interrupts via `when` predicates; production = `AsyncPostgresSaver`. [primary —
LangChain/LangGraph official docs + blog]

**Recommendation** — Model the pipeline as one LangGraph StateGraph with typed Pydantic state;
each of the 4 HITL checkpoints = an `interrupt()` node emitting a structured adjudication
payload (items, AI rationale, confidence, evidence quotes) and accepting
approve/edit/reject+feedback; feedback rows persist to Postgres and are injected as few-shot
examples on the re-run edge (feedback-to-policy loop); the whole run is resumable and auditable
by construction. CLI adjudication first; thin web UI later.

## Q8 (added). What should the final output look like (human-vs-machine comparability)?

Grounded in Richmond's own artifact genres + RAMESES II: make the machine emit **the same
genres of artifact the human team published**, so comparison is one-to-one:
1. PRISMA flow diagram + counts (vs Richmond Fig 1).
2. Per-paper **CMOC evidence table** (typed slots + verbatim quotes + spans) — vs their
   NVivo/Excel extraction (Appendix S1/S2).
3. **Programme theory diagrams**: one overview of 5 contexts (vs Fig 2) + per-context CMOC
   chain diagrams (vs Fig 3), rendered from the typed KG (Mermaid/Graphviz + interactive HTML).
4. **Narrative programme theory** with italicised CMOC statements + n-studies support per claim.
5. **Verification dashboard**: side-by-side system-vs-Richmond per stage with all metrics.
6. **Audit trail** (every decision, prompt version, human intervention) — the RAMESES II
   transparency artifact.

---

### Consolidated source list (key)
Microsoft GraphRAG docs & auto-tuning blog (microsoft.github.io/graphrag; MS Research blog) ·
OMD-GraphRAG arXiv 2603.25152 · Ontology-grounded KG arXiv 2412.20942 · Anchor-constrained
provenance KG (MDPI Computers 15(3):178) · Provenance-enhanced statements arXiv 2606.15246 ·
Evidence KG from full-text literature arXiv 2603.28325 · TRACE-KG arXiv 2604.03496 · RAMESES II
reporting standards (Wong et al., BMC Medicine 2016; PMC4920991) · LLM screening meta-analysis
(J Med AI 2025) · Dual-model screening ensemble (medRxiv 2025.11.03.25339455) · Collaborative
LLM extraction (JAMIA 2025; medRxiv 2024.09.20.24314108) · LLM-MAS screening (medRxiv
2025.08.11.25333429) · HITL LLM extraction arXiv 2501.11840 · LLM-assisted SR survey arXiv
2409.04600 · ExtractBench arXiv 2602.12247 · LLM-Ensemble survey arXiv 2502.18036 · Frontiers
Digital Health 2026 extraction benchmark · MDPI Information 17(5):501 low-prevalence screening ·
LangChain/LangGraph HITL official docs · Neo4j dev blog (GraphRAG→Neo4j import) · nano-graphrag
breakdown [blog] · GraphRAG-vs-HippoRAG/PathRAG/OG-RAG comparison [blog] · Neo4j-vs-pgvector 2026
comparison [blog ⚠].
