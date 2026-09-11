# Realist evidence synthesis

This repository investigates a researcher-controlled agent method for realist evidence synthesis under Wei Zheng's accepted RRE proposal. Richmond et al. (2020), *The student is key*, is the worked example and external human synthesis. The research output is a set of conditional explanations with an inspectable evidence trail and a defined human evaluation protocol.

## Current status

The September 2026 audit found substantive problems in historical verification claims and CSV exports. An isolated evidence-preserving implementation and a three-paper pilot are available. The clean full-corpus attempt stopped because the OpenAI API returned `credit_balance_exhausted`: 19 papers extracted, 17 source audits completed, 86 audited findings and 83 machine-eligible findings. A new final programme theory and Richmond comparison have **not yet been generated**. Independent human validation remains pending.

Open the local [actual progress report](outputs/runs/evidence-20260910-full/progress.html) and [current results/continuation record](docs/research/CURRENT_RUN_RESULTS.md). Run files and private research inputs are excluded from Git; their local links require the research workspace.

## Start here

| Document | Purpose |
|---|---|
| [Richmond's official findings](docs/research/RICHMOND_OFFICIAL_FINDINGS.md) | Published outputs, five contexts, branches, exact pages and limitations |
| [Method and verification protocol](docs/research/METHOD_AND_VERIFICATION_PROTOCOL.md) | Primary research, exact algorithms, tool choices and six-dimension comparison |
| [Historical output audit](docs/research/OUTPUT_INVENTORY_AND_CORRECTIONS.md) | Actual files, defective exports and unsupported preliminary claims |
| [Current run results](docs/research/CURRENT_RUN_RESULTS.md) | Observed counts, interruption and executable resume command |
| [Reading coverage](docs/research/READING_COVERAGE.md) | What was reviewed and what an inventory does not establish |
| [Research continuity](docs/research/RESEARCH_AUDIT_STATUS.md) | Active task, decisions, unresolved work and source hierarchy |
| [Decision log](docs/DECISION_LOG.md) / [Walkthrough](WALKTHROUGH.md) | Dated changes; earlier entries are historical |

The reference in `gold/richmond_reference_v1.json` contains an explicit 18-row operational decomposition awaiting expert ratification. It is not a machine-readable gold standard supplied by Richmond.

## Implemented experiment

`src/res_pipeline/evidence/` contains typed extraction, exact/typography-preserving citation location, source-line repair, a separate source critic, a NetworkX evidence graph, seeded Louvain grouping, BM25 page retrieval, bounded synthesis/refinement, isolated comparison and human-review exports. Source snippets and missing evidence remain labelled. Requests, responses, hashes, code snapshots and token estimates are retained per run.

The current stack is Python 3.11, Pydantic, pypdf, NetworkX and the OpenAI SDK. Extraction/synthesis use pinned GPT-5.5; repetitive source audit/comparison use pinned GPT-5.4 mini. JSON/JSONL, CSV and HTML provide run-local persistence and readable outputs. See `config/evidence_run.json` for exact snapshots and budget parameters.

This is a custom graph-assisted baseline. Full Microsoft GraphRAG execution, graph-guided extraction, learned domain adaptation, RLHF and complete interactive human checkpoints are not established by this run. Legacy PostgreSQL/Neo4j/Parquet modules and historical reports remain preserved for inspection.

## Local use

Install the project in a Python 3.11 environment with `pip install -e ".[dev,viz]"`, and configure the private `.env` from `.env.example`. Supply the authorized private corpus separately. Do not commit credentials or source PDFs.

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -B -m pytest -q
python -B -u -m res_pipeline.evidence.pipeline --run-dir outputs/runs/NEW_RUN_NAME
```

Use a new run name for a new protocol or source state. For the interrupted September experiment, follow the specific resume instructions in `CURRENT_RUN_RESULTS.md` after restoring API credit. Do not interpret tests passing or model judgments as independent scientific validation.
