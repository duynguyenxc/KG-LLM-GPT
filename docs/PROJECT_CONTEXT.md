> **Historical document - September 2026 audit supersedes performance and implementation claims below.** Read `docs/research/RESEARCH_AUDIT_STATUS.md`, `docs/research/RICHMOND_OFFICIAL_FINDINGS.md`, and `docs/research/METHOD_AND_VERIFICATION_PROTOCOL.md` from the repository root. Old AI judgments are not completed human validation.

# PROJECT CONTEXT — Realist Evidence Synthesis (living memory)

_Last updated: 2026-07-14. Maintained by Claude. This is the authoritative project memory.
Update it whenever understanding, decisions, or status change._

---

## 1. What this project actually is

- **Real deliverable:** a manuscript for **Review of Research in Education (RRE), Volume 50
  (2026)** — a AERA journal. It is a **methodological-innovation paper with a worked example**,
  explicitly *not* a tool/system paper and *not* a re-run of one review.
- The abstract/proposal was **already accepted** by the journal (see
  `documents/abstract-from-professor/abstract.md`).
- **Principal investigator / professor:** Wei Zheng. **RA (project owner / our collaborator):**
  Duy Nguyen. Meetings are weekly.
- **Framing that must survive peer review** (from the professor's editor-style critique):
  1. Method > platform (the AI system is *infrastructure enabling a method*, not the contribution).
  2. Review-methodology scholarship > AI novelty (introduction must read as if it could have been
     written before LLMs existed, then introduce AI as the enabler).
  3. Must address **change in complex educational systems** (RRE's mission).
  4. Human interpretive judgment preserved and foregrounded.

## 2. The proposed method (what we are building)

An **agentic, human-in-the-loop, GraphRAG-based multi-agent pipeline** for realist synthesis,
organized as a **core-and-plugin architecture**:

- **Core Review Infrastructure (method-agnostic "Review OS"):** protocol/scope, retrieval +
  provenance, study registry + deduplication, two-stage screening, reporting/audit export,
  and the HITL control layer.
- **Realist Synthesis Plugin (method-specific, the worked example):** IPT management, CMOC
  extraction, cross-study synthesis / demi-regularity detection, contradiction & sensitivity.
- The paper lays out *other* plugins conceptually (QCA, framework/thematic, meta-ethnography/CIS,
  meta-analysis/mixed-methods) but only **implements the Realist plugin**.

**Default agent set (~9–10 operational agents)** — professor's latest layout (NotebookLM doc):
Protocol & IPT · Search & Retrieval · Deduplication · Title/Abstract Screener ·
Full-Text Acquisition · Full-Text Eligibility · CMOC Extraction · (Normalization) ·
Theory Synthesis & Refinement · Contradiction & Sensitivity · Reporting & Audit.
> **Important correction from the professor:** the "Benchmark Agent" that compares model vs
> human is **NOT** part of the production pipeline. Model-vs-Richmond comparison is a
> *separate, independent evaluation activity* done for research verification only.

**Orchestration:** LangChain + **LangGraph** (stateful state-machine; "GraphChain" the professor
asked about is not a real product — LangGraph is the answer). Agents share a **single-source-of-truth
state** (study registry, LKG, CMOC store, theory store, audit log).

**Knowledge substrate:** a **Literature Knowledge Graph (LKG)** built with Microsoft **GraphRAG**
(entity/relation extraction + Leiden community detection + embeddings). **GraphRAG** retrieves
*subgraphs of connected claims* rather than isolated chunks, enabling configuration-level
("why/for whom/in what circumstances") reasoning. Professor's recurring concept: **"MOTIF
detection"** = treating CMOCs as recurring subgraph patterns; used for demi-regularity
consolidation and contradiction detection. He is aware subgraph isomorphism is NP-hard and
argues it is workable because relevant paper sets are small, retrieval is localized, and
embeddings/community structure prune the space.

**HITL "Master Control" — 4 checkpoints** (human decisions dominate; every correction is
recycled into prompts/rules = "lifelong/continual learning", with a "redo" trigger):
1. Screening adjudication (few-shot calibration on a stratified sample).
2. CMOC extraction validation (ground-truth spot-check).
3. Contradiction adjudication (human resolves conflict register).
4. Programme-theory sign-off.
Professor's forward-looking ideas: a "Living Project Handbook" (semantic policy anchoring),
active preference learning (RLHF-style), and an Adjudication UI sorted by uncertainty.

## 3. The Richmond benchmark (the worked example / gold standard)

Richmond A., Cooper N., Gay S., Atiomo W., Patel R. (2020). *The student is key: a realist review
of educational interventions to develop analytical and non-analytical clinical reasoning ability.*
Medical Education, 54(8), 709–719. https://doi.org/10.1111/medu.14137

- **RAMESES-standard realist review.** Workflow: Theory seeding (IPT, grounded in Dual-Process
  Theory) → structured search (MEDLINE, PsycINFO, ERIC, CINAHL; post-2000) → two-stage screening
  → CMOC extraction over **28 included papers** → synthesis of demi-regularities → final
  programme theory.
- **Headline finding:** *the student is key* — 5 student **contexts** defined mainly by
  pre-existing knowledge and self-confidence/self-efficacy determine which interventions work.
  Key phenomenon: **Expertise Reversal Effect** (directive/explicit teaching helps novices but
  hinders experts; unsupported observation harms low-knowledge students).
- **Corpus:** all 28 studies are clinical-reasoning-in-medical-education RCTs/studies
  (analytical vs non-analytical reasoning, self-explanation, worked/erroneous examples, schema
  instruction, simulation/virtual patients, feedback, serious games). See
  `data/studies_metadata.jsonl` (20 full-text PDFs + 8 abstract-only records).

**Operationalized gold standard already exists** (in the old project,
`../LLM-Knowledge-Graph/data/gold_standard.json`) — a defensible machine-checkable benchmark:
- **47 entities E01–E47** typed as Context / Intervention / Mechanism_Resource /
  Mechanism_Response / Outcome, each with a verbatim label + page location in Richmond.
- **40 relationships R01–R40** as (subject, predicate, object) triples with predicates
  PROVIDES / ENABLES / TRIGGERS / LEADS_TO / CONSTRAINS.
- **5 programme-theory statements PTS1–PTS5**, one per student context, each a canonical
  C→M→O chain.
This is genuinely reusable and probably the single most valuable asset from the old version.
**Verified 2026-07-14 against the primary source** (`data/paper-Richmond-original.pdf`): the 5
contexts, resource/response mechanism split, the five per-context CMOC statements, Expertise
Reversal + Matthew effects, and the search strategy (MEDLINE/PsycINFO/ERIC/CINAHL, from 2000,
searched May 2017; 149 full texts → 25 + 2 reference-list + 1 later = 28) all match. The
E-code/R-code/PTS operationalization is faithful and reusable. Only gap: a per-paper CMO mapping
coded by a *real independent human* (not AI) is still needed for verification step 2.

## 4. Verification protocol (how success is judged — separate from the pipeline)

From `documents/plan_verification_text.txt` (professor's 8-step plan). Compare model output to
Richmond's human output at each stage; report structural/conceptual correspondence, not verbatim:
1. **Search/screening alignment** — same search scope; overlap of model's included set vs the 28
   (recall/precision; explain divergences). Professor's variant: feed ~100 papers incl. the 28,
   see how close the model lands.
2. **CMOC extraction fidelity** — precision/recall of extracted C/M/O vs Richmond's CMOCs.
3. **Community ↔ mechanism alignment** — do emergent communities match Richmond's mechanisms.
4. **Cross-study synthesis** — do the same dominant + conditional patterns emerge.
5. **Programme-theory correspondence** — structural/conceptual match to PTS1–PTS5.
6. **Grounded Q&A** — "what works, for whom, why", forced CMOC framing + citations.
Boundary: the system does **not** claim to automate normative theory choice / final judgment.

## 5. Lessons from the OLD version (`../LLM-Knowledge-Graph/`)

What it did: a 10-agent LangGraph + Microsoft-GraphRAG pipeline (GPT-4o-mini) enforcing the
E01–E47 ontology via strict Pydantic Union types; produced PRISMA report, evidence table,
programme theory, dashboards; 1,318 entities / 1,672 relationships / 245 communities.

Why the RA was dissatisfied / open gaps (from its own `documents/Current_Project_Status_Gap_Report.md`):
- **Not yet a defensible research result.** Corpus coverage of all 28 studies unproven.
- **Relationship evaluation against R01–R40 never implemented.**
- **HITL checkpoints were auto-approve placeholders**, not real auditable human review.
- Output artifacts predate later fixes; need reconciling.
- Hardcoded paths (`d:\LLM-Knowledge-Graph\...`), `node_modules` committed — messy repo hygiene.
- **Tension to resolve:** the old pipeline *hardcoded* Richmond's E01–E47 ontology, but the
  professor's stated novelty is **community-defined / emergent conceptual entities** (not a
  predefined ontology). Reconcile: emergent extraction for the *method*; map to E-codes only for
  *verification* against Richmond. This is a central design question — do NOT silently re-hardcode.

### Assessment of `outputs/adjudication/Richmond_Per_Paper_Adjudication_Completed.xlsx`
- **What it is:** 57 model-extracted CMOC rows from the 28 papers, then adjudicated into
  `human_corrected_*` columns to build a *per-paper* CMOC benchmark (43 included / 14 excluded);
  fills the gap `gold_standard.json` flagged (no per-paper CMOC mapping). Good idea, well-structured
  (model baseline preserved, evidence quotes, support scores, decision-status taxonomy, data dictionary).
- **Serious caveat:** the "human_corrected" adjudication was itself **AI-assisted** (there is an
  `ai_adjudication_confidence` column; summary says "AI-assisted expert adjudication"). Using
  AI-adjudicated codes as the *gold standard* to then verify an AI pipeline is **circular** and
  will not survive reviewer scrutiny. For a defensible benchmark this per-paper coding needs a
  **genuine, independent human coder** (ideally 2 + inter-rater κ), or must be explicitly labelled
  as a *candidate* requiring human sign-off — never presented as ground truth.
- **Second caveat:** 16/57 rows are **abstract-only** — CMOCs extracted without full text; fidelity
  claims from those are weak and must be flagged or excluded.
- **Verdict:** valuable scaffolding and a good template to reuse, but not a usable gold standard
  as-is. Keep the structure; replace the AI adjudication with real human coding.

## 6. Current status & next steps

**Done:** read the accepted abstract, the 8-step verification plan, 3/4 meeting transcripts
(Jan 23, Feb 4, Feb 19), the full NotebookLM "agentic framework" professor doc, the old project's
README/main/architecture-FAQ/gap-report, `gold_standard.json`, `studies_metadata.jsonl`, and the
adjudication xlsx. Created V2 `CLAUDE.md` + this file.

**Key signal from the May 28 meeting (first half read):** the professor scrutinized the KG and
asked directly whether the **relation TYPES are predefined** — Duy admitted they are NOT (GraphRAG
auto-generates untyped entities/relations). The professor clearly wants **typed, named, directed
relations shown on the graph** (consistent with the R01–R40 predicate set:
PROVIDES/ENABLES/TRIGGERS/LEADS_TO/CONSTRAINS). This partly resolves the emergent-vs-predefined
tension: favour a **defined relation typology** while still allowing emergent *entity* discovery
(hybrid). Also: old runs only used ~5 of 28 papers due to token cost; Duy had shifted to a
multi-LLM (OpenAI+Claude+Gemini) approach for stronger screening; API budget is a live concern.

**Still to read before locking architecture:**
- Second half of `transcript-meetings/GMT20260528-...vtt` (logistics-heavy; outcomes already
  captured by the gap report which was written in response to this meeting).
- The other 2 professor PDFs: `new-documents-from-professor/grok output -KG and GraphRag-sent-2.pdf`,
  `Grok output plugin agent-sent-3.pdf`.
- Deep-read `data/paper-Richmond-original.pdf` + `Human-Workflow-from-paper-Richmond.pdf` +
  `in4-about-28-studies-paper.pdf` (to independently rebuild the gold standard rather than trust the old one).
- **SOTA web research** (required by the RA before deciding tech): current GraphRAG variants,
  realist-review automation prior art, KG ontology design for CMO/realist evidence, LLM
  screening/extraction benchmarks, model-vs-cost trade-offs, Neo4j vs Postgres+pgvector.

**Open decisions needing the RA / professor (see DECISION_LOG.md):**
- LLM choice + budget (RA offered an OpenAI key; consider quality-vs-cost across screening/
  extraction/synthesis; possibly tiered models).
- "Microsoft Graph" (the M365 enterprise API) — the professor's docs name it as the retrieval/
  provenance backbone, but for a research prototype verifying against 28 local PDFs it is likely
  overkill/aspirational. Decide: real M365 integration vs a simpler local provenance store that
  we *describe* as Microsoft-Graph-compatible.
- Storage/graph DB: Neo4j vs Postgres(+pgvector) vs file-based (parquet like the old version).
- Predefined E-code ontology vs emergent community-defined entities (see §5 tension).
- Whether the per-paper CMOC gold standard gets real independent human coding (needed for §4 step 2).
