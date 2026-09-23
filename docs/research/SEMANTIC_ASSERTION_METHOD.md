# Source-led conditional semantic assertions

## Decision and research basis

Keep the September baseline intact. Extend the production representation with separately identifiable source entities and conditional assertions. Do not relabel `has_context`, `cites` or lexical-similarity edges as extracted semantic relations. This extension is source-led; Richmond's entity/relation inventory remains external evaluation material.

Nye et al. separate evidence extraction, entity linking and reported-result inference. They emphasize intervention/comparator/outcome combinations and document-level context, and report errors when decreasing an undesirable outcome is confused with a negative effect. Their clinical-trial experiments are not validation of educational realist inference. The useful design implication here is to keep comparator, outcome definition and statistical direction explicit, and distinguish magnitude direction from educational benefit/harm. Their pipeline also illustrates error propagation; competent modules do not guarantee correct end-to-end output. [Primary paper, sections 1.1, 2.2 and 3.2](https://pmc.ncbi.nlm.nih.gov/articles/PMC8378650/).

Luan et al. model entity spans, relations and coreference jointly in SciIE and introduce SciERC. The annotation domain is AI research abstracts, not realist educational evidence. The paper's knowledge-graph construction selects a most-frequent relation between an entity pair. We reject that aggregation rule for this project: different conditions can legitimately yield different relations, and minority adverse/null evidence must remain visible. Their distinction between mentions, relations and coreference informs our separate records; their labels and trained scores are not imported. [Primary paper, sections 3–5](https://aclanthology.org/D18-1360.pdf).

DyGIE++ refines contextual span representations through learned graph propagation for information extraction. Those graph updates are part of a trained extraction model; they are not equivalent to GraphRAG retrieval over our stored evidence graph. Its methodology motivates testing contextual extraction rather than isolated keyword pairs, but does not establish that installing its code or copying a graph schema provides domain adaptation. [Primary paper, section 2](https://aclanthology.org/D19-1585.pdf).

Dagdelen et al.'s structured extraction work and the realist resource/response distinction remain additional foundations described in `METHOD_AND_VERIFICATION_PROTOCOL.md`. The contract below is our design inference from those methods and observed baseline failures, not an algorithm claimed verbatim from any one paper.

## Representation

An entity record identifies a source-specific mention or a labelled source-grounded abstraction, its role, original quotations and page locators. Roles cover context, educational resource, learner response, outcome, population, assessment and study design. An abstraction is not a verbatim named-entity occurrence and must not be counted as span-level NER success. No cross-paper synonym merge is automatically approved by this contract.

A conditional assertion is

`a = (paper, subject, predicate, object, kind, context, comparator, time, outcome_definition, statistical_direction, educational_interpretation, inference_status, relation_evidence, limitations)`.

The graph may display a subject–predicate–object edge pointing to `a`, but the edge does not replace the assertion's qualifiers. The same endpoint pair may have several assertions for different conditions or times. Relation evidence is checked independently from quotations locating the endpoint entities. A quote containing both endpoints is not sufficient proof of the relationship.

`statistical_direction` distinguishes increase, decrease, no statistical difference, mixed, unmeasured and not applicable. `educational_interpretation` distinguishes benefit, harm, no detected difference, mixed, unclear and not applicable. A null statistical contrast cannot automatically become harm or benefit. An author explanation or model hypothesis cannot be labelled as a measured contrast; a compound sentence mixing the two must be split into separate assertions. Missing context/comparator/time must be explicit rather than invented.

## Intended extraction and reasoning sequence

1. Read a page-preserving source packet and identify relevant source spans and constructs, including null/adverse findings and partial configurations. Return entities and assertions jointly so the relation refers to actual local entity IDs.
2. Locate each quotation against the frozen source; preserve exact source spans and any unresolved quotations. Check endpoint identity, duplicate IDs, source availability and direction/inference consistency.
3. Independently assess whether the source supports the asserted connection and qualifications. A located quotation is not a pass on this semantic assessment. Keep rejected/uncertain candidates visible.
4. Propose reversible concept equivalences with explanations; preserve mention identities, role and scope. A shared word, entity type or embedding similarity supplies a candidate, not an accepted semantic merge.
5. Retrieve complete assertion neighborhoods with their conditions and provenance for synthesis. Keep source-reported connections distinct from cross-paper hypotheses. Never promote a predicted missing edge into observed evidence.
6. Evaluate source-span extraction, semantic assertions, global reference recovery and programme-theory correspondence as separate tasks. Record failures at the earliest attributable stage and preserve pre-intervention output.

This sequence is an extension to evaluate, not a statement that every step is implemented. `semantic_contracts.py` currently implements the typed records and offline source/structural audit. Its tests cover missing relation evidence despite located endpoints, dangling endpoints, duplicate identifiers, null-versus-harm mistakes, and inference inflation. No actual semantic extraction, trained entity model, new canonical inventory, relation critic, learned embeddings or link prediction has run under this extension yet.

## Evaluation denominators

The 47/40 project reference concerns recovery of constructs and relationships in Richmond's synthesis. It is not a fully annotated source-span corpus and therefore cannot by itself supply supervised NER/RE precision/recall. Span-level NER evaluation needs source-span annotations. Semantic relation precision needs human judgments on generated assertions, including assertions absent from the Richmond reference. Reference recovery needs a ratified reference and must not combine endpoints from unrelated studies to manufacture a match.

For relation correspondence, compare endpoint meanings, predicate, context, comparator, time, outcome definition, direction and inference status. Report exact strings separately from semantic equivalence and partial correspondence. For a benefit with decreasing outcome magnitude, compare the actual outcome meaning before assigning polarity. Neither an exact anchor check nor passing the new contract tests establishes these judgments.

The next executable extension experiment should pilot joint source extraction and source auditing on contrasting papers, then inspect errors before full-corpus execution. Pilot selection and any changes after reading Richmond are development choices. Effectiveness remains to be tested against simpler source-based and retrieval baselines with a consistent schema, model/budget and independent human rubric.
