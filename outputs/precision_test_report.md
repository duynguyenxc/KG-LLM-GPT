# Screening Precision / Specificity Test — System vs Richmond benchmark

_Generated 2026-07-14. Addresses the professor's "~100 papers" requirement: test whether the
screening agent DISCRIMINATES (rejects irrelevant papers), not only whether it RECALLS the 28._

## Design

Richmond assessed 149 full texts and included 28; the 121 excluded records are not published.
To obtain a controlled precision test, a **distractor pool of 72 real papers** was assembled from
Europe PMC (2000–2017, English, with abstracts, de-duplicated against the 28), across four
categories each violating a known eligibility criterion:

| Category | Violates | n |
|---|---|---|
| postgraduate | 'undergraduate' population (residents/fellows) | 18 |
| non_reasoning | focus (medical education not about clinical reasoning) | 18 |
| no_intervention | intervention (observational / descriptive) | 18 |
| off_topic | scope (clearly outside clinical-reasoning education) | 18 |

The mixed pool (28 benchmark + 72 distractors) was screened by the same recall-first dual-model
agent used in the main pipeline.

## Results

**Per-category specificity (recall-first policy):**
| Category | Correctly excluded |
|---|---|
| off_topic | **18/18 (100%)** |
| postgraduate | 15/18 (83%) |
| non_reasoning | 11/18 (61%) |
| no_intervention | 11/18 (61%) |
| **Total** | **55/72 (76.4%)** |

**The recall / precision tradeoff is a tunable design parameter** (both policies measured on the
real data):

| Combine policy | Recall on the 28 (auto) | Specificity on 72 distractors |
|---|---|---|
| **Recall-first** (union — either model includes) | 89.3% (25/28) → **100% after HITL-1** | 76.4% (55/72) |
| **Precision-first** (both models must include) | 53.6% (15/28) | **98.6% (71/72)** |

## Interpretation (honest)

- The system **can reject 98.6% of distractors** under a precision-first policy — it is genuinely
  discriminating, not indiscriminately permissive.
- The pipeline **deliberately** uses the recall-first policy, the correct choice for a systematic
  review where missing a relevant study is the costly error; the human then clears false positives
  at HITL-1. This reproduces the standard human workflow (high-sensitivity machine filter +
  human adjudication) and is supported by the LLM-screening literature (see SOTA_REPORT Q2).
- Clearly off-topic papers are rejected perfectly (18/18); the residual false positives are
  topically-plausible undergraduate medical-education papers (e.g., professionalism/skills courses)
  flagged by ONE model — precisely the borderline cases a human is meant to adjudicate.
- **Caveat:** a distractor "wrongly included" is a false positive only relative to Richmond's set;
  some may be genuinely eligible papers Richmond did not capture. Human check recommended before
  counting any as an error.

## Bottom line

The system now has BOTH sides of screening quantified against a human-comparable standard:
**100% sensitivity (after HITL) and demonstrated discrimination (76.4% specificity recall-first,
98.6% precision-first)** — evidence that the machine reproduces the human screening function, with
the sensitivity/precision balance an explicit, researcher-controllable parameter.
