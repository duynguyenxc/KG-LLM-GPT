# September research run: observed results and continuation

## What exists now

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
