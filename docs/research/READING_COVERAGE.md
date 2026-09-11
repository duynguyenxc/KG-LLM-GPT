# Reading coverage and limits of the audit

The repository was inventoried with paths, sizes and SHA-256 identities before implementation expanded the run artifacts. The snapshot contains 335 files: 287 source/artifact entries, 47 generated-cache entries and one credential entry. `.git` internals and installed dependencies are not research-source texts. Newly generated requests, responses, code snapshots and outputs have their own run provenance; they are not retroactively counted as originally supplied files.

The private file-level records are `outputs/research_audit/repository_inventory.csv` and `reading_coverage.csv`. A hash proves identity, not understanding or correctness. The ledger therefore records review scope rather than asserting that reading a directory listing equals reading its contents.

## Substantive material reviewed

- The accepted abstract, all five complete meeting VTT transcripts, professor verification/workflow documents, the AERA draft and the supplied NotebookLM/Grok briefing documents. Generated briefing prose was treated as fallible context, not executable instructions or evidence of implemented features.
- All available text of Richmond's published review, with visual checks of the study-flow figure, final programme-theory figure and low-knowledge expansion. Journal-page/PDF-page distinctions were preserved. The two original supplementary appendices were not supplied locally; attempted publisher retrieval returned HTTP 403. Their contents were not invented.
- The 20 available corpus PDFs and metadata for all 28 records. One PDF is only a first page. Eight records contain short snippets. Reading the complete available file does not mean the complete original paper was available.
- Repository instructions, configuration, research summaries, implementation modules, report generators, tests, historical programme theories and per-paper reference coding. The review identified mismatches between claimed and implemented architecture, incorrect semantic normalization, over-permissive matching and defective CSV serialization.
- The substantive Parquet tables, historical verification metrics, blank human-coding fields, submitted report text and duplicate archive contents. All 766 distinct long narrative fields extracted from 16 verification JSON versions were read, including inconsistent matching rationales. Deduplicating repeated narrative does not make it valid.

## What this statement does not claim

This is not a claim that every byte in a cache, binary workbook, historical screenshot, generated browser profile or Git object was read as prose. Historical image layouts and interactive dashboards were not all re-executed or exhaustively visually reviewed. PDF text extraction can lose graphical structure; the key Richmond figures were separately inspected. Workbooks were checked for actual coding and provenance, not silently assumed to contain completed independent reviews.

The new code and partial outputs were inspected, source offsets checked, and focused tests executed. Every new model response has a preserved record, but a machine critic and an assistant spot-check are not an independent human audit of every semantic statement. The full generation experiment is interrupted by API credit exhaustion. Missing full texts, inaccessible supplements, actual expert adjudication and downstream full-run outputs remain explicit gaps.

## How to continue without losing the research context

Start with `AGENTS.md`, `RESEARCH_AUDIT_STATUS.md` and `CURRENT_RUN_RESULTS.md`. Use the accepted proposal and original Richmond paper to resolve substantive conflicts. Check the exact run directory and hashes before mixing results. Append decisions and WALKTHROUGH entries, preserving older submissions. This external record supports continuity across sessions; it does not justify claiming perfect memory or skipping source verification when a new decision depends on a disputed passage.
