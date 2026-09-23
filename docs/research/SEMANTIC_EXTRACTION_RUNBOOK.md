# Conditional semantic extraction: implementation and pilot

## Current source-locator version

The current runner uses `conditional-semantic-v2-source-units`. It validates a complete source-locator map (or derives unambiguous legacy PDF/metadata locators), supplies source kind and original-page identity to extraction, and retains resolved locators in entity/assertion evidence, CSV and graph JSON. Source viewers and the correspondence workbench display the distinction. An abstract source-unit ID is never an original PDF page. Unknown citation units remain unresolved and cannot pass source checks merely through this annotation.

Actual offline preparation: `outputs/runs/semantic-20260923-enriched-preparation-v2/`, all 28 papers from `corpus-20260923-abstracts-v1`, with **zero executed model calls**. Its `locators.json` and raw input locator snapshot are frozen alongside packets/code/prompts. No actual new assertion or human judgment has been generated. V1 preparations are preserved and must use the frozen replay command below, because the current entry point and prompt have changed. Comparing V1 and V2 would change method as well as potentially source; it is not a controlled source-enrichment result.

The repository suite reached 83 passing tests (the existing asyncio warning remains), including eight additional source-locator/replay cases. Actual checks verified all 28 new packets, source identities, evaluator-v2 code, S009 PDF-versus-abstract labels and old V1 replay preservation. Synthetic execution verified locator propagation through CSV/graph and the independent-review exporter without critic judgments. Browser checks exercised the actual S009 source view and labelled synthetic citation/review navigation. Evidence: `outputs/research_audit/source-unit-20260923-qa.json`.

## September 23 implementation checkpoint

`src/res_pipeline/evidence/semantic_pipeline.py` now implements source-led joint entity/assertion extraction, a separate AI source critic, exact typed-ID coverage checks, source/structural admission, qualified graph export, CSV/JSON export and a searchable HTML inspection page. It uses the contracts and methodological rationale in `SEMANTIC_ASSERTION_METHOD.md`. The dated 19-page PDF records the earlier contract-only checkpoint; this runbook records the subsequent implementation. Neither document is evidence of successful model execution.

Preparation runs offline by default. `--execute` is required for model calls. The actual prepared experiment is `outputs/runs/semantic-20260923-pilot-v1/`. Its status is **prepared_not_executed**, with zero generated candidates and zero API calls. Those zeros are not negative scientific findings. The frozen baseline with 180 findings and nine provisional theories remains unchanged.

## Scientific scope and pilot selection

The module reads frozen baseline source pages, not baseline findings/theories or Richmond's operational reference. A whitelist supplies paper identity, title, DOI, year, availability, study family and page text. Filesystem paths and prior evaluator/critic decisions are absent from production packets. The source manifest and page snapshots are retained separately for provenance.

The development pilot uses three available full texts:

| Paper | Selection rationale |
|---|---|
| S006 | Erroneous worked examples and feedback: inspect conditional effects and avoid converting useful feedback into an unsupported universal necessity claim. |
| S015 | Clinical decision making and perceived impact: distinguish perceptions, responses and measured outcomes; revisit source quotation problems observed in development. |
| S026 | Self-explanation, examples and prompts: distinguish within-group change from between-group contrasts and immediate from delayed/transfer outcomes. |

This selection is deliberately informed by prior errors and benchmark inspection. It is not random sampling, a representative performance estimate or held-out evaluation. The exact proposed assertions are not prefilled. The extraction must discover them from the original sources. After pilot inspection, freeze any changes in a new run rather than changing this experiment silently. Full-corpus extraction, canonical equivalence proposals, graph-grounded synthesis and 47/40 correspondence remain subsequent work.

## Execution contract

1. Validate the source manifest, paper selection and contiguous page identities. Freeze source/configuration/prompt/schema/code identities and snapshots. Reject changed inputs or existing unrelated directories. Packet bytes use explicit UTF-8/LF to make Windows hash verification reproducible.
2. Extract entities and assertions jointly. Each relation refers to actual local entity IDs and carries its own source quotations, conditions, comparator, time, outcome definition, direction and inference status. No automatic cross-paper canonical merges occur.
3. Run structural/source checks before the critic; duplicate/ambiguous identifiers stop processing. The separate AI critic receives the full source packet and original extraction, not automatic eligibility labels or the external benchmark.
4. Require one critic assessment for every typed local ID, with no missing, duplicate or unknown IDs. Invalid coverage stops the paper; there is no silent truncation of the assessment population.
5. Preserve all candidates. Entity admission requires located evidence/structural checks and a supported AI critic verdict. Assertion admission additionally requires both endpoints to pass. Model hypotheses retain their explicit evidence class even if the premises pass machine checks; this is not observed causal evidence or human approval.
6. Export after each audited paper. Mark completion only after the selected papers finish and the original source-input hashes still match. Completion concerns the selected machine stage, not scientific validity or full-proposal completion.

The shared `RunClient` retains request identities, raw/parsed responses, returned model versions, usage and estimated costs. Its existing no-automatic-retry and unresolved-reservation behavior applies. The pilot inherits the USD 50 software ceiling and includes the original pilot, completed baseline and interrupted evaluation-v2 ledgers. The budget is not the account balance. This preparation did not initialize an API client or charge tokens.

## Inspectable outputs

Open `outputs/runs/semantic-20260923-pilot-v1/index.html`. Before execution it explicitly states that results do not exist. Frozen sources are readable at `sources/S006.html`, `sources/S015.html` and `sources/S026.html`, retaining page numbers. These are extracted text, not PDF facsimiles: table/reading-order questions require the original PDFs.

After execution, each entity/assertion opens a readable record with source quotations and page links. Assertions show endpoint labels and IDs, comparator, time, statistical direction versus educational benefit/harm, inference status and AI review reasons. Failed candidates remain visible. Search covers records and evidence. Full records remain inspectable as JSON.

| Artifact | Meaning |
|---|---|
| `entities.json`, `entities.csv` | Source-scoped entities; mention/abstraction distinction and admission status. |
| `assertions.json`, `assertions.csv` | Conditional relations with separately audited evidence, qualifications and blank human approval. |
| `semantic_graph.json` | Candidate edges carrying full qualified assertion records, including rejected candidates; not universal causal triples. |
| `audited_papers.json`, `papers/Sxxx.json` | Per-paper audits and extractor/critic omissions. |
| `packets/`, `inputs/`, `code_snapshot/`, `manifest.json` | Frozen inputs and reproducible experiment identities. |
| `calls/`, `usage.jsonl` | Created only by actual model execution; absent in this prepared pilot. |

Entity/assertion CSVs retain source availability and study-family identity. Shared sample reports must not be counted as independent replication merely because they have distinct paper IDs. Source support, 47/40 reference correspondence and programme-theory recovery remain separate evaluations. No new precision, recall, F1 or human agreement is available from this preparation.

## Exact continuation

The latest provider observation is the separate evaluator's `credit_balance_exhausted` rejection. Do not interpret the owner's earlier top-up as a response to that new failure. Wait for confirmation of restored credit before executing the paid command below. No process is currently running.

Offline preparation/identity check (safe to repeat; does not erase generated outputs):

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
& 'C:/Users/Admin/AppData/Local/Programs/Python/Python311/python.exe' -B -m res_pipeline.evidence.replay_semantic --run-dir outputs/runs/semantic-20260923-pilot-v1
```

The replay helper checks frozen code and configuration hashes, verifies active imported dependencies against the frozen identities, and invokes the saved entry point. Its default is offline. The old three-paper and 28-paper preparations were replayed offline with all 24 and 74 files respectively unchanged. If dependencies differ, use an isolated matching checkout; do not relax the identity checks.

After credit restoration, execute the identical frozen pilot by appending `--execute`. Inspect both raw output and original source before extending to the full corpus. A changed source, schema, code, prompt or paper selection requires a new run. If an API call fails after its request is written, inspect its response/error before using the existing explicit resume helper; never discard a saved raw response or reset uncertain budget reservations. Resume evaluation v2 separately using `CURRENT_RUN_RESULTS.md`. Frozen budget configurations do not automatically include paid runs created later: verify the intended shared budget before replaying an older experiment after newer spending. No newer semantic spending has occurred in this checkpoint.

To check the new 28-paper V2 preparation offline, use the same replay helper with `--run-dir outputs/runs/semantic-20260923-enriched-preparation-v2`. This is not a directive to spend on all 28 papers before a separately identified pilot. Source enrichment, semantic extraction, canonical alignment and synthesis integration still need actual controlled execution and review.

## Verification at the original V1 implementation checkpoint

Forty-five repository tests pass, including 13 new semantic-runner cases (parameterized cases counted separately). Cases exercise offline API exclusion, prompt-field isolation, typed critic coverage, endpoint rejection, unlocated relation evidence despite AI support, hypothesis provenance, synthetic end-to-end export, non-overwriting preparation, frozen input/code tampering and invalid selections/budget paths. One pre-existing pytest warning concerns missing asyncio configuration support; these tests are synchronous. Targeted Ruff F/I checks pass.

Headless Chrome checks exercised a clearly synthetic two-entity/one-assertion example, search, opened assertion anchors, source-page navigation and the real prepared-pilot state. No severe browser errors occurred; the synthetic screenshot was visually inspected. The synthetic records live under `tmp/semantic-ui-qa/`, not in research outputs.

`outputs/research_audit/semantic-preparation-20260923.json` records zero API calls, 20 matching raw-PDF hashes, matching metadata identity, three frozen packet hashes and unchanged evaluation-v2 code/dependencies. These are engineering observations, not research accuracy scores. Source extraction quality, critic reliability, full-corpus coverage and human validation still need actual execution and evaluation.
