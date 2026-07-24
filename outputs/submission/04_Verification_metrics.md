# Verification Report — System vs Richmond et al. (2020)

External benchmark evaluation (separate from the production pipeline).

## 1. Screening (title/abstract)
- Gold includes: 28
- Auto-include sensitivity: **92.9%** (26/28)
- False excludes: **0** 
- Uncertain → HITL-1: 2 ['S018', 'S028']
- Final sensitivity after HITL-1: **100.0%**

## 2. Entity coverage (47 gold entities E01–E47)
- Recall: **91.5%** (43/47) — LLM-judged semantic matching (human audit required before publication)

## 3. Relation coverage (40 gold relations R01–R40)
- Strict recall (exact concept match on both endpoints): **0.0%** (0/40)
- Type-level recall (causal pattern recovered — predicate + endpoint types): **97.5%** (39/40)
- Missed (strict): R01, R02, R03, R04, R05, R06, R07, R08, R09, R10, R11, R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23, R24, R25, R26, R27, R28, R29, R30, R31, R32, R33, R34, R35, R36, R37, R38, R39, R40

## 4. Citation faithfulness (automated, exact)
- 501/517 extracted elements have verbatim quotes resolved to exact character spans: **96.9%**

## 5. Programme-theory correspondence (5 gold PTS chains)
- Mean correspondence: **0.54** (model-based, averaged over samples (human rating required before publication))

| PTS | Score | Rationale |
|---|---|---|
| PTS1 | 0.89 | Strong correspondence. The SYSTEM theory has a closely matching low-knowledge/novice context and describes explicit expert-reasoning visibil |
| PTS2 | 0.50 | Partial correspondence. The SYSTEM theory includes case exposure, simulation/virtual/realistic cases, repeated varied cases, feedback, build |
| PTS3 | 0.32 | Low-to-moderate correspondence. The SYSTEM theory contains some related positive affective and engagement outcomes, especially in bounded si |
| PTS4 | 0.59 | Moderate correspondence. The SYSTEM theory clearly includes negative pathways involving thin/absent guidance or feedback, excessive complexi |
| PTS5 | 0.39 | Partial but limited correspondence. The SYSTEM theory includes expert-reasoning visibility, modelling, prompts, comparison with one's own id |