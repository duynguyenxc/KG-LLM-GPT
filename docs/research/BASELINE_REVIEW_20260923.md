# September 23 baseline: interpretation and review priorities

## Status and purpose

The source extraction/audit stage produced 180 findings from all 28 available-source records; 174 passed the machine gate. The frozen final synthesis contains nine provisional theory statements. These are generated outputs, not independently established scientific conclusions. Refer to `CURRENT_RUN_RESULTS.md` for terminal comparison/export status and costs.

The theory file SHA-256 is `d0489f641746eeb0389343e28c0db521e441e582ff98bf8fcfb1cb0ca81bdf7f`. The original is preserved in `outputs/runs/evidence-20260910-full/programme_theory.json`. Review observations below do not modify that file and are not human adjudication.

## What the nine generated statements cover

| ID | Subject of the machine-generated explanation |
|---|---|
| PT01 | Case-proximal diagnostic prompts versus abstract or delayed counter-bias instruction |
| PT02 | Early, concrete visual-diagnosis strategy instructions versus late or vague combined instructions |
| PT03 | External diagnostic schemas, task fit and limits of generalization |
| PT04 | Self-explanation/reflection, prior knowledge and immediate versus delayed transfer |
| PT05 | Error exposure and feedback sufficient to explain or repair mistakes |
| PT06 | Varied cases and virtual patients, separating observed learning from design rationale or popularity |
| PT07 | Repeated key-feature questions, feedback, time-on-task and item-specific retention |
| PT08 | Simulation/game responsibility, preparedness, stress, usability and expertise |
| PT09 | Governance, topic fit and uptake of virtual-patient/EHR resources |

These are primarily organized around instructional resources. Richmond organizes the final explanatory account around five overlapping learner contexts. A different organization is not automatically wrong, but the system must still recover or defensibly challenge the important conditional mechanisms. Neither the number of theories nor their fluent wording establishes this.

## Concrete interpretation issues found during assistant inspection

1. **PT02 study independence is not established as written.** Its limitations say that S004 and S005 are related study families and should not count as independent replication. The manifest supplies distinct family IDs, and the supplied methods describe different designs/sample sizes. Shared authors and ECG tasks alone do not establish shared participants. Verify recruitment/sample overlap before accepting this warning; do not silently merge the studies or call the statement human-validated. S013/S020, by contrast, are explicitly linked as a secondary analysis in the supplied record.
2. **PT05 title states necessity more strongly than its evidence establishes.** “Only when” implies a necessary condition across error-based learning. Its own limitations acknowledge that S018 did not directly compare detailed feedback/coaching against diagnosis-only feedback, and that the prior-knowledge threshold is unknown. The body presents a hypothesis; an expert should decide how narrowly the headline can be supported. This is a candidate overclaim, not a revised output.
3. **PT04's S026 delayed claim needs its exact comparator.** S026-F01 reports within-control-group improvement after self-explanation, not a randomized superiority contrast against no self-explanation. PT04 summarizes this as delayed improvement from self-explanation alone. A reviewer must retain the within-group design and consider testing/time effects before treating it as an intervention effect. S026-F04 separately supplies between-group far-transfer contrasts. Excluded S026-F02/F03 remain available for review; a machine exclusion is not an expert judgment.
4. **All nine direction fields are mixed.** This is understandable for broad summaries containing benefits and failures, but too coarse to function as an atomic relation label. Relation evaluation needs separate assertions preserving the specific context, comparator, outcome and time. A single mixed-direction theory must not be counted as both a recovered positive and a recovered negative relation without those links.
5. **The implementation admits synthesis after an automated source gate.** A gate checks individual findings, whereas synthesis can still introduce new unsupported connections or generalizations. Therefore the nine final theories need their own source-support assessment. Source linkage and a valid finding ID alone do not establish entailment.
6. **Four partial comparison rows overreach their selected-theory evidence.** RC04 cites S005-F01/S013-F02/S016-F03 outside PT01; RC05 cites S021-F01 outside PT01/PT03/PT08; RC12 cites S005-F04 outside PT01; RC11 selects no theory but cites S028-F01/F08. The baseline validator enforced selected-theory linkage for full equivalence only, leaving these partial assessments unflagged. An independent post-run check found them. The original comparison is preserved; inspection v4 visibly flags them. A corrected evaluation must distinguish source-finding correspondence from final-theory recovery instead of pooling those levels. The raw 14 partial/four not-recovered distribution must not be reported as a validated recovery score.

## A worked comparison, not a claimed human score

The provisional reference row RC01 operationalizes Richmond Figure 3's low-knowledge pathway involving near-peer examples with prompts, perceived similarity/feeling at ease, and improved learning or accuracy. The actual system counterpart PT04 discusses prompted resident examples and delayed transfer, with findings including S026-F04 and S025-F05. It does not establish the same perceived-similarity/at-ease mechanism. The saved AI comparator therefore marked RC01 **partial**.

This illustrates the required distinction: recovering an intervention and a favorable outcome is insufficient if the explanatory response is missing. The evaluator must also verify that the reference decomposition fairly represents Richmond and that the system's interpretation is supported by its primary sources. The AI label is an aid to inspection, not the human verdict or a measured accuracy rate.

## Prepared human work

- `outputs/runs/reference-review-20260923-v1/index.html`: ratify 47 concepts, 40 relations and 18 configurations against Richmond. These are project-coded reference units, not a dataset published by Richmond. Separate A/B/adjudication forms contain blank decisions.
- `outputs/runs/source-review-20260923-v1/index.html`: assess source support of every extracted finding and every frozen theory, with critic/eligibility/comparison verdicts withheld. Six forms cover findings/theories for A/B/adjudication. Review both machine-included and excluded findings to observe false acceptance and false exclusion.
- The baseline run's final `blind_review.html` and `human_review_coder_A/B.csv` support the separate configuration-correspondence task after reference ratification. The 47/40 system-scoring track remains additional work; reference ratification forms alone do not complete it.

Reviewers have not yet been appointed. No human cells are filled, no human agreement or precision is inferred, and no after-human-intervention improvement is claimed. Subsequent corrections must be attributed and stored in a new output version, preserving this pre-intervention baseline. Review packets should be completed independently before reviewers see AI verdicts or this assistant's issue list.

## Method implications

The baseline provides actual inspectable candidates and testable failure modes. The next implementation should preserve atomic semantic assertions separately from broad theory summaries, link each assertion to its supporting finding(s), and distinguish observations from cross-paper explanatory hypotheses. It must evaluate entity/relation recovery and source support separately from whole-configuration correspondence. Changes informed by these Richmond comparisons are development work, not held-out validation. The accepted proposal's unimplemented training, link-prediction and human-intervention components remain explicit in `REQUIREMENTS_AND_ACCEPTANCE.md`.
