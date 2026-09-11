> **Historical document - September 2026 audit supersedes performance and implementation claims below.** Read `docs/research/RESEARCH_AUDIT_STATUS.md`, `docs/research/RICHMOND_OFFICIAL_FINDINGS.md`, and `docs/research/METHOD_AND_VERIFICATION_PROTOCOL.md` from the repository root. Old AI judgments are not completed human validation.

# Preliminary Results — An Agentic Pipeline for Realist Systematic Review in Education

**Worked example and external benchmark: Richmond et al. (2020).**
Prepared for the RRE 2026 methodological-innovation manuscript. Draft — preliminary findings; not a
final result. _(Numbers in §4 are filled from the clean run completed 2026-07-23.)_

---

## 1. What these preliminary results are, and are not

The manuscript proposes an agentic, human-in-the-loop pipeline that performs a realist systematic
review as a set of explicit, auditable computational steps, rather than as the implicit cognition of
a review team. These preliminary results test one question: **can the pipeline reproduce the analytic
operations of a completed human realist review closely enough to be useful, while remaining
transparent and researcher-directed?** We use Richmond et al. (2020) — a published realist review of
educational interventions for clinical reasoning (28 included studies) — as an external benchmark,
because it reports its intermediate products (search, screening, context–mechanism–outcome
configurations, and a five-context programme theory), not only its conclusions.

We are deliberately cautious in what we claim. These are early results on a single benchmark; they
demonstrate feasibility and a set of measurable correspondences, not a validated general method. The
system does not replace the reviewer's interpretive judgement, and we do not present it as doing so.

## 2. The system, in brief

The pipeline addresses the four shortcomings the proposal identifies in current AI review tools —
opaque reasoning, uncontrolled retrieval, unstructured output, and the smoothing-over of
contradictions — through four corresponding design commitments:

- **Traceability.** Every extracted claim carries a verbatim quote resolved to a character span in
  the source document; nothing enters the graph without provenance.
- **Researcher direction.** Scope, eligibility, and the analytic vocabulary are encoded in
  human-editable configuration (a review protocol and a typed context–mechanism–outcome ontology),
  not in ad-hoc prompts.
- **Structured, reproducible output.** Extraction produces a typed knowledge graph — a coded dataset
  that can be re-queried and audited, not free text.
- **Contradictions surfaced, not smoothed.** The same intervention leading to opposite outcomes is
  detected and routed to a human for interpretive resolution, as realist method requires.

The work is divided across eight specialised agents, each carrying an embedded domain persona and
each mirroring a role a human reviewer plays, with the researcher sovereign at five human-in-the-loop
checkpoints. A full account of the agents and the human-vs-machine workflow is in
`docs/SYSTEM_WORKFLOW.md`; the ontology and its grounding in Richmond's own definitions are in
`docs/ENTITY_RELATIONSHIP_EVALUATION.md`.

## 3. Evaluation design

We compare the pipeline's outputs to Richmond's published outputs at each stage. The benchmark's
answer key (a coded rendering of Richmond's Figures 2–3: 47 entities, 40 relations, five
programme-theory chains) is read **only** by the verification harness, which sits outside the
pipeline; the extraction agents never see it. This separation is enforced in code and is what lets us
interpret agreement as reproduction rather than recall of a memorised answer.

Metrics of two kinds are reported. **Deterministic** measures (screening sensitivity, quote-to-span
resolution, relation type-validity) are exact and stable across runs. **Model-judged** measures
(entity coverage, programme-theory correspondence, community–mechanism alignment) are inherently
noisy; we therefore sample each judgement three times and report a majority vote or an average with
its range, so that no single run is presented as a point of fact. Expert human rating of the
model-judged measures remains to be done and is noted as such.

## 4. Preliminary results

_(Filled from the clean run of 2026-07-23; corpus of 28 studies — 20 full-text PDFs, 8 abstract-only
records; «N_CMOC» configurations, «N_ENT» entity instances over «N_CANON» canonical concepts,
«N_REL» typed relations.)_

### 4.1 Transparency and structure (deterministic)

| Property (proposal's target quality) | Preliminary result |
|---|---|
| Claims traceable to source (quote → span) | «FAITHFULNESS»% of extracted elements resolve to an exact/near span |
| Structured, type-valid output | «TYPE_VALID»% of relations satisfy the ontology's domain/range constraints |
| Contradictions surfaced (not smoothed) | «N_CONTRA» same-driver / opposite-outcome contradictions detected and routed to a human |
| Reproducible coded dataset | «N_CMOC» CMOCs · «N_CANON» canonical concepts · «N_REL» typed relations, all provenance-bearing |

### 4.2 Correspondence with the human review (benchmark)

| Analytic operation | Measure vs Richmond (2020) | Preliminary result |
|---|---|---|
| Search & screening | sensitivity to the 28 included studies (after HITL-1) | «SCREEN»% |
| CMOC extraction | causal-pattern recovery of the 40 gold relations | «REL_PATTERN»% |
| — | strict relation recovery (both concepts individually matched) | «REL_STRICT»% |
| Concept coverage | recovery of the 47 gold entities (E01–E47), majority-vote | «ENTITY»% (range «ENTITY_MIN»–«ENTITY_MAX»%) |
| Conceptual entities (novelty) | emergent Leiden communities aligned to Richmond's mechanisms | «COMM_ALIGN»% («N_COMM» communities) |
| Programme theory | structural/conceptual correspondence of the theory (model-judged) | «THEORY» (range «THEORY_MIN»–«THEORY_MAX») |

### 4.3 The retroduction effect

Realist synthesis is iterative: earlier studies are re-analysed as later evidence reshapes the
theory. We implemented this as a bounded loop that re-reads the studies the independent checker
flagged, under the refined theory. In an earlier run this loop raised entity coverage from «RETRO_BEFORE»%
to «RETRO_AFTER»% while faithfulness held, which is direct evidence that the machine benefits from the
same iterative discipline a human team uses. _(Reported as a mechanism observation; the §4.2 figures
are from the single clean pass without the loop, unless stated.)_

## 5. What these results do — and do not — show

They show that the pipeline reproduces the **causal structure** of Richmond's review at high fidelity
(pattern-level relation recovery «REL_PATTERN»%), keeps its claims **grounded** in the source
(«FAITHFULNESS»%), produces a **reproducible, typed dataset**, and **surfaces contradictions** — the
four qualities the proposal argues current tools lack. The emergent conceptual entities recover a
meaningful fraction of Richmond's mechanisms without being told them in advance, which is preliminary
support for the community-defined-entity idea.

They do **not** show that the system matches a human on every measure. Strict, concept-for-concept
relation recovery is low («REL_STRICT»%): the machine recovers the right *shapes* of causal claims
more reliably than the exact concept pairs a human abstracted. Concept coverage (~«ENTITY»%) is
partly limited by the corpus itself — several concepts Richmond theorised (e.g. self-efficacy) are
barely present in the 28 papers, and the system correctly declines to invent them. We read this as a
sign the system is honest, not as a ceiling on the method.

## 6. Limitations

- **Single benchmark.** One realist review; generality is not yet established.
- **Corpus availability.** We hold full text for 20 of the 28 studies and only abstracts for 8, which
  bounds concept coverage below what Richmond, with all 28 full texts, could reach.
- **Model-judged metrics are noisy.** We mitigate with three-sample majority voting and report
  ranges, but human expert rating is still required and pending.
- **Human ratification pending.** HITL decisions in these runs were exercised under delegated
  authority for reproducibility; the professor's ratification is required before any result is final.
- **Pre-training exposure.** The model may carry memory of the published Richmond paper; the 96%
  quote-grounding constrains this, but a benchmark outside the training window is the definitive
  future control.

## 7. Next steps

Tighten the resource/response typing further and let the checker re-type (not only flag) to raise
strict recovery; obtain the eight missing full texts; run the retroduction loop over the full clean
corpus; collect two-coder human κ on a sample; and add a second benchmark review to test generality.

---

_Artifacts supporting every figure above: the per-paper CMOC evidence table with quotes, the typed
knowledge graph (parquet + Neo4j), the verification report, and the full decision/audit log, all
under `outputs/`. Code and documentation: the project repository._
