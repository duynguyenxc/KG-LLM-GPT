# Research audit and implementation status

## Active request

The September 2026 request authorizes a continuous end-to-end review, primary-literature research, implementation, execution, and delivery of readable, evidence-linked outputs that can be compared with Richmond's human synthesis. Project artifacts are in English. The central deliverables are an accurate Richmond reference document, an honest inventory of existing outputs, a justified algorithm and architecture, and an executed comparison package with explicit human-review status.

## Current continuation checkpoint: explicit source locators and frozen replay

Previous turn made corpus integration progress (`ab0ec3f`). This continuation completes source-kind handling for semantic extraction and the correspondence workbench: PDF pages, partial-PDF pages, abstracts and metadata have distinct validated locators. The V2 prompt supplies source-unit semantics, and audited quotation records retain resolved locator provenance through JSON/CSV/graph and readable source links. The prior evidence/theory reports and review packets are not rewritten.

Actual V2 artifact: `outputs/runs/semantic-20260923-enriched-preparation-v2/`, prepared for all 28 papers with zero executed model calls/candidates. The V1 three-paper and enriched 28-paper preparations remain usable through `replay_semantic.py`, which verifies saved code, configuration and imported dependency identities before invoking the frozen entry point. Offline replays left all 24 and 74 files unchanged. Current V2 code intentionally differs from V1; never resume V1 through the new entry point. Evaluation-v2 code remains unchanged.

The repository suite reached 83 passing tests with the existing asyncio warning; targeted Ruff checks pass. Actual packet/source/baseline hashes, S009 locator labels and synthetic citation/independent-review navigation passed browser checks and visual inspection. QA: `outputs/research_audit/source-unit-20260923-qa.json`. No paid API call, new research extraction, reference score or human judgment. See `SEMANTIC_EXTRACTION_RUNBOOK.md` for current commands and budget caveats. Full-text gaps, actual semantic/evaluator execution, canonical/graph/synthesis integration, training experiments and real human evaluation still prevent full-goal completion.

## Earlier continuation checkpoint: supplemented corpus connected to offline extraction

Previous turn made source-acquisition progress (`a6c2a42`). This continuation adds `corpus.py` to verify the acquired XML/abstract identities and create a new sibling corpus without overwriting research history. Actual version: `outputs/runs/corpus-20260923-abstracts-v1/`, comprising 19 unchanged full-text records, eight complete abstracts and S009's original partial PDF plus abstract. Source units retain a locator map; an abstract unit is not an original PDF page. See `CORPUS_VERSIONING.md`.

The existing semantic runner successfully prepared all 28 packets in `outputs/runs/semantic-20260923-enriched-preparation-v1/`. It has not executed: zero calls, zero new entities/assertions and no scientific improvement result. The older pilot/evaluator code and baseline hashes remain unchanged. The historical evidence loader is not a loader for the new corpus; complete synthesis integration remains unfinished.

Nine new synthetic tests passed; the repository suite reached 75 passing tests with the existing asyncio configuration warning. Actual snapshot/bundle/packet checks and browser inspection passed. QA: `outputs/research_audit/corpus-enrichment-20260923-qa.json`. The generic semantic viewer still labels units as source pages; the source locator map must be surfaced explicitly downstream before publishing enriched citations. Credit restoration, actual new extraction/evaluation and human review remain pending. The full goal is not complete.

## Earlier continuation checkpoint: nine supplemental abstracts acquired

The previous goal turn restated and verified existing review packets; it did not advance implementation. This continuation searched the nine incomplete source records and captured nine complete official author abstracts through PubMed EFetch. The raw XML and per-article source records are isolated in `data/source_acquisition/20260923-pubmed/`; no frozen corpus or result was replaced. Open `outputs/research_audit/source-acquisition-20260923/index.html`. See `SOURCE_ACQUISITION_STATUS.md` for provenance and remaining access limitations.

Zero new local full-text PDFs, zero model API calls and zero human judgments. S010 full-text body text was accessible through the web tool, but local download and graphical inspection failed; it is not counted as locally acquired full text. Targeted searches found restricted institutional copies and catalogue records, which were not treated as usable articles. Assistant observations identify source-coverage distinctions for the next run rather than silently correcting historical extraction.

All nine abstracts were read; identifiers, raw/parsed hashes, six baseline hashes and the readable report were checked. Production code and existing results are unchanged. Source enrichment must use a new frozen corpus/run and be distinguished from algorithm changes. Actual new semantic extraction, evaluator-v2 execution, independent ratification and full-proposal experiments remain incomplete. Credit restoration and reviewers are still outstanding; no paid process is running.

## Earlier continuation checkpoint: attributed synthesis revision workflow prepared

Previous turn made concrete correspondence-workbench progress (`cacd758`). This continuation inspected the existing feedback-store and source-review workflow, revisited the professor's manual-intervention instructions and implemented `interventions.py`. It records attributed add/replace/withdraw actions, exact parent/source/reference identities, before/after events and explicit human versus AI assistance, in new sibling runs. It rejects stale/no-op/empty/conflicting submissions and unknown finding links. This is output editing, not RLHF, fine-tuning or reference repair.

Actual artifact: `outputs/runs/intervention-preparation-20260923-v2/index.html`, containing nine existing baseline theories and an **empty ledger**. Status is prepared_no_intervention; zero actual edits and no changed research synthesis. V1 preparation is preserved; V2 provides readable field views. `ATTRIBUTED_INTERVENTION_PROTOCOL.md` explains use, version controls, fixed-rubric before/after evaluation and scientific limits. No reviewer identity or judgment was invented.

Validation: 66 repository tests passed with the pre-existing asyncio warning; targeted Ruff checks pass. Browser checks exercised the real source link and a labelled synthetic before/after example, with changed-field highlighting and no severe errors. Baseline/source/reference hashes remain unchanged. QA: `outputs/research_audit/intervention-preparation-20260923-v2-qa.json`. Prepared/applied structures retain pending human validation; attribution fields do not authenticate a reviewer. No API calls or training updates occurred.

The API credit interruption and unavailable raters remain unresolved. Next work still includes actual semantic pilot/evaluator execution after credit restoration, source/graph integration, canonical/evaluation experiments, and real attributable human contributions followed by independent before/after assessment. A prepared ledger is not the requested measured intervention result; the full goal remains active and incomplete.

## Earlier continuation checkpoint: actual-output 47/40 human review workbench

Previous turn made source-audit progress (all 47 concepts/40 relations/five chains, commit `3bb7834`). This continuation implements a separate reference-to-output review workbench and strict form importer. Open `outputs/runs/correspondence-review-20260923-legacy-v2/index.html`: 47/40 reference items sit beside 517 actual historical entities and 439 actual historical relations, with actual endpoint IDs, CMOC narrative, source quotations and frozen-page text. No automatic match or human verdict is supplied. This is July semantic output, not new September semantic extraction. `CORRESPONDENCE_REVIEW_GUIDE.md` documents use and limits.

Six A/B/adjudication CSVs are blank (47 or 40 rows each). Selected relation paths must join actual entity-instance IDs within one paper/configuration; equivalence requires six explicit dimensions. Adjudication requires paired reviews, distinct A/B identities and a reason. Record checks do not authenticate people or establish semantic truth. The reference remains unratified; recovery/precision metrics remain null. A prepared/unexecuted semantic run is rejected as evaluation input instead of being labelled non-recovery.

New historical issue: S008-cmoc-458176-r-1de6ea maps two different entity instances to the same canonical label, leaving edge direction unresolved. The workbench retains both candidates and flags ambiguity; the old edge is unchanged. Historical relations lack dedicated relation quotations; 494/517 endpoint quotations were located anew in frozen source text, not semantically validated. V1 preparation is preserved; V2 exposes the ambiguous endpoint candidates.

Validation: repository suite reached 56 passing tests; all 11 new focused tests passed after the endpoint-display correction; existing asyncio warning persists. Input/form/browser checks and visual review passed, including the ambiguous edge and 47/40 versus 517/439 record counts. No API calls or actual human reviews. Engineering evidence: `outputs/research_audit/correspondence-review-20260923-qa.json`. Frozen production/evaluation/semantic-pilot artifacts remain unchanged.

Next: continue canonical/semantic integration and evaluation preparation offline; execute the semantic pilot and evaluator v2 after credit restoration, then create a separate actual new-output correspondence packet. Reference ratification, source-support judgments and attributable human intervention still require reviewers. Full-proposal experiments and the overall goal remain incomplete.

## Earlier continuation checkpoint: historical reference audited against the original paper

Previous goal turn was progress: semantic extraction/critic implementation, 45 passing tests, frozen offline pilot and commit `1d4ad37`. This continuation audited all 47 legacy concepts, 40 relations and five historical union chains against the original Richmond text and visually inspected Figures 2/3. `outputs/runs/reference-audit-20260923-v1/index.html` preserves each original entry, assistant proposal, source locator and blank human decision. See `REFERENCE_STANDARD_AUDIT.md`. No original reference or production artifact was changed.

Material concerns include E43's locally explicit Mresponse role versus the old Outcome label; E21's compound role; R17's polarity-ambiguous CONSTRAINS predicate; R11/R28's unestablished serial response arrows; R37-R40's omitted mediators; and cross-context mixing in the old five chains. All 40 legacy triples lack dedicated qualifiers; this is not a claim that all are false. The 47/40 inventory also omits several distinctive Figure 3 elements, so perfect inventory recovery would not prove complete programme-theory recovery. All proposals are assistant analysis, not expert judgments.

The version-checked builder preserves exact input hashes and creates a separate report/JSON. Coverage/UI checks verify 92 distinct entries, blank human fields, source-page links, search, E43/R17 deep links and no severe browser errors. Original and reference hashes match; zero API calls. Existing independent ratification forms remain blank and unchanged. Withhold assistant proposals during initial coding when measuring unaided agreement; disclose assistance otherwise. Actual human ratification, new semantic extraction and scoped evaluation v2 remain pending. The API interruption and full research scope are unchanged.

Next offline work can implement linked concept/relation correspondence without confusing path summaries, semantic assertions and full explanations. Do not revise the reference merely to increase a system score or conflate reference repair with human improvement of system output. Paid execution still awaits credit-restoration confirmation; no process is live.

## Earlier continuation checkpoint: semantic extraction runner prepared offline

The previous conversational turn only rechecked existing review packets and explained their use; it did not advance implementation. The next safe action was available despite the API credit interruption: implement and test the source-led entity/assertion runner. This is now done in `semantic_pipeline.py`, including an independent AI source critic, exact typed-ID coverage, endpoint/source gates, qualified graph/CSV/JSON exports and searchable source-linked HTML. All candidates and uncertainty remain inspectable. No benchmark is loaded by production extraction or its critic.

`outputs/runs/semantic-20260923-pilot-v1/` is **prepared_not_executed** for S006/S015/S026, with zero model calls. Frozen source snapshots cover the existing 28-record corpus; the pilot packets contain three selected sources. No new semantic entities, relations or accuracy result have been generated. Selection is development informed by prior errors. See `SEMANTIC_EXTRACTION_RUNBOOK.md` for exact commands, output meanings and limits.

Validation: 45 tests pass (one pre-existing asyncio configuration warning), targeted Ruff F/I passes, synthetic browser checks and real prepared-source navigation pass. Twenty raw PDFs, metadata identity and three packet hashes were checked; evaluation-v2 code/dependencies remain unchanged. An end-to-end test found and resolved Windows newline/hash inconsistency before freezing the pilot. Engineering report: `outputs/research_audit/semantic-preparation-20260923.json`. No paid request was attempted in this continuation.

Current blockers for execution/human evaluation remain the new API credit interruption and unavailable independent reviewers. Offline integration/evaluation work remains possible. Next: run the frozen semantic pilot and resume evaluator v2 only after credit restoration; inspect errors before full-corpus semantic execution, then implement canonical candidates, linked 47/40 evaluation and integration experiments. Human fields stay blank. The complete research objective remains unfulfilled. The dated method PDF preserves the earlier contract-only edition; the new runbook documents subsequent implementation.

## Earlier continuation checkpoint: evaluation v2 and semantic contracts

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
