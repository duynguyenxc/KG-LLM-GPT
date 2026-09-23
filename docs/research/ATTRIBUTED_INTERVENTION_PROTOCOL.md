# Attributed revisions and before/after evaluation

## Current implementation and actual state

The July 24 meeting requests manual intervention and results before/after that intervention. The accepted proposal additionally discusses human feedback, active learning and RLHF. These are related but different interventions. The present module implements **versioned editing of synthesis output**, not model training, RLHF, prompt learning or automatic changes to the extraction graph.

`src/res_pipeline/evidence/interventions.py` now prepares an empty attributed revision ledger and can apply genuinely supplied changes to a new sibling run. Open `outputs/runs/intervention-preparation-20260923-v2/index.html` for the nine actual baseline theories and the empty ledger/schema/hash files. Status is **prepared_no_intervention**, with **zero recorded changes**. There is no revised research synthesis, human intervention benefit or human validation to report. V1 preserves the initial preparation view; V2 presents fields as readable text rather than requiring JSON inspection.

The old `plugins/realist/guidance.py` can store wrong/correct/note text and replay it in a prompt. Its current storage fields do not by themselves establish the editor's identity, exact old output, independent approval or measured before/after benefit. That mechanism is not being relabelled RLHF and is not used to inject Richmond-derived corrections into this frozen production run.

## What is recorded

Each actual change needs an edit ID; replace/add/withdraw action; theory ID; exact old-record hash for an existing theory; a complete replacement when applicable; reason; existing finding IDs used as the basis; a source locator/explanation; and attribution. Attribution distinguishes human, human_with_ai_assistance and ai_assistant, with identity, timezone-aware date/time, finite nonnegative minutes and assistance disclosure.

Record time spent on each edit without repeating a whole-session duration for every row. A name and timestamp are an attribution claim, not independent authentication. AI-authored edits must remain labelled as AI work. If the assistant translates a human's prose correction into structured data, preserve the original human correction, disclose the translation/assistance and have the contributor check that the structured edit expresses their decision. Do not invent a reviewer to fill an empty field.

Supported actions are:

- **Replace:** revise a theory while retaining its stable ID and its full previous record in the event log.
- **Add:** create a new theory ID with no old-record hash and links to existing findings.
- **Withdraw:** remove a theory from the active revised synthesis, retaining its entire old record and reason in history.
- **Split/merge:** use explicit withdrawal(s) and addition(s), with unique IDs and reasons. Do not hide a structural change inside an unexplained rename.
- **Summary revision:** change the overview/unanswered questions in a separately attributed edit. Otherwise the inherited summary is explicitly flagged for review after theory changes.

This scoped module does not edit source findings, quotations, entity definitions, canonical merges or the reference standard. If an underlying finding is wrong or missing, correct it in a separate identifiable source-level experiment and revalidate affected synthesis. An output-edit ledger cannot silently turn new source observations into old extraction evidence.

## Structural and provenance checks

Before any new revision directory is written, the importer checks the full parent/source/reference/configuration hashes, schema, old-record hashes, unique edit/target IDs, attribution and known evidence IDs. It rejects empty ledgers, no-op changes, competing edits to the same theory, invalid dates/times, unknown evidence, stale references and overwriting the original directory. A new theory must have nonempty scientific fields and unique existing finding links.

Application retains byte-identical source pages, corpus manifest, findings and reference snapshot. It saves the exact submission, original theory file, individual before/after events, revised theory, configuration lineage and implementation snapshots. The readable report shows before/after fields and highlights changes. A final input-identity check detects a parent changing during application; such a result is marked invalid rather than usable.

Structural validity does not prove that an edit is supported by the source. All revised theories retain `human_approval: null`, and the run records source-support revalidation and comparison as pending. The actor may be a human author without the resulting theory having independent human validation. The stored intervention-effect field remains null. No API call occurs in preparation or application.

## How to evaluate a real intervention

1. **Freeze the before state.** Preserve source corpus, initial output, reference version, scoring rubric and evaluator configuration. Record the actual evidence restrictions and missing texts.
2. **Record the intervention.** Retain every addition, withdrawal or changed claim, its basis, actor and time. Do not silently revise the reference to accommodate an edited answer. The historical 47/40 reference still needs ratification; the same applies to the 18-branch decomposition.
3. **Recheck source support.** Review the changed claims and any dependent explanations, including comparator, time, direction and inference status. A narrower title may be more defensible even without increasing reference recovery; such improvements should be described explicitly.
4. **Compare like with like.** Evaluate frozen before/after versions against the same ratified reference and rubric. If evaluation v2 replaces the flawed baseline comparator, rerun both versions under v2; an old-v1/new-v2 score difference confounds output change with evaluator change.
5. **Keep evaluation independent where feasible.** Reviewers assessing outcome quality should not simply endorse their own edits. Use blinded/randomized presentation and preserve the independence/assistance record. Blinded paired-intervention evaluation has not yet been executed or implemented as an automatic randomization experiment.
6. **Report change with its denominator.** For a fixed ratified reference of N eligible claims, a simple strict recovery difference is `(equivalent_after - equivalent_before) / N`. Report partial, contradictory, uncertain and reference-problem decisions separately, together with source-support results and editor time. Do not reinterpret this quantity as NER F1, independent-study replication, causal superiority or proof of human-equivalent reasoning.

A before/after output comparison can document what a specified intervention changed on this worked example. It does not by itself establish general effectiveness of the agent architecture. Reference repair must be analysed separately, holding the system output fixed. Full effectiveness claims still need controlled variants, suitable human evaluation and explicit development versus held-out status.

## Commands and output contract

To prepare another empty packet, choose a new directory:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
& 'C:/Users/Admin/AppData/Local/Programs/Python/Python311/python.exe' -B -m res_pipeline.evidence.interventions --source-run outputs/runs/evidence-20260910-full --output-dir outputs/runs/intervention-preparation-NEW
```

The actual prepared `revision_submission.json` contains frozen `parent_input_sha256`, an empty `edits` array and null `summary_edit`. Fill only with actual attributed contributions according to `submission_schema.json`; parent theory records and hashes are provided for accurate editing. An empty ledger will be rejected as an intervention.

After a real submission exists, apply it to a new sibling run:

```powershell
& 'C:/Users/Admin/AppData/Local/Programs/Python/Python311/python.exe' -B -m res_pipeline.evidence.interventions --source-run outputs/runs/evidence-20260910-full --submission PATH_TO_ACTUAL_COMPLETED_SUBMISSION.json --output-dir outputs/runs/attributed-revision-NEW
```

Outputs include `parent_programme_theory.json`, `programme_theory.json`, `revision_submission.json`, `revision_events.json`, unchanged source/reference files, `code_snapshot/`, `run_status.json` and readable `index.html`. The revised schema is compatible with the source-support and separate scoped-evaluation interfaces. That compatibility has not been demonstrated on a real human-revised research result because none exists. Source support and paired comparison still need to run separately.

## Verification completed

The repository suite reached **66 passing tests**, including ten new synthetic intervention cases: empty preparation, exact parent preservation, AI attribution retained, stale record/reference, unknown evidence, duplicate targets, no-op edits, timezone requirement, split/withdraw history and overwrite prevention. The existing pytest asyncio-configuration warning remains. Targeted Ruff F/I checks pass.

Browser checks exercised the nine real preparation records and PT01's original report link, plus a clearly synthetic before/after example. The readable field display, changed-field highlighting and pending-validation statements were inspected; no severe browser errors occurred. The synthetic examples remain under `tmp/intervention-ui-qa*`, not in research result runs. `outputs/research_audit/intervention-preparation-20260923-v2-qa.json` records the final UI/provenance checks. Baseline/source/reference hashes remain unchanged. No real edit, expert judgment, training update or paid request was introduced.
