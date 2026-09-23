# Frozen-theory correspondence evaluation v2

## Reason for a new evaluation

The September 23 baseline's four partial rows RC04/RC05/RC11/RC12 use findings outside the selected theory, including one row selecting no theory. The first validator applied evidence-link checks only to full equivalence. V2 evaluates the same frozen production result under a stricter, explicit theory-level contract. It does not alter the original 180 findings, nine theories, reference, or earlier comparison responses.

This protocol is development work informed by observed benchmark/evaluator behavior. A change in labels is an evaluation-method change, not improvement in the production system and not held-out validation. The 18-branch task remains separate from concept/relation recovery and source-support assessment.

## Pre-execution specification

Run `res_pipeline.evidence.evaluation` against `outputs/runs/evidence-20260910-full`, writing a sibling `outputs/runs/evaluation-20260923-v2`. Evaluate all 18 reference rows, not only the four known problem rows. Use the existing pinned comparator model and pricing configuration. The budget includes this evaluation, the source run, its unresolved reservations and the separate pilot; the existing USD 50 ceiling is retained. Prior AI comparison labels and source-critic verdicts are not sent in new requests.

For each reference, the model sees the complete frozen programme theory and the scientific content of findings linked to those theories. It must select actual theory IDs and supporting findings already linked to those selected theories. Findings unrelated to the selected theories cannot count as theory recovery. It assesses context, resource, response, outcome, direction and qualifiers once each. Each equivalent/partial dimension must include a verbatim anchor to a named string field of a selected theory.

An equivalent, partial or contradictory verdict requires a selected theory and linked evidence. Equivalent also requires all six dimensions equivalent. Partial requires substantive dimensional correspondence. Not recovered means no selected counterpart and no claimed equivalent/partial dimensions; uncertainty is recorded separately. A broad theory with mixed outcomes may contain a matching conditional branch, so the evaluator must inspect that branch instead of comparing only the overall direction field. An additional defensible qualifier is not automatically a contradiction.

The validator rejects unknown/duplicate IDs, findings outside selected theories, missing/duplicate dimensions, inconsistent verdict prerequisites and unmatched/misassigned quotation anchors. Failed rows are **quarantined**, preserving the raw scientific verdict; no automatic relabelling, score imputation or silent prompt retry is performed. Successful admission means only that these scope/location checks passed. A model could cite an exact but semantically irrelevant passage, so admission is not entailment or human verification.

## Outputs and audit

The separate directory preserves exact request/response/parsed records, token usage, actual model identities, configuration, code/prompt/input hashes, row admission reasons, JSON/CSV comparison records and a readable HTML matrix. Source files are hashed again after evaluation to detect mutation. The HTML links every theory anchor and supporting finding back to the frozen baseline report. Original evaluator labels may be displayed for audit but are not model inputs.

Independent reviewers still need to ratify the Richmond operational reference, judge source support and assess conditional correspondence. Their existing forms remain blank. The evaluation run does not authorize or impersonate human approval. Structural test fixtures cover the observed outside-theory partial-match failure and absent-theory partial verdict, false quote anchors, invalid no-counterpart matches and admissible control cases; these tests do not establish scientific validity.
