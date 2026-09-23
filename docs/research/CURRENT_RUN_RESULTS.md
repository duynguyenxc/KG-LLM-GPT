# September research run: observed results and continuation

## Current continuation: source citations distinguish abstracts from PDF pages

`outputs/runs/semantic-20260923-enriched-preparation-v2/index.html` is the latest offline semantic preparation. All 28 packets now identify source kind and original-page identity; its readable S009 source distinguishes the retained PDF page from abstract unit 2. Citation locators are preserved in new semantic JSON/CSV/graph and correspondence exports. There are still zero new semantic calls/results and no human judgments.

For the preserved V1 pilot or V1 enriched preparation, use `python -B -m res_pipeline.evidence.replay_semantic --run-dir <existing-run-directory>`; default is offline. The current semantic entry point has a new prompt/code identity and must not be used to resume V1. Exact replay checks left 24/74 old files unchanged. The evaluator-v2 continuation below is unaffected. The repository suite reached 83 passing tests; `SEMANTIC_EXTRACTION_RUNBOOK.md` records scope and limits. New execution still awaits credit restoration.

## Earlier continuation: supplemented corpus prepared for extraction

`outputs/runs/corpus-20260923-abstracts-v1/index.html` shows the separate 28-record corpus: 19 unchanged full texts, eight complete abstracts and one partial PDF plus abstract. `outputs/runs/semantic-20260923-enriched-preparation-v1/index.html` is its actual offline extraction preparation, with 28 frozen packets and zero model calls/results. Read `CORPUS_VERSIONING.md` for commands, citation-unit limits and scientific controls. Existing baseline outputs and older pilot/evaluator hashes are unchanged. The test suite reached 75 passing tests; this does not establish scientific validity or human review.

## Earlier continuation: source supplements captured, not yet adopted

Nine complete PubMed abstracts are now preserved separately under `data/source_acquisition/20260923-pubmed/`. Open `outputs/research_audit/source-acquisition-20260923/index.html` for each incomplete source and the newly available distinctions. No new local full-text PDF, changed baseline input, new synthesis, paid call or human judgment occurred. `SOURCE_ACQUISITION_STATUS.md` records access failures, identity checks and the need for a separate corpus-enrichment experiment. The baseline remains the latest complete machine synthesis; prepared semantic/evaluator runs remain unexecuted or interrupted as recorded below.

## Earlier continuation: intervention recording prepared, no actual edits

`outputs/runs/intervention-preparation-20260923-v2/index.html` now provides the nine baseline theories, empty revision ledger, schema and record hashes. `interventions.py` can record attributed add/replace/withdraw/split changes in a new sibling run while preserving original evidence and reference versions. No submission has been supplied or applied to research output. Human/AI attribution, source support and independent validation remain separate; no improvement score is claimed. See `ATTRIBUTED_INTERVENTION_PROTOCOL.md`.

The repository suite reached 66 passing tests; browser checks covered readable before/after fields using explicitly synthetic data, real source navigation and unchanged baseline hashes. No API call, real human intervention or model training occurred. The latest real machine result is still the baseline with 180 findings/nine theories; semantic extraction and evaluator v2 still await credit restoration.

## Earlier continuation: 47/40 review now displays actual historical output

`outputs/runs/correspondence-review-20260923-legacy-v2/index.html` is a new side-by-side review workbench: 47 reference concepts/40 reference relations and all 517/439 historical system records. Six blank independent/adjudication forms and a strict linkage/provenance validator are ready. Read `CORRESPONDENCE_REVIEW_GUIDE.md`. No correspondence decisions or accuracy scores have been invented. This is explicitly historical July output; the new semantic pilot still has not run.

The workbench identifies one ambiguous S008 canonical endpoint mapping and keeps its original entity candidates visible. Historical edges have no relation-specific quotation; endpoint evidence must not be mistaken for relation support. Input hashes, all form rows, search/source expansion and browser record counts were checked. The repository suite reached 56 passing tests; focused tests passed after the display correction. No API calls; human decisions remain zero. V1 preparation is preserved as the earlier inspection stage.

The new API credit interruption below remains unresolved. Baseline 180 findings/nine theories remain the latest complete machine synthesis. The semantic pilot and evaluator v2 have no new results; do not mix the historical semantic packet with those experiments.

## Earlier continuation: reference audit completed, no new model output

`outputs/runs/reference-audit-20260923-v1/index.html` now exposes assistant audit notes for all 47 historical concepts, 40 relations and five union chains, with original coding and primary-paper page links. `REFERENCE_STANDARD_AUDIT.md` explains role/polarity/mediator/context concerns and versioned evaluation consequences. The audit changes neither the historical reference nor system outputs and contains zero completed human decisions. It is not a new system comparison score or a ratified gold standard.

Coverage and browser checks verified all 92 entries, unchanged source/reference hashes, blank human fields and working search/deep links. No API call was made. The semantic pilot below remains prepared_not_executed and evaluator v2 still has zero responses after the recorded credit failure. The baseline with 180 findings/nine theories remains the latest completed machine result.

## Earlier continuation: semantic pilot prepared, not executed

The source-led semantic extraction/critic runner is implemented and tested. `outputs/runs/semantic-20260923-pilot-v1/index.html` shows the explicit prepared state and readable frozen page text for S006/S015/S026. No new semantic API response or research accuracy result exists; candidate counts are zero because execution has not begun. The baseline remains the actual completed result. See `SEMANTIC_EXTRACTION_RUNBOOK.md` for the offline command and later `--execute` command, output contract, pilot selection rationale and shared budget accounting.

Forty-five tests pass, targeted Ruff checks pass, browser source navigation and synthetic record inspection pass. The audit report `outputs/research_audit/semantic-preparation-20260923.json` verifies zero API calls, all 20 source PDF hashes, metadata identity, three packet hashes and unchanged evaluation-v2 code. Do not rerun baseline extraction merely to obtain this new semantic representation. The extension is a separate, identifiable experiment; full-corpus semantic execution and 47/40 scoring remain pending.

The latest provider state is still the evaluator-v2 credit rejection below. No live process is waiting. Credit restoration has not been confirmed in response to that new interruption. Human raters remain unavailable; all prepared forms are blank.

## Earlier continuation: evaluation v2 interrupted, baseline preserved

A new evaluation implementation in `src/res_pipeline/evidence/evaluation.py` evaluates the frozen theory under an explicit theory-level contract. It checks all six dimensions, selected-theory finding links for partial/equivalent/contradictory verdicts, and verbatim theory anchors. Invalid assessments are quarantined without silently rewriting their verdicts. Read `EVALUATION_PROTOCOL_V2.md` for the pre-execution protocol. The new run is `outputs/runs/evaluation-20260923-v2/`; it is separate from production and includes prior run/pilot charges in the existing USD 50 software cap.

The first call `compare_RC01` was rejected with HTTP 429 `credit_balance_exhausted`, timestamp **2026-09-23T10:55:41Z**. The process exited 1; there is no live handle to poll. `failure.json` and `calls/compare_RC01/error.json` record the interruption. **Zero v2 model responses exist; no new v2 comparison result is claimed.** The ledger's reservation and rejected-no-generation reversal net to USD 0. The complete baseline below is unaffected.

The owner was asked whether to replenish credit or continue offline; no answer is assumed. After replenishment is confirmed, inspect the rejected-call records, then explicitly archive the request with the existing resume helper and run the identical evaluator:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
& 'C:/Users/Admin/AppData/Local/Programs/Python/Python311/python.exe' -B -c "from pathlib import Path; from res_pipeline.evidence.resume import prepare_resume; print(prepare_resume(Path('outputs/runs/evaluation-20260923-v2')))"
& 'C:/Users/Admin/AppData/Local/Programs/Python/Python311/python.exe' -B -u -m res_pipeline.evidence.evaluation --source-run outputs/runs/evidence-20260910-full --output-dir outputs/runs/evaluation-20260923-v2
```

The evaluator checks manifest/code/config identities on resume. A changed protocol requires a new run. After completion, inspect `run_status.json`, `comparison.json`, row quarantine reasons and rendered `index.html`; preserve the historical failure record and document its resolution rather than mistaking it for a current block.

Offline semantic extension work now includes typed entity/conditional-assertion contracts and source/structural checks in `semantic_contracts.py`, with the scientific rationale and unimplemented stages in `SEMANTIC_ASSERTION_METHOD.md`. No semantic-extraction API run has happened under this extension. Tests: 32 passed; targeted Ruff F/I passed. Next offline work includes completing the source-led extraction/audit runner, linked relation evaluation and updating research PDFs. Human raters are still unavailable, so preparation remains distinct from validation.

The research PDF update subsequently completed: `output/pdf/Research_Method_and_Verification_20260923.pdf`, 19 pages, with a hash manifest and Poppler visual QA. It includes the current method, semantic contract, evaluation-v2 specification and baseline limitations. Older PDF editions remain preserved. The source-led extraction/audit runner and linked relation evaluation still require further implementation/execution.

## Completed baseline: September 23, 2026

The baseline process **68346 exited with code 0**. No pipeline process is left intentionally running. All machine stages completed: 28 records, 180 findings (174 eligible), six communities, one refinement pass, **nine final provisional theory statements and 18 AI comparison rows**. This is completion of the current fixed-corpus baseline, not the full accepted research programme or human validation.

**Open `outputs/runs/inspection-20260923-v4/index.html` first.** It shows actual historical entities/relations and the new findings/theories/comparisons, with source navigation and visible comparison-link warnings. Earlier v1-v3 snapshots are preserved. `outputs/runs/evidence-20260910-full/report.html` is the original generated report; its comparison counts must be interpreted with the post-run audit below.

The AI returned **14 partial / 4 not_recovered / 0 equivalent**. Four partial rows (RC04, RC05, RC11, RC12) cite findings outside their selected theory statements; RC11 selects no theory. These are not validly linked theory-recovery assessments without further review. The original responses and counts remain unchanged, and v4 displays the defects. Do not convert these labels to human accuracy/recall. Read `BASELINE_REVIEW_20260923.md` for concrete synthesis and evaluation concerns.

Completed-call cost for the entire clean attempt is **USD 13.5529** across **97 calls** (36 GPT-5.5 and 61 GPT-5.4 mini), including September 10's USD 3.1133; the September 23 increment is approximately **USD 10.4396**. The separate pilot cost remains USD 1.4252. The clean-run ledger including unresolved reservations is USD 15.1265. These are configured token estimates, not the provider invoice. The account/API is working; credit exhaustion is no longer the active blocker.

The frozen theory hash is `d0489f641746eeb0389343e28c0db521e441e582ff98bf8fcfb1cb0ca81bdf7f`. `outputs/research_audit/completed-baseline-20260923.json` checks all 97 request identities/raw-versus-parsed responses, 1,100 located spans, final theory references, frozen hash and actual CSV counts; it explicitly reports the four comparison-link warnings. Engineering checks do not authenticate scientific claims. Browser QA exercised 18 comparisons, nine theories, links to findings, warning display, report anchors/downloads and the blind packet; no severe console errors were found. Repository tests: 22 passed, with the existing asyncio configuration warning.

Human preparation is now split into three tasks: reference ratification at `outputs/runs/reference-review-20260923-v1/index.html`; source support for all 180 findings/nine theories at `outputs/runs/source-review-20260923-v1/index.html`; and the baseline's `blind_review.html`/coder forms for configuration correspondence. All decisions are blank. The source-support packet withholds machine verdicts and has six independent/adjudication forms. Reviewers are not yet available, as confirmed by the owner.

**Next executable work:** preserve this baseline; address the comparator's finding-versus-theory scope in a separately identified evaluation version; implement and evaluate source-led conditional semantic assertions and the 47/40 system-comparison track; retain exact inference/comparator/time qualifiers and audit the synthesis concerns. Reference ratification and genuine before/after-human results await actual reviewers. Proposal-to-baseline gaps, broader experiments, missing sources and PDF updates remain explicit. Do not rerun all extraction or present a changed evaluation as the original baseline. Pony Tail remains unlocated; execution used PowerShell/Python.

## Earlier September 23 extraction/synthesis checkpoint (superseded above)

API credit restoration has been verified by successful new calls. The extraction/source-audit stage completed with exit code 0 on all **28 available-source records: 180 findings, 174 eligible**. Seventy-one recorded calls have an estimated clean-run completed-call cost of **USD 5.6822**, including the previous USD 3.1133. The additional extraction/audit work cost approximately USD 2.5689. The separate pilot and uncertain reservations remain in the ledger. Eight snippets and one one-page PDF still limit source coverage.

**Open actual output:** `outputs/runs/inspection-20260923-v2/index.html`. It shows 517 historical entity instances (180 canonical IDs), 439 historical relationships, 91 historical CMOCs, and all 180 September findings. Records open their evidence and actual graph neighborhood. Deep links include `#findings/S006-F06` and `#findings/S026-F03`. The September graph has 1,933 finding/component/evidence nodes, 696 component-attribution edges, 1,063 citation edges and 9,611 lexical retrieval links; these are not counts of validated causal relations. The inspection snapshot distinguishes the two experiments.

**Human preparation:** `outputs/runs/reference-review-20260923-v1/index.html` contains instructions and blank A/B/adjudication forms for 47 concepts, 40 relations and 18 configurations. The owner confirmed that two reviewers are not available yet and asked to prepare the package first. Reference ratification is distinct from system scoring; neither human agreement nor human validation is claimed.

The six ineligible findings are S007-F03, S009-F01/F02, S015-F05 and S026-F02/F03. Three were marked partial by the critic; three have unlocated quotations despite a supported critic verdict. They remain visible. The S026 comparator/timepoint interpretation merits expert source review; an automated exclusion is not a final scientific verdict.

**Execution checkpoint:** after successful extraction, the baseline synthesis/comparison command below was launched as tool session **68346**. Poll that specific handle before doing anything dependent on its status. A saved checkpoint is not proof that a process is currently live. At this checkpoint the final programme theory/comparison had not yet been generated. Do not start a duplicate merely because an observation times out.

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
& 'C:/Users/Admin/AppData/Local/Programs/Python/Python311/python.exe' -B -u -m res_pipeline.evidence.pipeline --run-dir outputs/runs/evidence-20260910-full
```

If the process is terminal/unavailable, inspect `calls/`, `run_status.json`, `metrics.json` and any new `failure.json` before deciding how to resume. Raw responses without parsed results must be inspected before retry. The four earlier unresolved requests were archived in `calls_archive/attempt-001/`, retaining uncertain reservations. Completed extraction requests stayed identical. Before the first synthesis request, an explicit scientific-field selection removed local paths and evaluation metadata from model inputs; code snapshots preserve that change.

Offline evidence: `outputs/research_audit/preflight-20260923-001.json` verifies 46 old calls/17 audits; `preflight-20260923-002.json` verifies 71 calls/all 28 audits. Both reread current sources, compare configuration and request identities, and compare parsed caches against raw model responses, without API calls. Tests: 22 passed with the existing pytest-asyncio configuration warning. Browser inspection and targeted Ruff F/I checks passed. These engineering checks do not establish scientific validity.

Old partial progress/error/graph artifacts are preserved under `outputs/runs/evidence-20260910-full/execution_history/checkpoint-before-20260923-completed-extraction/`. The v1 inspection package preserves the earlier 86-finding view. Historical July submissions are unchanged.

The 18-branch evaluation does not replace the 47/40 concept/relation track. Semantic assertions, linked source-support evaluation, actual expert judgments, before/after human intervention, and the proposal's unimplemented training/graph components remain explicit work. Read `REQUIREMENTS_AND_ACCEPTANCE.md`. The current machine baseline is not declared the completed research architecture.

Pony Tail remains unlocated after tool, local plugin/skill filename and plugin-directory searches. The installation path is still requested. Execution used PowerShell/Python.

## Historical September 10 checkpoint (superseded above)

### What existed at the interruption

The clean run is `outputs/runs/evidence-20260910-full/`. It is **incomplete because the OpenAI API returned HTTP 429, `credit_balance_exhausted`**. This is an observed billing interruption, not a model-quality verdict. No new final programme theory, Richmond comparison score or completed human validation is claimed.

| Observation | Recorded value | Interpretation |
|---|---:|---|
| Fixed included-paper records | 28 | 19 apparently full PDFs, one one-page PDF, eight short snippets |
| Papers with a saved extraction response | 19 | Some still lack a completed source audit |
| Papers with a completed source audit | 17 | S001-S014 and S016-S018 |
| Findings in completed audits | 86 | Includes partial configurations and unmeasured proposals |
| Findings passing the machine gate | 83 | Full quote location plus AI critic support, not expert validation |
| Completed API calls in this attempt | 46 | Raw requests, responses and token usage retained |
| Estimated completed-call cost | USD 3.1133 | Standard uncached-token estimate, not an account invoice |
| Separate pilot cost | USD 1.4252 | 27 calls across development/repair attempts |
| Combined completed-call estimate | USD 4.5385 | Other account spending and four unresolved calls are not known |
| Full-run budget charges including unresolved reservations | USD 4.6869 | Reservations deliberately retained for calls without responses |
| Final new programme theory / comparison | Not generated | Downstream synthesis/evaluation remain to run |
| Independent human validation | Not performed | Human recall, precision and kappa remain unavailable |

The account balance is shared with activity outside this experiment. A USD 50 software ceiling does not guarantee that the API account contains USD 50 of usable credit.

## Open these outputs

- `outputs/runs/evidence-20260910-full/progress.html`: readable coverage and actual findings, including quotations, source pages, evidence status and limitations.
- `.../partial_evidence_matrix.csv`: one audited finding per row, with actual values and explicit eligibility.
- `.../paper_progress.csv`: extraction/audit status for every included record.
- `.../comparison_plan.csv`: the 18-row Richmond layout with six comparison dimensions and unexecuted verdicts left blank. It is an evaluation instrument, not an evaluation result.
- `.../papers/Sxxx.json`: full paper extraction, source audit and machine gate decisions.
- `.../calls/`: exact model requests, responses and parsed outputs. `usage.jsonl` records completed and unresolved charges.
- `.../failure.json` and `.../progress.json`: interruption and machine-readable checkpoint.

The scientific output being sought is a set of conditional explanatory statements, each traceable to source evidence. A graph organizes that evidence; the comparison matrix tests correspondence with Richmond; independent reviewers judge source support, explanatory coherence and useful differences.

## A concrete example already visible

In `papers/S016.json`, finding **S016-F02** preserves lower immediate-test performance after structured reflection, including the borderline comparison after correction. **S016-F03** separately preserves the higher performance at the one-week delayed test. **S016-F07** labels the proposed cognitive-load/confusion explanation as an author inference rather than a measured mediator. These are distinct observations under different time conditions, not an automatic contradiction.

This example shows why a useful matrix needs time, comparator and evidence status in addition to C/R/M/O labels. It does not prove that every finding is accurate. Another caution is S006-F02: its negative direction concerns increased time spent, not decreased diagnostic learning. Outcome definitions must remain visible whenever direction is interpreted.

## What interrupted execution and what changed

The first full attempt stopped when a citation-repair response selected lines 95-97 on a page containing only 95 lines. The original response and execution snapshot were preserved. The implementation now retains the unresolved original quote and quarantines its finding instead of accepting an invalid range or terminating every paper. A focused test verifies that even a positive AI critic verdict cannot admit that unresolved citation.

The resumed attempt encountered exhausted API credits. Four requests have no saved response: `critic_v3_S015`, `critic_v3_S019`, `extract_S020`, `extract_S021`. The visible provider error came from `critic_v3_S015`; the precise outcomes/billing of the other three are not asserted. No completed extraction is discarded or regenerated solely because another call failed.

Future explicit retries archive unresolved requests, preserve uncertain cost reservations, and reuse completed calls only when request hashes match. A raw response without a parsed result must be inspected before retry. Provider credit errors are now recorded directly and halt new generation requests in that client. Execution-code changes preserve prior snapshots.

## Resume after API credit is restored

From the repository root, using the same Python environment and private `.env`:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -B -u -m res_pipeline.evidence.pipeline --run-dir outputs/runs/evidence-20260910-full --retry-unfinished
```

The explicit retry flag archives only unfinished calls without raw responses; it does not remove completed responses or erase cost reservations. Inspect `failure.json` first. Do not use the flag to bypass a schema, source-identity or changed-prompt error. Finish the remaining paper audits, graph communities, synthesis, return-to-source refinement and external comparison. Then inspect the generated `report.html`, `metrics.json`, source evidence and human forms before reporting completion.

Only after the machine stages complete should two reviewers ratify the reference decomposition and independently evaluate the outputs. The protocol is in `METHOD_AND_VERIFICATION_PROTOCOL.md`. Finding agreement with Richmond is one evaluation dimension; neither agreement nor disagreement alone establishes scientific truth.

## Verification performed in this session

Nineteen focused/existing tests pass, covering source-location integrity, invalid citation quarantine, correct CSV values, comparison consistency, retrieval identity, blank-human metric behavior, explicit resume preservation and provider-credit error handling. One pytest configuration warning concerns an unavailable asyncio plugin; no async tests were run. A deterministic check also confirmed 500 located quotations against source offsets (503 proposed spans total), correct CSV row counts and the integrity of a separately labelled partial graph: 902 nodes, 3,290 edges and four retrieval groups from 83 eligible findings. `partial_evidence_graph.json`, `partial_communities.json` and `integrity_checks.json` preserve these observations. These groups are not programme theories; no community synthesis has run. The full API experiment is incomplete. Unit tests are not evidence of human-level reasoning performance.

Pony Tail was requested but was not found in the exposed tools or searched plugin/skill paths. Its installation path was requested. Execution used PowerShell/Python; no Pony Tail use is claimed.
