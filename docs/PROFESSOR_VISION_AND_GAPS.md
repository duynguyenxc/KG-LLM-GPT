> **Historical document - September 2026 audit supersedes performance and implementation claims below.** Read `docs/research/RESEARCH_AUDIT_STATUS.md`, `docs/research/RICHMOND_OFFICIAL_FINDINGS.md`, and `docs/research/METHOD_AND_VERIFICATION_PROTOCOL.md` from the repository root. Old AI judgments are not completed human validation.

# The Professor's Full Vision, and an Honest Gap Analysis of Our System

_Built from a close reading of every source the professor provided: the accepted RRE abstract,
the 8-step verification plan, all meeting transcripts, and — critically — the three fresh design
documents in `documents/new-documents-from-professor/` (agentic framework, KG+GraphRAG, plugin
agent). This is the corrected, complete picture; earlier docs captured only part of it._

---

## 1. What the professor actually wants (not just "a multi-agent system")

**A core-and-plugin, HITL, multi-agent framework for systematic reviews in EDUCATION — general
across synthesis methods, with realist synthesis as the worked example.** The novelty and the RRE
selling point is *modularity*: the same core supports realist synthesis now, and framework/thematic
synthesis, meta-ethnography, critical interpretive synthesis, QCA, and mixed-method later.

Key design commitments, verbatim from his documents:

1. **Core (method-agnostic) vs Plugin (method-specific).** Core = protocol/IPT, search & retrieval,
   deduplication, two-stage screening, reporting/audit. Plugin (Realist) = CMOC extraction, theory
   refinement, contradiction detection. Orchestrated as a stateful workflow (LangGraph) over a shared
   state = **single source of truth**.

2. **~10 named production agents** (he explicitly EXCLUDES the Benchmark Agent from production —
   model-vs-human comparison is separate evaluation only, never part of the live system): Protocol &
   IPT · Search & Retrieval (Microsoft Graph + web crawl) · Deduplication · Title/Abstract Screener ·
   Full-Text Acquisition · Full-Text Eligibility · CMOC Extraction · Theory Synthesis & Refinement ·
   Contradiction · Reporting & Artifact. Each is mapped to a human role in Richmond's team.

3. **The central innovation — the Literature Knowledge Graph (LKG) of "big concepts".** Entities are
   *high-level thematic concepts* ("Low Knowledge Context", "Expertise Reversal Effect"), NOT granular
   terms. They are formed by a specific pipeline:
   - **seed-guided extraction** — the researcher provides seed examples of big concepts (from the IPT);
     the extractor uses them as few-shot to propose candidate entities;
   - **Leiden community detection** groups candidates;
   - **LLM community summarisation** — each community is summarised into ONE big-concept entity
     (name, type, description, members) — *this* is the step that turns fragments into big concepts;
   - **HITL iterative refinement** — the researcher merges/splits/renames; feedback updates the seeds;
     re-run 3–10× until it plateaus. CMOCs are then assembled from/expressed via these big concepts.

4. **GraphRAG queries the LKG DURING extraction** for consistency/disambiguation (e.g. "novice
   overload" → retrieve the "Low Knowledge Context" community so the new extraction is consistent).

5. **HITL feedback → few-shot → re-run loop at every checkpoint** (screening, CMOC validation, theory
   sign-off): human corrections are recycled as few-shot examples that refine the agent, which then
   RE-RUNS to modify the outcome before moving on. Continual/"lifelong" learning from the human.

6. **Reflexion / self-check + a separate Verifier agent** for quality; everything provenance-linked
   and RAMESES-auditable.

---

## 2. Honest gap analysis — our system vs. this vision

| Element the professor wants | Our system today | Verdict |
|---|---|---|
| Core-and-plugin, shared source of truth | Staged pipeline + PostgreSQL SoT (functionally equivalent, not literally LangGraph) | ✅ functionally; naming/framing to align |
| ~10 named agents mapped to Richmond roles | 8 agents; we ADD Verifier/Checker/Normaliser/Community; we LACK Search & Retrieval, Full-Text Acquisition, and a named Deduplication agent | ⚠ partial — reconcile the roster |
| Benchmark agent OUTSIDE production | verification harness is external | ✅ correct |
| Typed CMOC + span provenance | yes | ✅ |
| **Big concepts as the LKG substrate** (Leiden → **LLM community summary** → the entity) | we run Leiden and label communities, but as a *downstream* layer, not the substrate CMOCs are assembled from; summarisation is a short label, not the iterative big-concept builder | ⚠ have the pieces; not central or iterative as specified |
| **Seed-guided extraction** (few-shot from IPT big-concept seeds) | deliberately pristine/data-driven (we measured that a heavy IPT block *suppressed* yield) | ✗ diverges — must reconcile: implement as a LIGHT seed few-shot, not a dominating block |
| **GraphRAG query during extraction** (disambiguate against existing big concepts) | not implemented | ✗ missing |
| **HITL feedback → few-shot → re-run** | HITL records decisions but does NOT recycle them as few-shot and re-run the agent | ✗ missing — this is a signature mechanism he repeats in every document |
| Reflexion / self-check + Verifier | self-refine loop + verifier + independent checker | ✅ (added this iteration) |
| Modularity for other synthesis methods | core-and-plugin structurally supports it | ✅ structurally; state it explicitly |

**Bottom line:** our backbone matches, and on quality control (Reflexion/verifier, benchmark-outside)
we are aligned. But we are **missing three mechanisms the professor describes in detail and clearly
wants**: (1) big-concepts-as-substrate via Leiden **+ LLM community summarisation**, iterated with the
human; (2) **seed-guided extraction** (done lightly, reconciled with our yield finding); (3) the
**HITL feedback → few-shot → re-run** loop. Plus a **GraphRAG-in-extraction** disambiguation step and
a roster/naming alignment. I previously dismissed some of these as low-value — that was wrong; they are
in his design.

---

## 3. Plan (research-first, then build, then one clean run)

1. **Deep research** (web + NotebookLM/Chrome) on the exact mechanisms before coding: how leading
   systems implement seed-guided KG extraction, GraphRAG-in-the-loop, LLM community summarisation, and
   human-feedback-to-few-shot — to ground each implementation in real practice, not guesswork.
2. **Close the gaps**, reconciled with our empirical findings:
   - big-concept builder = Leiden → LLM community summary → HITL merge/split → iterate (extend the
     existing `community_analyst`);
   - light seed-guided extraction (few-shot seeds, not a heavy block);
   - GraphRAG disambiguation call inside extraction;
   - a real HITL feedback → few-shot store → agent re-run.
3. **Align the agent roster/naming** with the professor's ~10 (Search/Acquisition can be documented
   stubs for the given 28-paper benchmark).
4. **Validate each change on a 2–3 paper pilot** (cheap) before committing.
5. **One clean full run** when the system is genuinely ready → collect results from the real terminal
   output → assemble the preliminary submission.
