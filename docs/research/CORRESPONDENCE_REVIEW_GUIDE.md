# Reviewing concepts and relations against actual system records

## Current deliverable

Open `outputs/runs/correspondence-review-20260923-legacy-v2/index.html`. The left pane contains the historical 47 concepts and 40 relations; the right pane contains **517 actual historical entity records and 439 actual historical relation records** from the preserved inspection snapshot. Choose a reference, search candidate records, open their actual endpoints and inspect quotations/full frozen source pages. This is a concrete reference-to-output workbench, not an AI-generated match list or a completed evaluation.

The system records are July output, not new September semantic extraction. The September baseline's 180 findings/nine theories remain a separate result. The new conditional-semantic pilot has not run. The exporter accepts completed semantic runs as a separate input mode and rejects prepared/unexecuted semantic output rather than misreporting its empty arrays as failed recovery. That input mode has not yet been exercised on actual new model responses.

The original reference is unratified and contains the concerns documented in `REFERENCE_STANDARD_AUDIT.md`. This packet deliberately withholds assistant audit suggestions, old correspondence labels, critic scores and verifier rationales during independent evaluation. Generated entity labels, predicted canonical IDs and CMOC narratives remain visible because they are the output being assessed. Search is literal filtering without semantic ranking or preselected matches.

## What the reviewer records

Download your own `concepts_A.csv` / `relations_A.csv` or B equivalents. The adjudication forms are separate. All six files are initially blank except the reference IDs; every concept form has 47 rows and every relation form has 40. Selecting a candidate in the browser does **not** save a judgment. Save decisions in the CSV, retaining its complete row population and original column names.

For each row, record:

- `verdict`: equivalent, partial, contradictory, not_recovered, uncertain or reference_problem. A blank cell means not reviewed, never a negative finding.
- `candidate_ids`: actual output IDs separated by semicolons. Use `match_unit=entity` for concepts, `single_assertion` for one relation, or `connected_path` for a directed sequence of relations. Put a path in traversal order.
- For relation equivalence, assess subject, object, predicate, context, qualifiers and inference status separately. All six must be equivalent before using equivalent overall. Structural linkage alone cannot establish these judgments.
- `source_support`: supported, partial, unsupported, uncertain or not_assessed, separately from reference correspondence. Record source page/quote and reasoning in `source_locator_and_note`; document the reference's scope/limitations in `reference_scope_note`.
- `rationale`, reviewer identity, ISO date/time in `reviewed_at`, and finite nonnegative `minutes`. Adjudication additionally needs `adjudication_reason` after both initial reviewers have completed the item.

For uncertain or problematic reference rows, a counterpart is optional. If an output's endpoint identity cannot be resolved, do not claim correspondence by selecting that unresolved relation; explain its ID and ambiguity in the notes pending source review or a separately attributed correction. No human record has yet been supplied.

## What the importer checks

`correspondence_review.py` validates complete reference populations, unique/known IDs, recorded provenance and allowed judgment values. Claimed correspondence requires actual output IDs. Multiple relation IDs must form a directed path joined by **actual entity-instance IDs**, not merely similar labels or a shared canonical label. A path must stay in one paper/configuration scope. Even a structurally valid path still needs human assessment of compatible qualifiers and explanation.

The importer rejects an edge with unresolved structure as a selected correspondence. It checks that adjudication follows paired reviews and that A/B do not name the same reviewer. These are record-integrity checks; names and dates do not independently authenticate who performed a review or whether reviewers truly worked independently.

Recovery against a ratified reference and source precision remain **null**, not zero. This packet uses an unratified reference. Moreover, a reference-centered matrix does not sample every generated assertion, so it cannot alone estimate source precision or the validity of novel claims. Reference ratification and source-support review remain distinct tasks. A future ratified version must be explicitly identified before reporting its recovery metrics.

## Newly observed historical limitations

The historical relation records store endpoint IDs, a predicate and a CMOC ID, but no relation-specific quotation. The workbench therefore labels endpoint quotations and CMOC narrative as material to inspect, not proof that the relation is supported. It independently located complete entity quotations in frozen September source text for **494 of 517 entity records**. This is a location count, not entailment accuracy; absent matches remain visible. It also does not prove that July used exactly the same source text.

One historical edge, `S008-cmoc-458176-r-1de6ea`, is structurally ambiguous. Both recorded canonical endpoints are `outc:diagnostic-error-correction`, while its two entity-instance references are `S008-cmoc-458176-e-646bce` and `S008-cmoc-458176-e-4eff0b`. The predicate is `UNTYPED_CANDIDATE`. The exporter preserves both endpoint candidates and labels direction unresolved rather than guessing source/target from a shared normalized label. The original edge remains unchanged.

This stricter check exposed a limitation of the earlier inspection check: membership of both canonical endpoints in the referenced set did not prove a unique instance-level mapping. The first prepared packet (v1) is preserved; v2 adds the unresolved endpoint candidates to the readable display. This is an inspection correction, not a change to historical scientific output.

## Reproducible commands and evidence

To produce a **new** snapshot, choose a new output directory:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
& 'C:/Users/Admin/AppData/Local/Programs/Python/Python311/python.exe' -B -m res_pipeline.evidence.correspondence_review --baseline outputs/runs/evidence-20260910-full --inspection outputs/runs/inspection-20260923-v4/inspection_data.json --output-dir outputs/runs/correspondence-review-NEW
```

To validate the saved forms without model calls or altering them:

```powershell
& 'C:/Users/Admin/AppData/Local/Programs/Python/Python311/python.exe' -B -m res_pipeline.evidence.correspondence_review --validate outputs/runs/correspondence-review-20260923-legacy-v2
```

For a completed semantic run, replace `--inspection ...` with `--semantic-run ...`; do not combine input modes. Its frozen page snapshot must match the source pages displayed. Partial/pilot versus full-corpus scope must still be reported; completion of selected papers is not full research completion.

The packet manifest records input, builder, template and packet hashes. Original inputs and forms are never overwritten by preparation. Browser checks exercised all 47/40 reference options, 517/439 candidate records, literal search, candidate selection, full-page evidence expansion and the ambiguous S008 edge. Six blank forms and input identities were verified; no severe browser errors occurred. The side-by-side view was visually inspected. `outputs/research_audit/correspondence-review-20260923-qa.json` records these observations.

Eleven new synthetic tests cover cross-paper/cross-configuration/disconnected paths, unresolved structure, dimension coverage, missing counterpart IDs, hidden historical scores, canonical endpoint ambiguity, blank versus incomplete forms, unexecuted semantic output, adjudication provenance and nonfinite review times. The repository suite reached 56 passing tests; the focused tests passed again after the endpoint-display correction. One existing pytest asyncio-configuration warning remains. No API calls or human judgments were introduced by preparation.
