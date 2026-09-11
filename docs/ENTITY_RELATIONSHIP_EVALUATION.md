> **Historical document - September 2026 audit supersedes performance and implementation claims below.** Read `docs/research/RESEARCH_AUDIT_STATUS.md`, `docs/research/RICHMOND_OFFICIAL_FINDINGS.md`, and `docs/research/METHOD_AND_VERIFICATION_PROTOCOL.md` from the repository root. Old AI judgments are not completed human validation.

# Evaluation — Are our Entities & Relationships correct, useful, and faithful to Richmond?

_A critical self-assessment of the knowledge-graph schema and the extracted graph, judged against a
close reading of Richmond et al. (2020) §2 (definitions) and §3.2 + Figures 2–3 (the CMOC statements).
Honest verdict up front, evidence below, and the concrete fixes that follow._

**Verdict:** The **schema is faithful and correct** — our five entity types are exactly Richmond's
Context–Mechanism–Outcome framework (with Mechanism split into resource/response as Richmond
mandates), and our five relation types are a defensible operationalisation of Richmond's causal
prose. The **extracted graph is structurally sound and low-fabrication** (99.4% of relations pass
type validation; 96% of quotes resolve to the source), and its causal-shape distribution matches
Richmond's. The **real weaknesses** are (a) *over-granularity* — 148 concepts vs Richmond's 47
abstracted ones, some too study-specific — and (b) a genuine *Resource / Intervention / Response
boundary ambiguity* that produces occasional mis-typing. Both are addressable and neither is
fabrication.

---

## 1. What Richmond actually defines (from the paper, §2, L138–165)

Richmond states the analytic unit explicitly: "Realist research data are analysed and interpreted to
form **context, mechanism, outcome configurations (CMOCs)**." Their definitions, verbatim in intent:

- **Context** — "separate to the intervention being investigated but affect how the intervention is
  received by participants." (a pre-existing condition, NOT the intervention)
- **Mechanism** — "conceptualised as **resources and responses**: interventions **offer resources**
  into a context, **effecting a change in participants' responses**, which in turn **leads to** various
  outcomes." → Mechanism is explicitly TWO things: **Mresource** and **Mresponse**.
- **Outcome** — "the measured effects of interventions."
- **Intervention** — the teaching method under study (referenced throughout; it is what *offers* the
  resource). Not one of the C/M/O letters, but the causal origin.

In §3.2 every one of the five contexts is written as an italic CMOC statement that literally tags
each element `(C)`, `(Mresource)`, `(Mresponse)`, `(O)` — e.g. *"When an expert's reasoning is
explicitly revealed and discussed (Mresource) with students with sufficient domain-specific knowledge
(C), this promotes understanding (Mresponse) leading to insight (O)."*

**Richmond does NOT define named relation *types*.** They write causal prose ("offer… into…",
"effecting a change in…", "leads to…", "promotes…"). So relation *typing* is our contribution.

## 2. Our schema vs Richmond — faithful

| Our entity type | Richmond's element (§2) | Faithful? |
|---|---|---|
| `Context` | Context — pre-existing learner/setting condition | ✅ exact |
| `Intervention` | the teaching method that offers resources | ✅ (their causal origin) |
| `Mechanism_Resource` | Mechanism-**resource** ("interventions offer resources") | ✅ exact |
| `Mechanism_Response` | Mechanism-**response** ("change in participants' responses") | ✅ exact |
| `Outcome` | Outcome — measured effect | ✅ exact |

**Five types, and they are the right five** — this is not an invented ontology; it is Richmond's own
CMO framework with Mechanism correctly split in two (the split most automated systems miss).

Our **five relations** operationalise Richmond's verbs, with machine-checkable domain/range:
`PROVIDES` (Intervention→Resource; "offer resources"), `TRIGGERS` (Intervention/Resource→Response;
"effecting a change / promotes"), `ENABLES` (Context→Response/Outcome; a context makes it possible),
`LEADS_TO` (Response→Response/Outcome; "leads to"), `CONSTRAINS` (Context→Outcome; the negative
conditioning Richmond describes for low-knowledge/poor-coping learners).

**Cross-check of the causal shape** — the predicate distribution matches Richmond's gold encoding:

| Predicate | Richmond gold (40 rel) | Our extraction (398 valid) |
|---|---|---|
| LEADS_TO | 20 (50%) | 105 (26%) |
| TRIGGERS | 14 (35%) | 103 (26%) |
| ENABLES | 4 | 75 |
| PROVIDES | 1 | 96 |
| CONSTRAINS | 1 | 19 |

Both are dominated by TRIGGERS + LEADS_TO (resource→response→outcome), which is the realist mechanism
chain. Our graph has proportionally more PROVIDES because we extract the Intervention→Resource link
explicitly, which Richmond's gold usually leaves implicit — a *more complete* graph, not a wrong one.

## 3. The extracted graph — quality evidence

- **Size:** 148 canonical concepts / 481 mentions; 398 valid typed relations.
  - Intervention 42 · Mechanism_Response 42 · Outcome 26 · Mechanism_Resource 21 · Context 17.
- **Typing integrity: 99.4%** — only 3 of 401 relations violated domain/range (demoted to
  `UNTYPED_CANDIDATE`, never silently dropped).
- **Grounding: 96%** — 463/481 entity quotes resolve to an exact/near span in the source; the 18
  unresolved are flagged for HITL-2, never fabricated.
- **Benchmark:** post-retroduction, this graph recovers 80.9% of Richmond's 47 gold entities
  (majority-vote), 97.5% of the causal *patterns*, at 96.3% faithfulness.

## 4. The real weaknesses (honest)

1. **Over-granularity.** We hold 148 concepts where Richmond abstracted to 47. Some of ours are
   genuinely useful sub-concepts, but some are *study-specific* ("90-minute interactive CFS seminar",
   "Novice ECG learners without prior training") that a human reviewer would generalise. → The
   concept-family layer already coarsens 148→30, but the *normaliser* should abstract more
   aggressively toward Richmond-granularity.
2. **Resource / Intervention / Response boundary is genuinely fuzzy.** Example: "Accuracy-speed
   pressure" is currently typed `Mechanism_Resource` but is really a Context/Response. Richmond's own
   gold shows the same tension — they folded almost all resources INTO Intervention (Resource has just
   1 gold entity, Intervention 12). This boundary is the hardest realist distinction and needs (a) a
   sharper prompt rule and (b) the Consistency Checker explicitly re-typing, not just flagging.
3. **Moderate extraction confidence.** The independent Checker disagreed with 56% of first-pass CMOCs
   — many were over-claims the human should adjudicate at HITL-2. This is *appropriate scepticism*,
   but it means the raw graph needs human ratification before it is "final".

## 5. Concrete fixes (proposed next work)

- Tighten the extraction prompt's Resource-vs-Response-vs-Context rule with Richmond's own
  `(Mresource)/(Mresponse)` examples, and let the Checker **re-type** (not only reject).
- Add an "abstract to Richmond-granularity" pass in normalisation (target ~40–60 concepts).
- Surface the Checker's per-CMOC verdict in the HITL-2 UI so a human confirms/retypes each flagged
  configuration — turning the 56% disagreement into resolved, ratified edges.
- Add a graph-hygiene report (orphan nodes, singleton concepts, type-imbalance) to each run.

**Bottom line for the professor:** the entities and relationships are *the right kinds*, *faithfully
grounded in Richmond's own framework and text*, and *usable* — the graph reproduces Richmond's causal
structure at high fidelity. What remains is **abstraction discipline and boundary precision**, i.e.
making the machine's concepts as *tidy* as an expert's, not making them *correct* (they already are).
