# The System's Reasoning, Algorithm, and Architecture — with an honest audit

_What our core algorithm actually is, how the reasoning is organised, how it compares to the current
state of the art in agentic literature review, what we borrowed, and where it is still shallow. Written
so a reviewer can judge whether the machine "thinks" like an expert reviewer or merely runs steps._

---

## 1. The core algorithm, in one page

The pipeline is a **typed, provenance-first, human-supervised realist-synthesis algorithm**. Its unit
of reasoning is the **CMOC** (Context → Mechanism[resource → response] → Outcome), and its invariant is
that *no claim exists without a verbatim quote resolved to a source span*.

```
INPUT: a corpus of documents D, a review protocol P, a typed ontology O (5 entity + 5 relation types)

1  INGEST      for each d in D: text → provenance-bearing units u(char offsets)
2  SEED THEORY IPT ← hypotheses from public learning theory (never the benchmark's answers)   [HITL-0]
3  SCREEN      for each d: two independent models vote include/exclude on THEORY-RELEVANCE
               keep = union of includes; disagreements → human                                [HITL-1]
4  EXTRACT     for each included d:
   4a draft    CMOCs(d) ← LLM(d, O)                          # typed, quote-per-element
   4b reflect  issues ← Checker(draft)                       # independent 2nd model family
   4c revise   if issues: CMOCs(d) ← LLM(d, draft, issues)   # SELF-REFINE (new)
   4d verify   for each cmoc: support ← Verifier(cmoc)       # cross-critique score
   4e ground   resolve each quote → exact/near span; else FLAG (never fabricate)
   4f validate keep relation iff type(subject)×type(object) ∈ domain/range(predicate)
   4g check    Checker signs off / flags residuals → human                                    [HITL-2]
5  NORMALISE   cluster synonymous labels → canonical concepts → Richmond-granularity families
6  COMMUNITIES Leiden partition of the CMOC graph → emergent conceptual entities
7  SYNTHESISE  demi-regularities = CMOC motifs in ≥2 studies (pure graph query)
               contradictions   = same driver, opposite outcome → human                       [HITL-3]
8  THEORISE    programme theory ← LLM(demi-regularities, contradictions, communities, IPT)     [HITL-4]
9  RETRODUCE   re-read the weakest studies under the refined theory; repeat 4–8 until stable
OUTPUT: a typed knowledge graph + a five-context programme theory, every edge quote-grounded
EVALUATE (outside the loop): compare to the human benchmark; the answer key is never read by 1–9
```

**Why this shape.** Steps 5–7 are deliberately *deterministic graph/SQL operations, not LLM calls* —
so demi-regularities and contradictions are reproducible and auditable, and the LLM's judgement is
confined to where interpretation genuinely belongs (extraction, community labelling, theory prose).
This is the opposite of an "ask-the-LLM-everything" design and is what makes the output traceable.

## 2. Architecture

- **Orchestration:** a staged pipeline over a shared typed state; one stage's output is the next's input.
- **Agents (8):** IPT Manager · Screening Reviewers (×2, different families) · CMOC Extractor ·
  Faithfulness Verifier · Consistency Checker (different family) · Normaliser · Community Analyst ·
  Synthesis Composer. Each carries an embedded expert persona (`config/agents.yaml`). See
  `docs/SYSTEM_WORKFLOW.md`.
- **Data layer:** PostgreSQL = single source of truth; parquet LKG = canonical reproducible artifact;
  Neo4j = derived exploration. Every triple: `{study, unit, char span, quote, model, prompt version,
  confidence}`.
- **Human:** sovereign at five checkpoints (HITL-0…4).

## 3. Reasoning audit — vs the state of the art

We compared our reasoning to current agentic-review systems and adopted what fits.

| SOTA technique (source) | What it gives | In our system? |
|---|---|---|
| **Self-Refine / Reflexion** (Madaan 2023; Shinn 2023) — draft → self-critique → revise | fewer errors without retraining | **Adopted** (step 4a–4c): the Checker critiques the draft and the extractor revises *before* persisting — previously it only flagged for the human. |
| **Independent 2nd reviewer / different model family** (JAMIA cross-critique) | reduces shared blind spots | **Yes** — Checker is gpt-5.4 vs extractor gpt-5.5. |
| **Multi-agent debate** (Du 2023; many 2025) — agents argue to a better answer | higher factual accuracy | **Partial** — our critique→revise is one round of structured disagreement, not full multi-round debate. Multi-round is a candidate upgrade. |
| **Evidence-gather-then-answer** (PaperQA2, FutureHouse) — retrieve + relevance-score evidence before answering | superhuman citation precision | **Not yet** — the extractor reads the whole paper at once. A gather-score-then-extract front-end is a candidate upgrade. |
| **GraphRAG retrieval for synthesis** (Microsoft) | reasoning over connected evidence | **Partial** — synthesis reasons over the typed graph via SQL motifs + communities, but the theory composer is fed a JSON evidence pack, not retrieved subgraphs. |
| **Role-play + reasoning transparency** (LatteReview) | auditable per-agent rationale | **Yes** — personas + per-agent audit-log rationale. |

**Honest verdict on optimality.** The *structure* is sound and, for a realist review specifically,
arguably better-suited than a generic RAG-QA system: it keeps C/M/O typed and quote-grounded, it
surfaces contradictions instead of averaging them, and it now self-corrects. It is **not yet optimal**
in reasoning depth: the debate is single-round, there is no evidence-relevance front-end, and synthesis
does not do true GraphRAG subgraph retrieval. These are the next reasoning upgrades, in priority order.

## 4. What changed this iteration (grounded, not guessed)

1. **Self-Refine reflection loop** (step 4a–4c) — the biggest reasoning change: the independent
   reviewer's critique now *improves* each paper's coding before it is stored, mirroring how Richmond's
   second reviewer's feedback led the lead coder to revise (§2.2, L248-250) — and matching the
   Reflexion/Self-Refine result that self-correction beats one-shot.
2. **Sharper Resource/Response/Context boundary rule** — fixes the most-mistyped realist distinction
   (a supplied *thing* vs an internal *reaction* vs a pre-existing *condition*).

## 5. The next reasoning upgrades (ranked)

1. **Evidence-gather front-end** (PaperQA2-style): for each candidate configuration, retrieve and
   relevance-score the supporting passages before committing — should raise strict recovery and cut
   over-claims.
2. **Multi-round debate** on the hardest CMOCs (extractor vs checker, 2–3 turns) instead of one revise.
3. **GraphRAG retrieval in the theory composer**: feed retrieved subgraphs + community reports, not a
   flat JSON pack, so the theory is reasoned from connected evidence paths.

Sources consulted: Madaan et al., *Self-Refine* (2023); Shinn et al., *Reflexion* (2023); Du et al.,
*multi-agent debate* (2023); Rostam & Kojima, *LatteReview* (2025, arXiv:2501.05468); FutureHouse,
*PaperQA2* (2024); Hong et al., *MetaGPT* (ICLR 2024); Edge et al., *GraphRAG* (2024).
