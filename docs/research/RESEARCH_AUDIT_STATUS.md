# Research audit and implementation status

## Active request

The September 2026 request authorizes a continuous end-to-end review, primary-literature research, implementation, execution, and delivery of readable, evidence-linked outputs that can be compared with Richmond's human synthesis. Project artifacts are in English. The central deliverables are an accurate Richmond reference document, an honest inventory of existing outputs, a justified algorithm and architecture, and an executed comparison package with explicit human-review status.

## Current continuation checkpoint: evaluation v2 and semantic contracts

Previous goal turn made verified progress: completed/froze the machine baseline, inspected actual artifacts, prepared human packets, and diagnosed four comparison-link defects. This continuation implemented a separate scoped evaluator and tested those failure cases. The v2 contract requires selected-theory evidence for partial as well as equivalent matches, exact theory anchors, explicit quarantine and no silent verdict rewriting. See `EVALUATION_PROTOCOL_V2.md`.

**New provider interruption:** the first request in `outputs/runs/evaluation-20260923-v2` failed on HTTP 429 `credit_balance_exhausted` (request timestamp 2026-09-23T10:55:41Z). Zero evaluation-v2 responses completed; its net recorded budget charge is zero. The earlier baseline remains complete. No process remains running. The owner has been asked about replenishment; no answer is inferred. Read `CURRENT_RUN_RESULTS.md` before retrying.

Offline work added `semantic_contracts.py` and the cited `SEMANTIC_ASSERTION_METHOD.md`: separate source entities and conditional assertions; relation-specific evidence; comparator/time/inference labels; statistical direction distinguished from educational benefit/harm. These are implemented contracts and source/structural checks, **not executed semantic extraction or trained NER/RE**. Thirty-two tests pass (existing asyncio warning), with targeted Ruff checks passing. Human review and all previously identified research gaps remain pending.

The updated consolidated PDF is `output/pdf/Research_Method_and_Verification_20260923.pdf` (19 pages), combining the current method, semantic contract, evaluation-v2 protocol and baseline review. Poppler renders were visually checked, including corrected list separation, table proportions and page footers. Its manifest records PDF/builder/source hashes. The September 10 PDFs remain unchanged. This document update resolves the stale-method-PDF item, not the unexecuted research experiments.

## Completed baseline checkpoint: 2026-09-23

The fixed-corpus baseline completed machine stages with process exit 0: **28 source records, 180 findings, 174 eligible, nine final theory statements and 18 comparisons**. API access is restored. Total clean-run completed-call estimate is USD 13.5529 across 97 calls. Human review remains pending; the owner has no two reviewers yet and requested preparation first.

Open `outputs/runs/inspection-20260923-v4/index.html` for the current complete inspection snapshot. The AI comparison labels are 14 partial and four not_recovered, not a human validation score. Post-run checking found unlinked comparison evidence in RC04/RC05/RC11/RC12, including no selected theory for RC11. The viewer explicitly warns on those rows while preserving original responses. `BASELINE_REVIEW_20260923.md` records further synthesis concerns. Do not claim the evaluation is fully validated or the full research goal achieved.

Reference ratification and source-support review packets exist in `reference-review-20260923-v1` and `source-review-20260923-v1`, respectively. All human fields are blank; machine judgments are withheld from independent source-support review. All 97 response/request identities and 1,100 located source offsets were checked, and complete exports/browser navigation were inspected. Tests: 22 passed. See `CURRENT_RUN_RESULTS.md` for costs, hashes, warnings and the next executable step. No pipeline process is intentionally left running.

Remaining scope includes semantic assertion extraction and 47/40 system evaluation, correction of comparison scope in a new evaluation version, source/synthesis adjudication, actual human intervention, full proposal-method reconciliation and controlled effectiveness experiments. Existing research PDFs still reflect September 10; current Markdown additions are not in them yet. Pony Tail remains unlocated.

## Earlier checkpoint: 2026-09-23 continuation (superseded above)

- The owner renewed the end-to-end objective, reported API credit replenishment, and clarified that no two independent reviewers are available yet: prepare the human-review package first. Actual human validation remains pending.
- Read `REQUIREMENTS_AND_ACCEPTANCE.md` for the full scope. The 47-concept/40-relation evaluation and before/after human intervention requested in July are not replaced by the 18-branch configuration comparison. Semantic relation extraction and the stronger proposal components remain explicit work, not completed claims.
- API access is now confirmed by successful new calls. All 28 available-source records have completed extraction and source audit: **180 findings, 174 eligible**, 71 completed cached calls, estimated clean-run cost **USD 5.6822** at the end of extraction (including the earlier USD 3.1133). The pilot and unresolved prior reservations remain separate accounting items. Source availability has not changed: eight snippets and one one-page PDF remain.
- Two offline preflight reports in `outputs/research_audit/` verify source/configuration identity, recorded request hashes, parsed-versus-raw response equality and reproducible paper audits. The second reproduces all 28 audits from 71 calls without network access. This is not semantic human validation.
- `outputs/runs/inspection-20260923-v2/index.html` exposes actual legacy entities/relationships and all 180 new findings, with source links, graph-edge semantics, CSVs and input hashes. The v1 inspection snapshot preserves the earlier 86-finding view. Both separate July semantic relations from September attribution/similarity edges.
- `outputs/runs/reference-review-20260923-v1/index.html` prepares independent A/B/adjudication forms for 47 concepts, 40 relations and 18 configuration branches. All decisions are blank; source-reference ratification is distinct from scoring the generated outputs.
- The extraction-only process completed successfully. The subsequent baseline synthesis/comparison process was launched using matching caches (tool session 68346 at this checkpoint). **Poll the handle or inspect terminal artifacts before inferring that it is still running or that it completed.** No new final synthesis or comparison was present when this checkpoint was written.
- Before the first synthesis request, scientific fields were explicitly selected to exclude filesystem paths (including the benchmark-named source directory), critic metadata and future external-review fields. Extraction requests stayed identical; code snapshots retain this pre-synthesis change. Local evidence/provenance files retain their original source paths.
- Old progress/error/partial-graph files were preserved under the run's `execution_history/checkpoint-before-20260923-completed-extraction/`; the resolved credit error is no longer presented as the current interruption. Historical July submissions were not modified.
- Current focused/full repository tests: **22 passed**; existing missing pytest-asyncio configuration warning remains. Browser checks exercised record counts, entity/relation selection, finding search and deep links, absent-theory display, source page links, and all nine reference form links. Targeted Ruff F/I checks pass.
- Pony Tail is still not located: exposed tools and installed plugin/skill filename searches did not find it; plugin-directory search returned no matching plugin. Its installation path remains requested. PowerShell/Python is the recorded execution method.

## Historical checkpoint: September 10 interruption

The following preserves the earlier audit context. Credit-related blockers and counts below are superseded by the dated checkpoint above.

- Extensive source reading has covered the accepted proposal, all five VTT meetings, the Richmond review, the 20 locally supplied corpus PDFs, metadata for 28 papers, professor briefing documents, implementation modules, historical reports, and reference-coding files. This is not a claim that every byte of every repository file has been semantically reviewed. A file-level coverage manifest will distinguish full reads, duplicate artifacts, metadata inspection, and outstanding material.
- A three-paper pilot completed in `outputs/runs/evidence-20260910-v1/`. It exposed quotation typography/copying and critic-index coverage failures. Source-line citation repair and explicit finding indices were implemented. The clean full fixed-corpus run in `outputs/runs/evidence-20260910-full/` stopped on provider `credit_balance_exhausted`: 19 extracted papers, 17 completed source audits, 86 findings, 83 eligible. Its source packets omit the benchmark-named directory. `progress.html` and partial CSVs show actual results. No new final programme theory/comparison exists. Do not mark it complete until `run_status.json` and `metrics.json` exist and outputs have been inspected.
- Existing July artifacts contain 91 CMOCs, 517 entity instances, 439 relations, and 26/28 papers with CMOCs. These are historical counts, not quality guarantees.
- Existing CSV exports contain repeated column names instead of row values. Parquet contains actual records. Both human-coder workbooks and concept/relation human verdict fields remain blank.
- Existing 47-concept/40-relation reference files are project operationalizations, not a machine-readable gold standard published by Richmond. Some mappings and five-chain definitions conflict with the primary paper.
- Existing reports overstate human validation and confuse quote location with claim support. Preserve them as historical records and issue a correction/limitations record.
- The current implementation does not implement all proposed GraphRAG, fine-tuning, RLHF, or human checkpoints. Documentation must distinguish proposal, implemented behavior, and tested behavior.

## Primary findings that must survive context changes

Richmond's five overlapping contexts are low knowledge, high knowledge, positive coping strategy, negative coping strategy, and mixed knowledge levels. Figure 2 is the final programme theory; Figure 3 expands low knowledge. Mechanisms include resources and learner responses. Retroduction may connect partial evidence across papers; it must not be represented as a directly measured causal effect. Year of training is not an adequate proxy for knowledge. Affect/confidence evidence is present in the available corpus. Do not repeat the old assertion that missing emotional concepts have essentially no textual basis.

The corpus has 28 included papers, not 28 independent medical RCTs. Eight records have short metadata/abstract snippets; S009 is only a one-page PDF; S020 is a secondary analysis related to S013. The search/screening experiment and fixed-corpus synthesis experiment are different evaluation tracks. Original searches occurred in May 2017.

Critical implementation defects include polarity-erasing normalization, requiring complete CMOCs within every source, unvalidated inferred links, cross-context/time contradiction detection, non-isolated metrics, and optimistic automatic verification. Human agreement and reliability remain unmeasured until actual reviewers complete the forms.

## Work sequence

1. Freeze source identity and reading coverage; retrieve original supplements if accessible; reconcile Richmond conclusions against exact pages.
2. Read primary realist-method, graph retrieval, evidence extraction, and evaluation literature; document justified choices and rejected alternatives.
3. Define versioned reference claims and configuration-level comparison protocol before the new run. Keep the comparator out of extraction and synthesis.
4. Implement an isolated evidence-preserving run and readable report/matrix exports; fix demonstrated defects with focused tests.
5. Execute a small pilot, inspect failures, then run the available fixed corpus with explicit missing-text status and a cost ceiling. Preserve prompts, provenance, raw responses, and actual usage.
6. Produce independent AI-assisted comparison and blank human adjudication fields. Compute only metrics supported by completed observations. Deliver limitations and concrete next human actions.

## Open operational items

- Pony Tail was requested by the owner, but has not yet been found in the exposed tool catalog or searched plugin/skill files. Investigate its installation; do not claim use without evidence.
- A clarification about the API budget was sent, with USD 50 proposed as the default ceiling. No reply had arrived when this entry was written.
- The repository inventory now exists at `outputs/research_audit/repository_inventory.csv`; detailed findings, method/verification and historical-output audit documents are in `docs/research/`. Two PDFs have been generated; the readable partial report has been inspected in headless Chrome. The full run remains unfinished because the provider account needs credit.
- Latest machine test suite: 19 tests passed; one environment warning indicates pytest-asyncio is not installed in the chosen interpreter. No async tests are currently present.
- The full run has a USD 50 budget ceiling including recorded pilot charges. Pony Tail remains unavailable in the exposed tools and searched plugin paths; the owner was asked for its installation path. Execution currently uses the authorized PowerShell/Python fallback.

## Exact continuation checkpoint

- Read `CURRENT_RUN_RESULTS.md` for the full interruption record and resume command. API credit restoration was requested from the owner; no response was available at this checkpoint.
- The clean attempt has 46 completed calls estimated at USD 3.1133; the separate pilot has 27 calls estimated at USD 1.4252. Four unfinished requests retain budget reservations. This does not reveal other account spending or assert final provider billing.
- Source-line range 95-97 on S015 PDF page 5 was invalid (95 lines exist). The response and original code snapshot are preserved. Invalid repairs now leave the original quote unresolved and the finding ineligible.
- Explicit `--retry-unfinished` archives unfinished requests without raw responses; it retains old reservations. Completed request hashes must match. Do not call again until API credit is restored.
- All 766 deduplicated long narrative fields from 16 historical verification JSONs were subsequently read. Their frequent polarity, time, proxy and reference-definition errors are documented. File-level reading coverage distinguishes text review, duplicate exports, data inspection and visual/byte-level limitations.
- Final completion still requires remaining paper audits, graph summaries, initial/refined programme theory, external comparison, output inspection and actual expert adjudication. Do not let a later assistant infer completion from the existence of code or a partial report.

Final offline QA: targeted Ruff F/I checks pass, 19 tests pass, the complete exporter was exercised with clearly labelled synthetic test fixtures, and existing human coding is preserved on re-export. The partial real-data HTML contains 86 entries and all six local/anchor links resolved in headless Chrome. Research PDFs have 5 and 9 pages with rendered layout review.
