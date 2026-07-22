# DECISION LOG

Append-only record of significant decisions (architecture, technology, ontology, methodology)
with date, the decision, the rationale, and who approved it. Keeps future sessions from silently
re-litigating settled choices or forgetting why something was chosen.

Format:
```
## YYYY-MM-DD — <short title>
- Decision:
- Rationale (grounded in which sources / research):
- Approved by:
- Supersedes / relates to:
```

---

## 2026-07-14 — Project restarted fresh in `Realist Evidence Synthesis V2`
- Decision: rebuild the project from scratch in V2 rather than continue the old
  `LLM-Knowledge-Graph`; use the old project as reference only.
- Rationale: RA found the old (Cursor/Antigravity-built) version confusing and not meeting the
  professor's requirements; wants a clean, professional, research-grounded rebuild.
- Approved by: Duy Nguyen (RA).

## 2026-07-14 — Working process: research-first, architecture approval before build
- Decision: Claude finishes reading (May 28 meeting, remaining professor PDFs, Richmond paper) +
  does SOTA web research, then presents a grounded ARCHITECTURE PROPOSAL for RA approval before
  writing pipeline code.
- Rationale: RA's choice; also matches the professor's repeated "architecture first" guidance.
- Approved by: Duy Nguyen (RA).

## 2026-07-14 — Orchestration + knowledge stack
- Decision: use **LangChain + LangGraph** for orchestration and **Microsoft GraphRAG** (open-source)
  for the Literature Knowledge Graph. "Microsoft Graph" (the M365 SharePoint/Teams API) is a
  DIFFERENT thing — it is optional; implement a local provenance layer described as
  "MS-Graph-compatible", upgradeable to real M365 later only if the professor insists.
- Rationale: RA confirmed LangChain+LangGraph; clarified the GraphRAG vs Graph confusion. M365 is
  overkill for a 28-PDF local verification prototype; the science lives in GraphRAG + the LKG.
- Approved by: Duy Nguyen (RA) — "use whatever is useful/optimal; use both if needed."

## 2026-07-14 — LLM provisioning
- Decision: RA provides an OpenAI API key; Claude selects models per task to balance cost/quality
  (e.g. cheaper models for screening/dedup, stronger models for CMOC extraction/synthesis).
  Concrete model choices to be proposed in the architecture doc BEFORE spending API credit.
- Approved by: Duy Nguyen (RA).

## 2026-07-14 — Architecture v1.0 adopted (seven grounded decisions)
- Decision: adopt `docs/ARCHITECTURE.md` v1.0 — D1 constrained typed extraction + GraphRAG BYOG;
  D2 novelty = first agentic realist-synthesis framework; D3 hybrid ontology (5 fixed entity
  types, 5 fixed predicates with domain/range constraints, emergent instances, E-code mapping
  only at verification, nanopub-style provenance); D4 tiered models (gpt-5.4-mini screening +
  gpt-4.1-mini second vote; gpt-5.4 extraction/synthesis; text-embedding-3-small; multi-vendor
  ensemble deferred to sensitivity analysis); D5 storage = Postgres (state/audit SoT) + parquet
  (canonical LKG artifact) + Neo4j (derived query/viz); D6 verification = fresh independent
  human per-paper CMOC gold (2 coders, Cohen's κ), AI-adjudicated xlsx demoted to suggestion
  aid; D7 HITL via LangGraph interrupt()/Command(resume) + AsyncPostgresSaver, feedback-to-
  few-shot loop.
- Rationale: each decision cites `docs/research/SOTA_REPORT.md` and/or professor documents.
- Approved by: Duy Nguyen (RA) — granted full build authority ("bạn cứ làm rồi chạy luôn",
  2026-07-14); architecture documented as the required record.

## 2026-07-14 — New standing requirements from the RA
- WALKTHROUGH.md: append a milestone entry (what/why/strengths/limitations) for every work
  session — layman-readable reporting is part of definition-of-done.
- Output design: system must emit the SAME artifact genres as Richmond's paper for 1:1
  human-vs-machine comparison (see ARCHITECTURE §6).
- Credentials: PostgreSQL password provided and stored in .env; Neo4j installed but not yet
  configured (set up during Phase 0/5). Both the OpenAI key and Postgres password were pasted
  in chat → rotate after the project stabilizes.

## 2026-07-14 — Model upgrade for quality-critical stages
- Decision: extraction and synthesis tiers → **gpt-5.5** (strongest reasoning tier available on
  the key); screening/verifier/normalization stay on mini tiers for cost. `llm.py` now sends
  `temperature` only when a tier declares one (gpt-5.5 accepts only the default) and always
  sends a fixed `seed` for best-effort reproducibility. Extraction prompt bumped to v2.0
  (mandatory affective Mechanism_Response capture, explicit negative pathways, 2-5 CMOCs).
- Rationale: RA directive to use the strongest-reasoning model while keeping cost optimal;
  first-pass verification showed the extractor under-captured affective responses and negative
  chains (PTS3/PTS4 weak) and relation coverage was low. Clarification: "best model" refers to
  the OpenAI API tier for the pipeline AND (separately) the Claude model the assistant runs on
  (Fable 5 vs Opus 4.8) — the latter is switched by the RA via /model, not by the assistant.
- Approved by: Duy Nguyen (RA).

## 2026-07-14 — Relation coverage measured at two levels
- Decision: report BOTH strict (exact concept match on both endpoints) AND type-level (predicate
  links an entity of the gold subject-type to one of the gold object-type) relation recovery,
  clearly labelled, never conflated. Rationale: strict recall is upper-bounded by entity-recall²
  and understates whether the causal *pattern* was recovered — the methodologically appropriate
  question for realist synthesis. Not metric-gaming: both numbers are always shown.

## (still-pending decisions)
- Neo4j initial password/setup (do during scaffold).
- Second human coder for per-paper gold standard (RA to arrange; professor?).
- Budget ceiling per full pipeline run (set after 3-paper pilot).
