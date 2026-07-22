# Realist Evidence Synthesis (V2)

> An agentic, human-in-the-loop, GraphRAG-based multi-agent framework for automating
> **realist systematic reviews** in education — the methodological contribution of a
> Review of Research in Education (RRE, Vol. 50, 2026) manuscript. Worked example and
> external benchmark: **Richmond et al. (2020)**, *"The student is key"* (Medical
> Education 54(8):709–719), a RAMESES realist review with 28 included studies.

**This is a research artifact, not a product.** The framework reproduces the analytic
operations of realist synthesis — search, two-stage screening, CMOC (Context–Mechanism–
Outcome Configuration) extraction, cross-study synthesis, programme-theory construction —
under human "master control" at four adjudication checkpoints, with every decision
auditable and every extracted claim span-grounded in its source. A **separate**
verification harness compares system outputs against the human benchmark; it is not part
of the production pipeline.

## Documentation map

| Document | Purpose |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | The seven grounded design decisions, agents, ontology, phases |
| [`docs/research/SOTA_REPORT.md`](docs/research/SOTA_REPORT.md) | Cited state-of-the-art research behind each decision |
| [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md) | Living project memory (goals, professor requirements, status) |
| [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md) | Append-only record of decisions with rationale |
| [`WALKTHROUGH.md`](WALKTHROUGH.md) | Milestone-by-milestone report for non-followers |
| [`config/ontology.yaml`](config/ontology.yaml) | The typed realist ontology (entity types + relation predicates) |
| [`config/models.yaml`](config/models.yaml) | Pinned LLM tiers and budget controls |

## Stack

Python 3.11 · LangChain + **LangGraph** (stateful orchestration, `interrupt()`-based HITL,
Postgres checkpointer) · **Microsoft GraphRAG** (Literature Knowledge Graph: BYOG typed
triples + Leiden communities) · OpenAI GPT-5.4 tier (see `config/models.yaml`) ·
**PostgreSQL** (registry, audit, checkpoints) · **Parquet** (canonical reproducible KG
artifact) · **Neo4j** (derived motif-query & visualization layer).

## Setup (Phase 0)

```bash
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -e ".[dev,viz]"
copy .env.example .env                            # then fill in keys
res --help
```

Corpus (`data/`) is read-only input: 20 full-text PDFs + 8 abstract-only records matching
Richmond's 28 included studies, plus the benchmark paper itself.

## Status

Architecture v1.0 adopted; Phase 0 scaffolding in progress. See `WALKTHROUGH.md` for the
current milestone log.
