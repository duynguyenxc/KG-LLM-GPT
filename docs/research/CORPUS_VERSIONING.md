# Frozen corpus supplementation

## Actual state

`outputs/runs/corpus-20260923-abstracts-v1/` is a prepared source version with 28 paper records: 19 unchanged full-text records, eight complete abstracts replacing metadata snippets, and one partial PDF plus abstract (S009). No additional full-text PDF was acquired. No existing baseline input, finding, programme theory or reference was overwritten.

`outputs/runs/semantic-20260923-enriched-preparation-v1/` contains 28 frozen extraction packets produced from this corpus by the existing semantic runner. Its status is `prepared_not_executed`: zero calls, zero completed extractions and no new scientific result. Open either directory's `index.html`; the semantic directory also contains readable source text under `sources/`.

## What the implementation guarantees

`res_pipeline.evidence.corpus` performs offline preparation only. Before creating a destination it checks the acquisition checkpoint against the baseline, raw XML and parsed-record hashes, known/unique paper and PubMed IDs, source-page completeness, exact abstract sections against the primary XML and DOI identity. When PubMed omits a DOI, the normalized article title must match the baseline; S010 additionally retains the preceding assistant identity review. These checks protect record identity, not research validity.

Supplements can replace only a metadata snippet or extend a partial PDF. Existing full-text records and extracted pages are preserved. For partial PDFs, the original page text is retained before the added abstract. Empty abstracts, duplicate records, mismatched identities, altered abstract text, unsafe paths and existing destinations are rejected. Assistant acquisition notes, historical findings and the Richmond reference are not supplied to extraction: the existing runner's explicit packet whitelist is retained.

The new version includes byte-preserved parent snapshots, raw acquisition XML, parsed abstract snapshots, source bundles, a source locator map, model configuration, builder snapshot and hashes. Configuration retains prior budget-run references and adds the parent baseline so future execution remains accountable to the existing shared software budget. This does not establish the balance of the API account.

## Citation meaning

The existing schema calls its locator field `page`. For this corpus it identifies a **source unit**, not necessarily a PDF page. `source_locators.json` is authoritative: an abstract unit has `original_page: null`, a PubMed identifier and source URL. S009 unit 1 is its original partial PDF page; unit 2 is the abstract. Do not report a unit-2 quotation as occurring on PDF page 2.

The preserved V1 semantic viewer uses the generic label “Source page”. The subsequent V2 implementation resolves and freezes locator types, supplies them to the model and displays explicit PDF/partial-PDF/abstract/metadata labels. `outputs/runs/semantic-20260923-enriched-preparation-v2/` is prepared with all 28 packets; it has not executed. Locator provenance is retained in evidence JSON/CSV/graph and the correspondence reviewer. Older historical finding/theory reports remain unchanged; this is not a retrofit of their citations. Read `SEMANTIC_EXTRACTION_RUNBOOK.md` for the current contract and frozen replay.

## Reproduction and execution boundary

Choose a new destination to reproduce the corpus:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
& 'C:/Users/Admin/AppData/Local/Programs/Python/Python311/python.exe' -B -m res_pipeline.evidence.corpus --baseline outputs/runs/evidence-20260910-full --acquisition outputs/research_audit/source-acquisition-20260923/source_acquisition.json --output-dir outputs/runs/corpus-NEW
```

The historical V1 offline preparation command was (do not use current code to recreate that frozen identity):

```powershell
& 'C:/Users/Admin/AppData/Local/Programs/Python/Python311/python.exe' -B -m res_pipeline.evidence.semantic_pipeline --source-run outputs/runs/corpus-20260923-abstracts-v1 --output-dir outputs/runs/semantic-20260923-enriched-preparation-v1 --budget-run evaluation-20260923-v2 --budget-run semantic-20260923-pilot-v1
```

There is no `--execute` in this command. Use `python -B -m res_pipeline.evidence.replay_semantic --run-dir outputs/runs/semantic-20260923-enriched-preparation-v1` to inspect its identity with frozen code. Paid execution remains pending credit restoration and should start with a separately named pilot before a full new extraction. A different paper selection, source version or prompt requires a distinct run. Do not change the prepared 28-paper selection in place. Do not invoke the historical `evidence.pipeline` loader on the supplemented directory: it rebuilds its original registry and is not the source loader for this version.

The enriched semantic runner currently extracts entities/assertions and performs AI source review. It does not by itself complete canonical alignment, graph-integrated programme-theory synthesis, the full proposal's training experiments or human verification. Those requirements remain outstanding.

## Scientific interpretation and evidence

Source enrichment and algorithm improvement are separate factors. Comparing this new semantic runner with historical July extraction or September finding synthesis would change both source and method. A source-effect claim needs paired runs under the same method/model/prompt/reference/rubric, with repeated-run uncertainty and development selection disclosed. No such measured effect is reported here.

Nine new synthetic tests cover preservation and rejection cases and exercise the real offline semantic preparation path without an API client. The repository suite reached 75 passing tests; the existing pytest `asyncio_mode` configuration warning remains. Targeted Ruff F/I checks pass. Actual checks verified all 28 packet hashes, nine source bundles, six unchanged baseline hashes, prior evaluator/pilot code hashes, S009's retained page, report navigation and browser errors. The corpus report was visually inspected. Evidence: `outputs/research_audit/corpus-enrichment-20260923-qa.json`.

The explicit source-locator display is now implemented and technically checked in V2, with no actual new extraction. Next: obtain further full texts when lawful access is available; run a controlled pilot after credit restoration; inspect source support and errors before broader execution and synthesis integration. Human forms remain blank until real reviewers contribute.
