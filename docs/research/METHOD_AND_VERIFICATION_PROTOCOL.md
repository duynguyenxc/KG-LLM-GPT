# Evidence-preserving realist synthesis and verification

## Research question and contribution

The research question is whether a controllable agent workflow can perform the analytic operations of a realist evidence synthesis and produce explanations that experts can inspect, challenge and compare with a published human synthesis. Richmond's clinical-reasoning review is a worked example. The contribution must be demonstrated through traceable analytic decisions and evaluation of the resulting explanations. A running interface, a dense graph or a high label-overlap score alone does not answer the research question.

The accepted RRE proposal describes researcher-controlled roles, an educational literature knowledge graph, graph-enhanced retrieval, domain adaptation and evaluation at module and system levels. Meetings distinguish two experiments: recovering the original included literature through searching/screening, and reconstructing the synthesis on the fixed included corpus. They also permit architectural adaptation while maintaining the methodological aim. These commitments are design requirements, not evidence that every proposed component already exists.[^1]

The immediate experiment uses the fixed 28-paper registry and explicitly reports document availability. It does not claim to repeat four subscription-database searches or reconstruct a complete historical screening population. Retrieval and screening require their own dated exports, search syntax, inclusion decisions and denominators. This separation prevents an apparent synthesis success from concealing a retrieval failure, or an artificial screening pool from being presented as the original review.

## Evidence from related research

| Source | Finding relevant to this project | Decision and boundary |
|---|---|---|
| RAMESES realist-synthesis reporting standards | Transparent explanation of selection, appraisal, extraction and iterative synthesis is central; findings include articulated inferences, not only extracted observations.[^2] | Preserve the chain from source to inference and explain contingent recommendations. A report satisfying a checklist is not automatically a valid synthesis. |
| Dalkin et al., mechanism conceptualization | Separating intervention resources from participants' reasoning helps operationalize mechanisms; activation may vary continuously rather than operate as a simple binary switch.[^3] | Represent resource and response separately. Do not treat an intervention label as a complete mechanism or a graph arrow as a measured causal effect. |
| Microsoft GraphRAG | Graph-based community summaries support corpus-level, query-focused summarization.[^4] | Use graph-organized evidence summaries as an inspectable retrieval/synthesis component. Its summarization results do not establish realist validity or faithful causal reconstruction. |
| PaperQA2 | Evaluates retrieval, cited synthesis and contradiction detection with task-specific human comparisons.[^5] | Adopt explicit evidence access and separate evaluation tasks. Performance on its tasks cannot be transferred to this corpus or used to claim human equivalence here. |
| LatteReview | Modular agents support review workflows, but screening performance varies by dataset and decision threshold.[^6] | Separate recall-sensitive screening from synthesis. Do not select high recall from one policy and high specificity from another and present them as one operating point. |
| Self-Refine | Iterative feedback and revision can improve outputs on tested tasks without parameter training.[^7] | Permit bounded feedback loops, retain revisions and evaluate their effect. Prompt revision is not fine-tuning or RLHF. |
| Huang et al., self-correction study | Intrinsic self-correction without external feedback is unreliable in the reasoning settings studied.[^8] | A second model opinion is a diagnostic signal. Returning to sources and human adjudication remain necessary. |
| SciFact | Scientific claim verification separates evidence retrieval, stance and supporting rationales.[^9] | Record supporting, conflicting and insufficient evidence distinctly. Verification of an isolated claim does not establish a whole realist explanation. |
| FActScore | Evaluates support at the level of atomic factual claims rather than giving an entire answer one binary judgment.[^10] | Check each component, qualification and citation. Add configuration-level comparison because individually correct fragments can still form an incorrect explanation. |
| Louvain/Leiden research and NetworkX implementation | Louvain partitions can be disconnected; Leiden addresses stronger connectivity properties. NetworkX exposes a seeded Louvain implementation.[^11] | The current diagnostic implementation splits disconnected Louvain groups. It does not claim this is Leiden or that connectivity establishes a coherent theory. |

These sources support specific design principles. They do not jointly prove that this implementation is effective. The scientific claim must come from the project's own measured comparison, including failures and expert judgments. A newer preprint describing multi-agent review automation was also located, but its abstract alone is insufficient to justify changing the architecture or claiming novelty relative to it; it remains a follow-up source rather than a result relied upon here.[^12]

## Unit of analysis and evidence representation

A finding is represented as

`f = (paper, study_family, C, R, M, O, direction, comparator, time, evidence_status, evidence_spans, limitations)`.

`C` is the relevant context; `R` is the resource offered; `M` is the learner's response; `O` is an outcome. This is an operational representation of a realist configuration, not a structural equation that estimates a causal effect. Some fields may be unknown. A paper can illuminate only one part of an explanation, and a conceptual paper can describe a plausible resource or mechanism without an observed outcome.

Each response is labelled reported, author inference, model hypothesis, or not reported. Each outcome is labelled measured, reported perception, author inference, or not reported. These labels prevent an account of enjoyment from becoming an accuracy result and prevent a discussion-section explanation from becoming a measured mediator. Inference remains legitimate, but it must be inspectable.

The source identity includes the PDF hash, paper identifier, PDF page and character offsets. Evidence quotations retain the model-proposed text and, where located, the actual underlying source span. Exact matching is attempted first. Typography normalization permits whitespace, Unicode ligatures and line-end hyphenation, while preserving an offset mapping. It does not permit fuzzy semantic similarity, omission of a negation, replacement of an outcome or selective matching of a convenient substring.

S013 and S020 share a study-family identifier because one report analyzes material associated with the other. Counts of papers, extracted findings, theory statements and independent study families are separate quantities. A high number of extracted findings does not mean a large independent evidence base.

## Precise algorithm

### 1. Freeze the experiment

Read the fixed registry, preserve its historical S001–S028 identifiers, and record hashes and availability. Correct the visibly erroneous Linn title/year without renumbering the registry. Snapshot the configuration and actual execution code identity. Store each API request, returned model identifier, raw response, parsed response, token use and estimated cost. Reuse a completed call only if its request hash matches.

The source packets contain primary-paper text or the explicitly labelled metadata snippet. They do not contain Richmond's final conclusions, the old 47/40 reference, previous correspondence reports or external comparison judgments. The developer has studied the comparator; consequently this remains a development experiment, not a pristine unseen benchmark. In addition, model pretraining may contain the public review. Prompt isolation cannot rule that out.

### 2. Extract and inspect findings

For each paper, the extraction model proposes structured findings from the complete available text. Zero findings are allowed. Separate findings preserve differing contexts, comparators and follow-ups. A deterministic locator checks the entire quotation. A citation-repair role selects numbered page/line ranges; code copies those source lines while preserving the claimed component. It cannot rewrite the substantive finding. Missing, invalid or too-short source ranges retain the original unlocated quotation and fail the evidence gate. Raw model proposals remain in the call archive.

A separate critic receives the full available source and the extraction. It assesses every finding, including inference status, direction and qualification. Coverage is checked in code; omitted or duplicate finding indices are not silently accepted. The initial machine eligibility rule is:

`eligible(f) = all_required_quotes_located(f) AND critic_verdict(f) == supported`.

Here “supported” means the finding is defensible with its stated uncertainty and inference labels; it need not describe a fully observed causal chain. This conservative gate can sacrifice recall. Findings assessed partial, unsupported or uncertain remain in the evidence matrix for human inspection instead of disappearing. A high pass rate is not an evaluation target.

### 3. Construct the evidence graph

Each finding is a distinct configuration node connected to its context, resource, response and outcome nodes and their source-evidence nodes. No semantic canonicalization merges opposite concepts. The same lexical label in different findings remains separately attributable. The configuration itself represents the conditional relationship; evidence edges express attribution rather than experimentally established causation.

A separate undirected projection connects findings for retrieval. For token sets `T_i` and `T_j`, its weight is:

`w_ij = size(intersection(T_i,T_j)) / size(union(T_i,T_j))`, provided at least three retained terms overlap.

This Jaccard edge means “candidate for joint inspection.” It does not mean equivalence, corroboration, contradiction or a causal link. Stopword removal and lexical similarity can miss synonyms and connect misleading near-neighbours. All original text and polarity remain available to the synthesis model and reviewer. The threshold is a transparent engineering parameter, not an empirically optimized scientific constant.

The graph projection is partitioned with seeded Louvain modularity optimization, followed by splitting disconnected subsets. The modularity objective has the conventional form `Q = (1/(2m)) sum_{i,j} [A_ij - gamma k_i k_j/(2m)] I(g_i = g_j)`, with the implementation default resolution. This organizes evidence packets. It does not discover “true mechanisms,” and the number of communities is not the number of Richmond contexts.

### 4. Synthesize and return to primary sources

Each community produces a provisional, cited explanatory summary. A reduction stage considers the community summaries together with eligible findings and proposes programme theories. Every theory must cite existing finding identifiers. Each contains a conditional explanation, rival explanations, limitations and evidence gaps. No fixed number or names of context groups are supplied from Richmond.

Theories then generate source-search queries from their contexts, resources, responses and gaps. Page retrieval uses BM25:

`score(q,d) = sum_{t in q} log(1 + (N - df(t) + 0.5)/(df(t) + 0.5)) * tf(t,d)(k1+1) / [tf(t,d) + k1(1-b+b|d|/avgdl)]`.

The configured values are `k1=1.5`, `b=0.75`, with the top eight matching pages per query. Positive-scoring results retain paper and page identity. A bounded refinement pass re-examines these pages, the initial explanations and their underlying findings. New observations without an extracted finding remain gaps requiring extraction/review; they cannot acquire an invented finding identifier.

This is an explicit, restricted operationalization of retroduction: propose an explanation, seek evidence that could qualify it, revisit the source and refine the explanation. It is not a claim to recover a model's hidden internal reasoning, nor a theorem proving the hypothesis. The recorded explanation is a research rationale that can be criticized. One pass does not establish theoretical saturation.

### 5. Freeze production output before comparison

Write the final provisional programme theory and record its hash. Only then load the versioned Richmond reference into the evaluation stage. The comparison stage may identify differences but cannot edit the frozen system theory. Any later modification informed by the comparator starts a new, explicitly labelled development iteration.

## Verification: the answer to “how?”

Verification requires three linked questions. First, **is the system's claim supported by its sources?** Second, **does its conditional explanation correspond to the published human synthesis?** Third, **do independent experts consider the explanation coherent, useful and appropriately qualified?** None of these questions can be replaced by a count of graph nodes.

The comparison matrix has one row per versioned reference configuration. It shows Richmond's context, resource, response and outcome beside the actual system explanation and its evidence identifiers. Six dimensions are judged: context, resource, response, outcome, direction and qualifiers. Qualifiers include population, comparator, time and whether an outcome or mechanism was observed or inferred.

| Verdict | Operational meaning |
|---|---|
| Equivalent | The same conditional explanation is preserved across all six dimensions, with an actual system-theory counterpart and attributable evidence. |
| Partial | Some explanatory content is recovered, but at least one material component or qualification is absent, narrower, broader or changed. |
| Contradictory | Incompatible claims concern sufficiently comparable conditions and outcome definitions. Different contexts, follow-ups or comparators do not automatically qualify. |
| Not recovered | No substantive counterpart appears in the system synthesis. A relevant source finding alone is insufficient if the synthesis never used it. |
| Uncertain | Evidence availability, interpretation or reference ambiguity prevents a defensible decision. |

AI verdicts are explicitly provisional. Code downgrades an “equivalent” verdict if a dimension is non-equivalent, if no system theory/evidence is cited, or if the cited findings are not linked to that theory. This removes certain internally inconsistent verdicts; it does not establish that the remaining semantic judgments are correct.

Two human reviewers should first ratify or amend the reference decomposition, then independently inspect the original paper and the system outputs using blank coder forms. They should not view the AI verdicts before their independent judgments. A later meeting adjudicates disagreements and records the reason, evidence and time spent. Reviewers should also assess system theories absent from Richmond, since a defensible new explanation is not necessarily an error.

The implemented exporter produces a separate `blind_review.html` without AI comparison verdicts, coder A/B CSVs and an adjudication CSV. Re-export preserves existing forms. The review reader requires identifiable reviewers, dates and rationales, and refuses adjudication without both initial ratings. It computes paired agreement only for completed rows and whole-reference recovery only after every reference row is adjudicated. These controls validate record completeness; they cannot authenticate a person's identity or substitute for actual independent review.

After complete adjudication, exact configuration recovery is `number equivalent / number reference configurations`. Report partial, contradictory, not-recovered and uncertain counts separately. Do not silently count partial as exact or assign an arbitrary half-credit score. If only a subset is reviewed, report the reviewed fraction and the sampling design; do not label the subset result whole-corpus recall.

Source-support precision is a different measure: `supported system claims / reviewed system claims`, using independently adjudicated claim-level support. It requires review of generated content, including content that has no Richmond counterpart. Precision cannot be inferred from reference recall. Automated quote-location rate is `located full quotations / all proposed quotations`, and must be labelled as such.

For paired categorical human judgments, Cohen's kappa is `(p_o - p_e)/(1 - p_e)`, where `p_o` is observed agreement and `p_e` is chance agreement calculated from the raters' marginal distributions. Report raw agreement, category counts, disagreements and denominators alongside kappa. With no paired human judgments, kappa and human recall/precision are **not available**, rather than zero or an AI estimate relabelled as human agreement.

## Architecture and tool decisions

The immediate architecture is a source layer, typed finding layer, evidence-graph layer, synthesis layer and separate evaluation layer. Named model roles have explicit inputs and outputs; deterministic Python controls sequencing, schema checks, persistence and budget gates. Different roles do not require different foundation models, and different model names do not establish independent human judgment.

| Component | Current decision | Reason and limit |
|---|---|---|
| Language and contracts | Python 3.11, Pydantic | Fits the existing repository and provides explicit validated data contracts. Schema validity is not factual accuracy. |
| Model access | OpenAI SDK with structured JSON-schema outputs | Record exact requests and returned model identity. API success is separate from scientific success. |
| Extraction and synthesis | GPT-5.5 snapshot `gpt-5.5-2026-04-23`, medium reasoning | Retains the established strong-model choice while making it reproducible; no claim it is optimal for this task. |
| Citation repair, critic and comparator | GPT-5.4 mini snapshot `gpt-5.4-mini-2026-03-17`, medium reasoning | Limits cost for repetitive audit tasks; semantic verdicts still need expert assessment. |
| PDF parsing | pypdf, page-preserving text plus original PDFs | Keeps source addresses; layout and extraction defects must be inspected. |
| Evidence graph | NetworkX and explicit JSON graph | A small corpus can be inspected without a graph server. Lexical grouping is a baseline, not a validated ontology. |
| Retrieval | BM25 primary-page retrieval and graph-community evidence packets | Deterministic and inspectable; synonym recall is a limitation requiring measured comparison with embeddings. |
| Run persistence | Immutable request/response files, JSON/JSONL manifests and CSV/HTML outputs | Isolates the experiment from the mutable legacy PostgreSQL database. Existing PostgreSQL/Neo4j artifacts are preserved. |
| Human-facing output | HTML report, evidence CSV, theory CSV, comparison CSV and separate coder forms | Readers can follow a conclusion to a source without querying a database or understanding graph internals. |

The official model documentation lists structured-output support for GPT-5.5 and standard input/output rates of USD 5/30 per million tokens; GPT-5.4 mini lists USD 0.75/4.50. The budget guard reserves a conservative per-call upper estimate and records actual token-based estimates. Unresolved calls retain a reservation; automatic retries are disabled to avoid silently duplicating uncertain charges.[^13]

This implementation is a **custom graph-assisted synthesis experiment**, not a drop-in implementation of Microsoft's full GraphRAG indexing and query stack. It does not claim that a citation/co-citation network, vector embeddings, link prediction, domain fine-tuning or RLHF has been implemented merely because corresponding packages or proposal paragraphs exist. Domain adaptation in this run is prompt/schema adaptation. The accepted proposal's stronger training claims need either actual training experiments or an explicit methodological revision agreed with the professor.

For a later production system, preserve the same evidence contracts and add genuine human gates and versioned feedback before downstream approval. Graph-guided extraction, approved concept merge/split operations, multiple refinement cycles and resumable human intervention are substantive extensions to evaluate; they should not be claimed complete because a simple workflow can run without stopping. The exploratory machine run keeps every human gate pending and cannot grant itself research approval.

## Experiments needed for a publishable effectiveness claim

The current run can establish that the output exists, is traceable, and can be evaluated with a specified protocol. It cannot by itself establish superiority of multiple agents or GraphRAG. A defensible comparison should hold corpus, model, output schema and budget constant while comparing: direct source-based synthesis; extraction plus source retrieval; and extraction plus graph-organized retrieval and refinement. A separate ablation removes the critic to measure both error reduction and evidence loss.

Reviewers should judge anonymized system variants and the same source corpus using a fixed rubric. Repeated runs quantify stochastic variation. Report cost, review time, recovery, unsupported claims, explanatory completeness and useful departures. Paper families, rather than every extracted node, are the appropriate units for assessing dependence when designing resampling or sampling plans. A small worked example warrants cautious generalization.

Predeclare error categories: unavailable text, parsing error, missed evidence, incorrect context/resource classification, inference inflation, polarity/comparator/time distortion, unsupported cross-paper linkage, synthesis omission, retrieval omission, and ambiguous reference. Investigate disagreements before deciding whether the benchmark, system or both need revision. This is how a result becomes useful research evidence rather than merely a higher score.

## Sources

[^1]: Private project sources: `documents/abstract-from-professor/abstract.md`; January 23, February 4, February 19, May 28 and July 24 meeting transcripts in `transcript-meetings/`; professor briefing documents in `documents/`. These establish intended scope, not empirical performance.
[^2]: Wong G, Greenhalgh T, Westhorp G, Buckingham J, Pawson R. [RAMESES publication standards: realist syntheses](https://link.springer.com/article/10.1186/1741-7015-11-21). BMC Medicine. 2013;11:21. Especially items 8–14 and discussion of inferences and reporting.
[^3]: Dalkin SM et al. [What's in a mechanism? Development of a key concept in realist evaluation](https://link.springer.com/article/10.1186/s13012-015-0237-x). Implementation Science. 2015;10:49. Sections on disaggregating resources/reasoning and continuums of activation.
[^4]: Edge D et al. [From Local to Global: A GraphRAG Approach to Query-Focused Summarization](https://arxiv.org/html/2404.16130v2). Version 2, 2025. Also supplied as `documents/paper-Microsoft-GraphRAG.pdf`. This source evaluates summarization, not the present realist task.
[^5]: Skarlinski MD et al. [Language agents achieve superhuman synthesis of scientific knowledge](https://arxiv.org/html/2409.13740v1). 2024 preprint. Methods and human-evaluation sections; the title is the authors' claim about their tasks.
[^6]: Rouzrokh P, Shariatnia M. [LatteReview: A Multi-Agent Framework for Systematic Review Automation Using Large Language Models](https://arxiv.org/pdf/2501.05468). 2025 technical report. Workflow and evaluation sections. Table 2 and accompanying threshold descriptions contain ordering/reporting inconsistencies; numerical results are not imported as expected performance here.
[^7]: Madaan A et al. [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651). 2023. Feedback-based inference-time revision, rather than weight training.
[^8]: Huang J et al. [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/html/2310.01798v2). 2023/2024 preprint. Scope is intrinsic correction on the reasoning tasks studied.
[^9]: Wadden D et al. [Fact or Fiction: Verifying Scientific Claims](https://aclanthology.org/2020.emnlp-main.609/). EMNLP 2020. Scientific claim stance and evidence rationale task.
[^10]: Min S et al. [FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation](https://aclanthology.org/2023.emnlp-main.741/). EMNLP 2023. Atomic factual support; primarily evaluated on biography generation.
[^11]: Traag VA, Waltman L, van Eck NJ. [From Louvain to Leiden: guaranteeing well-connected communities](https://doi.org/10.1038/s41598-019-41695-z). Scientific Reports. 2019;9:5233. [NetworkX Louvain documentation](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html), accessed September 2026.
[^12]: Ren Z et al. [Systematic Literature Reviews With Two Multi-Agentic Systems And Human-In-The-Loop](https://arxiv.org/abs/2607.21920). July 2026 preprint; discovery-stage source, abstract inspected only, not used to substantiate implementation effectiveness.
[^13]: OpenAI, [GPT-5.5 model documentation](https://developers.openai.com/api/docs/models/gpt-5.5), [GPT-5.4 mini model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-mini), and [Structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), accessed September 2026. Prices are configuration assumptions checked against the official documentation; account billing remains authoritative.
