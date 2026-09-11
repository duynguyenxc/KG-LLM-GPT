# Existing outputs and preliminary-results corrections

## What exists before the new experiment

The repository contains actual historical extraction and synthesis results. It also contains several generations of reports whose numbers and interpretations differ. A report file is not proof that a specific experiment was run under the code currently checked out. The most recent inspected historical verification artifact is `outputs/runs/verify-15b50105/verification_report.json`; the legacy graph exports contain corresponding substantive records. The pilot is stored in `outputs/runs/evidence-20260910-v1/`; the clean full-corpus attempt is separate in `outputs/runs/evidence-20260910-full/`.

| Existing artifact | Format and location | What a reader can obtain | Audit qualification |
|---|---|---|---|
| Extracted configurations | `outputs/lkg/cmocs.parquet` | 91 CMOC records, including paper identifier, polarity and narrative | 26 of 28 paper records contribute CMOCs; extraction is not completed human coding |
| Entity instances | `outputs/lkg/entities.parquet` | 517 instances, 180 canonical identifiers, quotes and metadata | Some canonical mappings erase meaning or polarity; source location is not entailment |
| Relations | `outputs/lkg/relationships.parquet` | 439 relations and source associations | 437 are marked constraint-valid; type constraints are structural checks |
| Concept families | `outputs/lkg/communities.parquet` | 43 family records | These are not the same objects as the eight reported Leiden communities |
| Latest historical verification | `outputs/runs/verify-15b50105/verification_report.json` | Metrics and model-generated matching explanations | Policies differ across metrics; semantic judgments need ratification |
| Readable professor report | `outputs/Professor_Report.html`, `.pdf`, `.docx` | Narrative summary, diagrams and headline numbers | Some claims overstate validation or misinterpret missing concepts |
| Older preliminary report | `outputs/Preliminary_Results_Report.docx` | Earlier narrative results | Contains an older 86-CMOC state; do not combine with 91-CMOC results without versioning |
| Preliminary submission material | `outputs/submission/`, `outputs/submission_v2/` | PDFs, copied raw exports and correspondence documents | Historical delivery snapshots; preserve unchanged |
| AERA draft | `outputs/AERA_2027_Preliminary_Paper_FILLED.docx`; final copy under `outputs/submission_v2/` | Draft claims and paper inserts | Contains statements about human review that are not established by completed local coding forms |
| Human concept/relation forms | `outputs/human_validation_concepts.csv`, `outputs/human_validation_relations.csv` | Proposed rows for adjudication | Verdict fields are blank |
| Two paper-coding workbooks | `outputs/gold/per_paper_coding_coder_A.xlsx`, `...coder_B.xlsx` | Instructions and candidate coding | Human coding fields are blank; identical copies do not establish two independent reviews |
| Legacy CSV exports | `outputs/exports/*.csv` and submission copies | Intended portable tabular outputs | Data rows repeat column names instead of values; these copies cannot be used as reliable evidence matrices |

The historical Parquet files have been inspected as data, rather than inferred from their filenames. Submission ZIPs and repeated report copies largely duplicate these artifacts. A file-level inventory with hashes is available at `outputs/research_audit/repository_inventory.csv`. It distinguishes credentials and generated cache files from substantive sources/artifacts; an inventory entry alone does not claim semantic review of every byte.

## What the old headline scores actually measure

The latest inspected verification reports 43/47 concept matches, 39/40 type-pattern relation matches, 22/40 anchored relation matches, and 0/40 strict relation matches. These are different definitions. In particular, type-pattern matching can reuse an edge shape without recovering the correct contextual endpoints and causal explanation. Calling 39/40 “97.5% recovery of Richmond's causal reasoning” is therefore not warranted.

The reported 501/517 located spans, approximately 96.9%, measure successful quotation positioning under the old resolver. They do not show that 96.9% of claims are entailed, that every quote is an exact unmodified source span, or that every inferred mechanism was observed. The new experiment separates location, machine support review and human judgments.

The historical programme-theory correspondence scores average approximately 0.5392 across the five coded reference chains. Those reference chains do not fully preserve Richmond's five published contextual groupings. A model-produced similarity score against an imperfect operationalization cannot be treated as expert acceptance of the programme theory.

Screening reports also refer to different policies. The recall-first experiment and precision-first experiment use different decisions and cannot supply the sensitivity and specificity of one classifier. A 100% result after delegated adjudication does not establish unaided screening recall or independent human review. A constructed distractor set is not the original 7,097-record screening population.

## Demonstrated semantic problems

Some legacy normalization/matching decisions confuse overload with cognitive-load reduction, increased time spent learning with reduced learning, and increased errors with error reduction. Other matches treat spontaneous reasoning as analytical-only reasoning, or passive exposure without explanatory support as equivalent to an explicit reasoning explanation. These errors matter because they change the educational explanation while potentially increasing label correspondence.

The historical explanation that emotional or confidence-related concepts are missing because the available corpus contains essentially no relevant text is not supported by a close reading. For example, McGregor's paper discusses emotional responses, confidence, pressure and clinical simulation; the examples/prompts paper also addresses self-efficacy. Missing retrieval or extraction must be distinguished from absent source evidence.

The old relation and concept references are project-created coding schemes. Some incorrect mappings appear in the per-paper AI coding as well. Comparing one AI's output against another AI's coding is useful for finding disagreements, but is not independent human validation. The published review remains an external human synthesis, while the project's decomposition of it still requires careful checking.

## Corrections needed in a scientific account

1. Replace unsupported statements of completed human review with the actual status: local records contain AI-assisted judgments and pending human ratification. If human reviews occurred outside this repository, their dated coding and adjudication records are needed before reporting them as evidence.
2. Label span-location rates as location checks. Claim support requires separate evaluation against the source and its context.
3. Report strict, anchored and type-pattern matches separately, with their exact definitions and limitations. Do not use the most permissive percentage as complete causal-configuration recovery.
4. Use one identifiable run and corpus state for each results table. Explain older 57-, 86- and 91-CMOC versions rather than mixing them.
5. Describe the available corpus accurately: 19 apparently full-text PDFs, one one-page PDF and eight short metadata/abstract snippets. Availability is not equivalent to 28 complete primary papers.
6. Remove assertions of observed fine-tuning, RLHF, complete GraphRAG execution, human time savings or completed ethical determinations unless the corresponding records actually exist.

These corrections are an audit record, not a replacement of historical submissions. No journal or professor has been contacted automatically, and the previously delivered files remain preserved. Any external correction should be based on the final audited figures and the research team's decision.

## What the new output is designed to look like

On completion, the exporter will produce a readable `report.html`, an `evidence_matrix.csv` with one finding per row, a `programme_theory.csv` with one provisional explanation per row, and a `comparison_matrix.csv` with one Richmond reference configuration per row. Each comparison includes the actual system counterpart, source quotations, six dimension-level judgments and blank human verdict fields. JSON files preserve full provenance; raw model calls are saved for inspection.

The September attempt currently stopped on a provider `credit_balance_exhausted` response. Its actual available outputs are `progress.html`, `partial_evidence_matrix.csv`, `paper_progress.csv`, `comparison_plan.csv` and `progress.json`. Nineteen papers have extraction responses; seventeen completed source audits contain 86 findings, of which 83 pass the machine gate. No new final programme theory or comparison verdicts exist yet. Blank comparison cells mean the stage was not executed, not that Richmond's conclusions were not recovered. See `CURRENT_RUN_RESULTS.md` for the reproducible checkpoint and resumption command.

This answers the practical output question: the scientific result is a set of conditional explanations and their evidence trail. The graph is a supporting representation. The matrix is the instrument for comparing the explanations, and the HTML report is the accessible view. An output can be readable and reproducible while still requiring human validation; those properties should be reported separately.

## Evidence locations

Primary audit inputs are the historical verification JSON, the four Parquet exports, the human forms, the supplied Richmond PDF, corpus PDFs, implementation modules and report-generation scripts. Richmond's correct findings are documented in `RICHMOND_OFFICIAL_FINDINGS.md`; the comparison protocol and algorithm are in `METHOD_AND_VERIFICATION_PROTOCOL.md`. The exact machine results of the new experiment are recorded in that run's `metrics.json`, rather than copied into this historical audit before execution is complete.
