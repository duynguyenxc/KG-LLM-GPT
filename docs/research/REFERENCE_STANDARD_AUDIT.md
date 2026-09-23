# Audit of the historical 47-concept / 40-relation reference

## Result and authority

The historical reference requires explicit qualification before it can support a defensible recovery score. An assistant source audit now covers **all 47 concepts, 40 relations and five historical programme-theory chains** in `gold/richmond_gold.json`. The original reference is preserved byte-for-byte. This audit is not independent human ratification, a replacement gold standard, an annotation of all primary papers or an evaluation of the new semantic extractor.

Open `outputs/runs/reference-audit-20260923-v1/index.html`. Every entry preserves the original coding, a specific interpretation/revision proposal, source-page links and a blank human decision. `reference_audit.json` retains all records and hashes. The version-checked builder is `scripts/build_reference_audit.py`; it assembles explicit assistant-authored notes rather than algorithmically establishing scientific truth.

The primary basis is the supplied Richmond et al. (2020) paper, DOI 10.1111/medu.14137: Figure 2 (PDF p. 5 / journal p. 713), sections 3.2.1-3.2.3 (PDF p. 6 / p. 714), Figure 3 (PDF p. 7 / p. 715), sections 3.2.4-3.2.5 (PDF p. 8 / p. 716), and limitations/conclusions (PDF p. 9 / p. 717). Figures 2 and 3 were rendered and read visually, not inferred from their largely empty text extraction. The professor's July 24 instructions concerning 47 concepts, 40 relations and manual intervention were revisited. Those instructions establish the intended evaluation task, not proof that the repository already contains human judgments.

## Findings that change how evaluation should work

| Historical record | Source-based concern | Consequence for evaluation |
|---|---|---|
| E01 | The undergraduate medical/health-professions label defines population/scope, not one of the five explanatory learner contexts. | Compare population explicitly; do not score it as recovery of a context-specific explanation. |
| E19 | Multiple relevant resources is the low-knowledge summary box in Figure 2, expanded in Figure 3. | It cannot serve as a universal extra mechanism connecting every intervention to every response. |
| E21 | The high-knowledge sentence marks insight as Mresponse while also identifying diagnostic/management reasoning as O; the legacy phrase combines spans. | Split the compound or permit explicitly contextual roles; do not force an outcome-only label. |
| E43 | The mixed-knowledge feedback paragraph explicitly marks complete illness scripts as Mresponse; the old entity labels it Outcome. | Ratify the local role before penalizing a generated response label. A similar construct may occupy another role elsewhere. |
| R11 and R28 | Gratitude/understanding and building-on-knowledge/developing-understanding are described within experiences or as coordinated responses. Serial causality between the response labels is not explicit. | Ask reviewers whether to remove the serial arrow, retain co-responses, or label a justified inference. Do not reward an unsupported causal edge simply because the old file contains it. |
| R17 | Poor coping CONSTRAINS negative learning outcomes can read as preventing harm. Richmond describes a resource-mediated adverse pathway under poor coping. | Rewrite or explicitly define the predicate and preserve the encounter, responses and direction. Do not silently invert the outcome to make a match. |
| R37-R40 | The triples collapse resource-response-outcome paths into resource-to-outcome edges. | A matching intervention/outcome supports only path-summary correspondence unless the mediator is independently recovered. |
| PTS1-PTS5 | Slash-separated unions mix branches and sometimes transfer resources/responses between contexts. PTS2 starts with real/simulated cases instead of the high-knowledge discussion/analytical-only branches; PTS5 imports near-peer prompting from low knowledge. | These are not verbatim published chains. Preserve them as historical operationalizations, then use ratified conditional branches for explanatory recovery. |

The remaining concept notes preserve nuances that coarse normalization can erase: high/maintained versus improved accuracy, future versus immediate outcomes, stress under positive versus negative coping, absent/incorrect versus accurate feedback, and combined versus analytical-only instruction. Understanding, illness scripts and confidence cannot always receive a single universal role independent of the configuration.

All 40 historical relation records contain only an ID, subject, predicate and object, with no dedicated context/comparator/time/inference fields. This is a representation limitation, **not a finding that all 40 relations are false**. The audit associates each with its relevant contextual branch and flags the conditional, theory-building status. The descriptions are not 40 independent measured effects.

The exported proposal counts are 33 relations needing contextual/modality/inference qualifications, two needing reconsideration of serial causality, one with a polarity-ambiguous predicate, and four requiring the mediator to be restored or the target explicitly restricted to a path summary. These are mutually assigned editorial proposal categories, not an error rate, expert votes or a model-performance statistic.

## Coverage and denominator limits

The 47-concept inventory omits several distinctive Figure 3 resources and responses. Examples include the analytical scaffold, imposed time pressure, skipped-step expert explanation, difficult cases, erroneous passive peer explanation, perceived near-peer similarity/feeling at ease, clarity/affirmation and discordant illness scripts. Some broad existing labels overlap partially; the audit does not automatically add new codes or increase the denominator.

Consequently, recovery of all 47 labels or 40 triples would still not prove recovery of Richmond's complete explanation. Conversely, a defensible generated assertion absent from this inventory is not automatically false. Source-support precision must be assessed on generated assertions independently from reference recovery.

The 18-row configuration catalog remains provisional too. Its branch IDs provide navigation in this audit, not proof that the branches or a particular granularity have been ratified. The 47/40 track and configuration track must both remain visible; one cannot silently replace the other.

## Versioned scoring and human intervention

1. Keep the legacy reference and any historical scores unchanged and labelled with their original version.
2. Have independent reviewers examine the original paper and blank reference-ratification forms. If the aim is unaided agreement, withhold this assistant proposal report during initial coding. If reviewers use it, disclose that assistance; do not call their workflow unaided.
3. Adjudicate revisions with identity, date, source locator and reason. Freeze a new ratified reference with explicit additions/deletions/splits and version hashes. No such decisions have occurred yet.
4. Score the **same frozen system output** against old and revised references, if comparing the effect of reference repair. Differences then concern the evaluation target, not an improvement in the system.
5. To evaluate human intervention on system output, hold the reference version and rubric fixed; compare attributed pre/post system versions and record reviewer time. Changing both reference and output cannot isolate intervention benefit.
6. Keep source support, concept recovery, qualified relation correspondence and programme-theory correspondence separate. Mark post-benchmark changes as development; no held-out claim is justified here.

The paper supports an explanation of what may work, for whom and through which response. Verification therefore needs the full qualified explanation and its source support, not a maximum match count obtained by merging concepts or dropping inconvenient conditions.

## What was verified and what remains open

The exporter requires the exact original/reference/PDF hashes against which the notes were authored. Its output directory is new and immutable by default. Automated coverage checks verified all 92 distinct IDs, blank human decisions, valid page ranges and unchanged input hashes. Browser checks found all 92 records, exercised E43/R17 anchors, search and source links, and reported no severe console errors. The two example views were visually inspected. The QA record is `outputs/research_audit/reference-audit-20260923-qa.json`. No API was called.

Those checks establish coverage and inspectability of this assistant audit, not correctness agreed by human experts. Original supplements remain unavailable; this does not reproduce the authors' full extraction files. Production extraction/synthesis, their frozen prompts, historical submissions and human forms remain unchanged. The next offline implementation should use these distinctions in linked concept/relation evaluation and preserve unratified-reference status. Actual scoring of newly extracted assertions still requires the semantic pilot/full run and real human review.
