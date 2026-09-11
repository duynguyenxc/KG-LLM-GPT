# Research audit and implementation status

## Active request

The September 2026 request authorizes a continuous end-to-end review, primary-literature research, implementation, execution, and delivery of readable, evidence-linked outputs that can be compared with Richmond's human synthesis. Project artifacts are in English. The central deliverables are an accurate Richmond reference document, an honest inventory of existing outputs, a justified algorithm and architecture, and an executed comparison package with explicit human-review status.

## Current state: API execution blocked; research work preserved

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
