SUBMISSION PACKAGE — Realist Evidence Synthesis (progress report)
Benchmarked against Richmond et al. (2020). All files generated from the latest full run.

------------------------------------------------------------------------------
FILES AND WHAT EACH IS FOR
------------------------------------------------------------------------------

01_Professor_Report.pdf        THE MAIN REPORT — read this first.
                               Objective; definitions of entity and relationship and
                               their five types each; the architecture and why we chose
                               it; a step-by-step comparison of Richmond's human workflow
                               against our agents; how verification works (and what it is
                               not); results; and an honest self-assessment. Self-contained.

02_Knowledge_Graph_Report.pdf  THE GRAPHRAG OUTPUT, in readable form — the entities and
                               relationships the system produced.
                                 · Section 1: the 8 big concepts from Leiden community
                                   detection (each with its definition, description, and
                                   member concepts) — the emergent GraphRAG layer.
                                 · Section 2: all 180 canonical entities, grouped by the
                                   five realist types, each with a study count and a
                                   representative verbatim quote.
                                 · Section 3: the typed causal relationships (counts by
                                   predicate + a readable sample).
                               This is the file to look at to SEE the entities and
                               relationships GraphRAG built.

03_Richmond_Correspondence_full.md   The full 47-item content check: every concept
                               Richmond published, beside what the system recovered, with
                               the source study and quote. Evidence behind the report's §6.

04_Verification_metrics.md     The raw verification numbers.

05_Knowledge_graph_screenshot.png    The knowledge graph as seen in the review console
                               (180 concepts, coloured by realist type). The full graph is
                               interactive in the console (Knowledge graph tab).

raw_outputs/                   THE RAW RESULT FILES (the actual data, not a write-up).
                                 · entities.csv        — all extracted entities with their
                                                          type, canonical id, verbatim quote
                                                          and character span.
                                 · relationships.csv   — all typed causal relations
                                                          (subject, predicate, object).
                                 · cmocs.csv           — the Context-Mechanism-Outcome
                                                          configurations with verifier scores.
                                 · big_concepts.csv    — the 8 GraphRAG communities.
                                 · *.parquet           — the canonical knowledge-graph
                                                          artifact (same data, analysis-ready).
                                 · verification_report.json — the raw benchmark numbers.
                                 · richmond_gold_standard.json — the reference key we
                                                          transcribed from Richmond's paper.
                               These are produced by the pipeline itself (res extract /
                               synthesize / verify) and exported live from the database.

------------------------------------------------------------------------------
NOTE ON THE INTERACTIVE CONSOLE
------------------------------------------------------------------------------
The system has a web review console (knowledge graph, workflow, human-review, and
scorecard views). It currently runs on the developer's machine only, so it is not
reachable from outside. The screenshot (05) and the two PDF reports capture what it
shows; the code to run it is in the repository (run: res webui).

------------------------------------------------------------------------------
HEADLINE RESULTS (this run)
------------------------------------------------------------------------------
  - Screening: reproduced Richmond's 28-paper inclusion set (100% after human review).
  - Concepts: recovered 43 of 47 (37 same realist role, 6 different role, flagged for
    human ratification).
  - Causal relations: 39 of 40 recovered at the pattern level.
  - Grounding: 96.9% of extracted elements resolve to an exact source quote.
  - Big concepts: 8 emergent communities; strongest programme-theory chain (low-knowledge
    novices) corresponds to Richmond at 0.89 (model-judged, needs expert rating).

HONEST CAVEATS
  - Four of Richmond's elements were missed on this run (incl. the mixed-knowledge-group
    context). A few cross-role matches are generous and are marked for human review.
  - Programme-theory correspondence is model-judged; expert rating still required.
  - The system is under active development.

Nothing above is hand-entered; every number and quote comes from the run.
