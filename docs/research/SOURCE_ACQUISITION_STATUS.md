# Supplemental source acquisition, 23 September 2026

## Observed result

Nine complete author abstracts were captured from PubMed's public EFetch XML endpoint for S001, S002, S003, S007, S008, S009, S010, S012 and S014. This supplements eight metadata snippets and one partial PDF. **No new local full-text PDF was acquired and no production source or result was replaced.**

Open `outputs/research_audit/source-acquisition-20260923/index.html` for the article-by-article source status, original-versus-new text lengths, public links and assistant observations. `source_acquisition.json` records the acquisition and frozen baseline hashes. Human judgments remain absent; this is source preparation, not a new extraction, synthesis or evaluation result.

## Evidence and access limitations

The private local source directory is `data/source_acquisition/20260923-pubmed/`. It contains:

- `pubmed_batch.xml`: the unmodified response for all nine records, 50,534 bytes, SHA-256 `4eee2c88aad5dd9ea7606927000e3551631afc6cd383db76e4385ec6754e3c74`.
- Nine `Sxxx_abstract.json` records with labelled abstract sections, article identity, source URL, raw-response hash and explicit `abstract_only` availability.
- `acquisition_manifest.json`: the earlier HTML attempt, including unsuccessful responses. It is preserved as an attempt record rather than overwritten to look successful.
- `acquisition_run.json`: provenance for the successful XML route and the report builder snapshot.

Eight XML records have DOI and PMID matches. S010 omits its DOI in PubMed XML; its PMID, normalized title and authors were checked against the observed primary record and article. This is assistant identity checking, not human ratification. Indexing publication types are retained as metadata, not automatically accepted as study-design evidence.

The S010 author-shared PDF was readable as 13 pages of web-extracted text. The local download returned HTTP 403 and the attempted figure/table screenshots did not produce inspectable images. Accordingly, neither a local full-text hash nor successful visual review is claimed. The university copies for S010 and S014 explicitly restrict access. An institutional catalogue record, a PSNet summary, a search snippet and a related publication are not substitutes for the requested article.

This was a targeted search for nine already-known records, not a comprehensive database search, screening experiment or proof that other lawful copies are unavailable. No access restriction was bypassed, no author was contacted, and no source material was added to Git. The separate source directory is not loaded by any frozen production run.

## Why this changes the next action

Source incompleteness is now directly observable, rather than merely assumed. The new material supplies distinctions that the original snippets could not support. The report records these as review issues without rewriting previous findings or treating hindsight as extractor error. It separates a source-coverage limitation from an extraction mistake, synthesis overstatement and disagreement with Richmond.

Before a new paid experiment, select and freeze a new corpus version. Prefer inspected full texts; otherwise label complete abstracts honestly and preserve the partial PDF for S009 alongside its abstract. Validate article identity, page extraction and source availability. A new source snapshot requires a new run: do not resume an existing run after replacing its inputs.

To estimate the benefit of source enrichment, hold model, prompts, configuration, reference version and evaluation rubric fixed as far as practicable; record unavoidable changes and repeatability limits. Separately test algorithm changes. No improvement in recovery, citation faithfulness or human agreement can be claimed from this acquisition alone. Human reference ratification and independent source-support review remain pending.

## Verification and continuation

The nine parsed records and their hashes were checked; all abstracts were read. Six baseline source/configuration/result hashes match the previously recorded values. Browser checks verified nine article cards, the S010 anchor, no horizontal overflow and no severe browser errors; the report was visually inspected. QA is in `outputs/research_audit/source-acquisition-20260923/qa.json`. No production code changed, no model API call occurred and no new pipeline test result is claimed.

Next: obtain inspectable full-text files through lawful access where available, then build an explicitly versioned corpus-enrichment experiment. The frozen semantic pilot and evaluator-v2 experiment still await confirmed API credit restoration; their identities must remain unchanged if resumed. Missing reviewers prevent claims of independent human validation. The full research objective remains incomplete.
