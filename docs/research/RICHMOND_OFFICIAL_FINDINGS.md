# Richmond's published findings and outputs

## Main conclusion in plain language

Richmond and colleagues conclude that teaching clinical reasoning depends on the learner's existing knowledge and ability to cope with the task. Effective education develops knowledge acquisition, application and recall while providing practice with real or simulated cases. As expertise develops, students should become able to use non-analytical reasoning and return to analytical reasoning when a case is uncertain, complex or requires an explanation. The review does not identify one intervention that works equally well for everyone. These are the conclusions of a theory-building realist synthesis, rather than pooled experimental estimates of causal effects.[^1]

The central question is therefore: **which educational resource helps which learner, through what cognitive or emotional response, with what consequence?** A useful result must preserve this configuration. A list containing “feedback,” “confidence” and “diagnostic accuracy” does not express the relationship between them.

## Source and reading convention

The authoritative source for this account is the supplied published article: Richmond, Cooper, Gay, Atiomo and Patel (2020), *The student is key: A realist review of educational interventions to develop analytical and non-analytical clinical reasoning ability*, *Medical Education*, 54, 709–719, DOI 10.1111/medu.14137. Journal page 709 is PDF page 1. The supplied PDF has 12 pages, including an additional copyright page. Figures 1–3 have been inspected visually because text extraction does not preserve their boxes and arrows.[^1]

This account distinguishes the authors' findings, the review's methods, and this project's proposed comparison units. The accompanying `gold/richmond_reference_v1.json` is an AI-assisted transcription and decomposition of the published configurations. It is awaiting independent human ratification. Its 18 rows are not a claim that Richmond published “18 CMOCs.” Earlier project files containing 47 entities and 40 relations are also operationalizations, rather than a gold-standard dataset supplied by the authors.

## What Richmond actually produced

| Published output | Location | What it communicates |
|---|---|---|
| Review question and initial programme theory development | pp. 710–711, section 2 | How scoping literature, clinical teaching expertise and learning theories informed the explanatory framework |
| Search and selection flow | p. 711, Figure 1 | Records identified, screened, excluded and added through supplementary searches |
| Definitions of knowledge | p. 712, Table 1 | General knowledge, domain/case-specific knowledge, ability to apply knowledge, and variation within groups |
| Characteristics of the included literature | p. 712, section 3.1; Appendix S2 | Countries, learner populations and heterogeneous outcomes across 28 papers |
| Final synthesis across five student contexts | p. 713, Figure 2; pp. 714–716, sections 3.2.1–3.2.5 | Context–resource–response–outcome explanations, including beneficial and adverse pathways |
| Expanded low-knowledge configurations | p. 715, Figure 3 | Specific facilitating and obstructing pathways for learners with low or hard-to-apply knowledge |
| Interpretation, limitations and recommendations | pp. 716–717, sections 4–5 | Conditional implications for teaching and the limits of theory-based inference |
| Supplementary methods and included-paper material | Appendices S1 and S2, publisher supporting information | Additional search/extraction and paper-level information referenced by the article |

Figure 2 presents the developed student-level programme theory. It must not be labelled the initial programme theory. The paper does not publish a downloadable Neo4j database, machine-readable knowledge graph, similarity score, or classifier accuracy against human coding. NVivo 12.1.0 and Excel supported the authors' analysis; those tools are not themselves the scientific output.[^1]

## Scope and evidence base

The structured searches covered MEDLINE, PsycINFO, ERIC and CINAHL in May 2017, starting with publications from 2000. Figure 1 reports 3,066 + 2,779 + 1,037 + 745 = 7,627 records. Removing 530 duplicates left 7,097 titles/abstracts. Removing 6,958 and adding 10 supplementary-search records led to 149 full texts considered for eligibility. Of these, 124 were removed, leaving 25; two reference-list additions and one subsequent knowledge-retention search addition produced 28 included papers. Reasons for full-text removal overlap and must not be summed as mutually exclusive categories.[^1]

The article reports 23 medical-education studies, one veterinary-education study and four studies with psychology students, with 1,495 participants in total. These are the authors' reported aggregate characteristics. “28 papers” should not be rephrased as “28 independent medical randomized trials.” Shared samples and secondary reports require attention in a computational replication.[^1]

Diagnostic accuracy was a primary endpoint in 13 studies; seven reported satisfaction, seven knowledge change, and five described interventions theorised to develop illness scripts and non-analytical reasoning. Some studies contributed several outcomes. One contributed potential mechanisms without reporting outcomes. Consequently, satisfaction, measured accuracy, knowledge retention and theorised future reasoning must remain different outcome types.[^1]

## The five overlapping contexts

### 1. Low knowledge or difficulty applying knowledge

This includes low general knowledge, low domain/case-specific knowledge, and having knowledge but being unable to apply it in a reasoning situation. It is not simply another name for an early year of study. Twenty-two papers contributed to this part of the theory; the context had the widest influence across interventions (section 3.2.1, p. 714).[^1]

Figure 3 contains five facilitating resource branches. Near-peer reasoning with examples and prompts may help learners feel at ease because the peer seems to have similar prior knowledge. Combined analytical and non-analytical instructions may help learners trust familiarity while developing their ability. Accurate timely feedback and clear expert explanations can each provide clarity and understanding. A stepwise analytical scaffold may relieve the tension of not knowing the answer immediately. These responses are linked in the figure to improved learning or diagnostic accuracy.[^1]

The same figure contains five obstructing branches. Time pressure deliberately forcing non-analytical reasoning may elicit guessing, frustration and distress. Passive expert observation without reasoning explanation may elicit panic or resentment. Expert explanations that skip steps or use difficult-to-understand pattern recognition may be discordant with a learner's illness scripts. More difficult cases can elicit frustration. Passive listening to peer explanations containing errors can elicit confusion. These are linked to poorer learning or accuracy.[^1]

The critical distinction is the resource actually delivered. “Listening to an expert explain reasoning” is not the same exposure as “watching an expert without any explanation.” Similarly, a peer model with prompts is not interchangeable with passive exposure to an erroneous peer explanation. A comparison system that merges these interventions destroys the finding it is meant to verify.

### 2. High domain-specific knowledge

Seven papers contributed. When expert reasoning is revealed and discussed, learners with sufficient relevant knowledge can understand the reasoning process and gain a positive learning experience. However, requiring analytical reasoning alone or overthinking familiar cases can provide little additional benefit. Such learners may feel frustrated while still attaining high accuracy through non-analytical reasoning (section 3.2.2, p. 714; Figure 2).[^1]

Figure 2 emphasizes maintained accuracy with limited or no added learning benefit. The narrative describes frustration and reliance on non-analytical reasoning. These descriptions should be reconciled, not converted automatically into “analytical reasoning reduces accuracy.” No added benefit is different from demonstrated harm.

### 3. Positive coping and appropriately calibrated confidence

Five papers contributed. Learners who can cope with the task, or whose confidence/self-efficacy is appropriate to their performance, can benefit from real or simulated experiences that permit mistakes. Feeling safe or grateful and developing understanding can support learning, more complete illness scripts and more accurate non-analytical reasoning. In real cases, responsibility and pressure may also be experienced as a positive part of learning (section 3.2.3, pp. 714–716).[^1]

The condition is not “more confidence is always better.” Calibration and coping matter. Nor is the finding “stress is always harmful”: the meaning and demands of the situation affect how the learner experiences it.

### 4. Negative coping or insufficient confidence

Four papers contributed, alongside cognitive-load and stress-response theory. Real or simulated encounters may evoke fear, stress or pressure in learners who cannot adequately cope. Increased cognitive load is proposed to impair illness-script development, future non-analytical reasoning and learning (section 3.2.4, p. 716).[^1]

This is an explanatory synthesis. It should not be reported as though every supporting primary paper measured every link, including future illness-script impairment. The comparison must indicate which part was observed, which was proposed by a primary author, and which was inferred in the review.

### 5. Different knowledge levels within a group

Nine papers contributed. Retention-oriented teaching can build on existing knowledge and understanding across heterogeneous groups, supporting learning and engagement. Accurate timely feedback helps learners understand successes and failures and plan improvements, with implications for illness scripts and future non-analytical reasoning. Absent, incomplete or incorrect feedback can produce confusion and poorer learning (section 3.2.5, p. 716).[^1]

These pathways overlap with some low-knowledge findings. The five context groups are not disjoint bins into which every paper or learner is assigned exactly once. The contributing counts 22, 7, 5, 4 and 9 must not be added to estimate the size of the corpus.

## How the authors reached these conclusions

The team developed an initial theory from background literature, experience and consensus, drawing on dual-process, cognitive-flexibility and situativity perspectives. They searched for relevant evidence and assessed whether methods were credible enough for the contribution being made. AR performed initial CMOC coding; section 2.2 states that all 28 articles were checked for consistency by another reviewer. The author-contribution statement separately mentions review of a sample of full texts. Neither passage supplies an inter-rater reliability coefficient.[^1]

The team compared recurring configurations, revisited earlier papers as explanations emerged, and combined evidence that illuminated different parts of a configuration. A source could contribute context without documenting the entire mechanism–outcome chain. Mechanisms could be inferred using theory. The final explanation was refined through team feedback. A faithful computational analogue therefore needs revisiting, explicit inference records, rival explanations and accountable human review, rather than merely a sequence of extraction calls.[^1]

## Limits on what can be concluded

The review mainly found student-level evidence. Limited teacher/organizational reporting does not establish that those levels are unimportant. The findings are contingent explanations, not universal effect sizes or a validated prediction rule for individual students. Under-reporting sometimes required theoretical inference. The conclusions support adaptation to learner knowledge and coping, but do not warrant an unconditional ranking of teaching methods.[^1]

The original appendices are referenced in the paper and listed on the publisher's site as two DOCX supplements. They were not present in the supplied repository. Direct retrieval of both publisher files returned HTTP 403 during this audit. Their contents have therefore not been inspected, and no claim is made to have reproduced the authors' complete extraction sheets or original search syntax.[^2]

## An explicit comparison target

The versioned reference catalog decomposes Figure 3 into ten low-knowledge branches and sections 3.2.2–3.2.5 into eight additional branches. It retains context, resource, response, outcome, direction and a page/section anchor. Overall recommendations in section 5 are evaluated narratively as programme-theory implications, rather than added as duplicate configuration rows.

For each row, a new system result can be judged equivalent, partially equivalent, contradictory, not recovered, or uncertain. Equivalence requires preservation of the causal explanation and its conditions; shared words are insufficient. A response may be plausible but inferred, and an outcome may be perceived rather than measured. These distinctions belong in the matrix and the human judgment. Agreement with Richmond is one form of methodological correspondence; independent source support and defensible departures are also required for trustworthiness.

## Sources

[^1]: Richmond A, Cooper N, Gay S, Atiomo W, Patel R. *The student is key*. Medical Education. 2020;54:709–719. [DOI](https://doi.org/10.1111/medu.14137). Primary source inspected: supplied `data/paper-Richmond-original.pdf`, journal pp. 709–719, including visual inspection of Figures 1–3. Detailed paraphrases above derive from this user-supplied file.
[^2]: Wiley, [article supporting-information listing](https://asmepublications.onlinelibrary.wiley.com/doi/10.1111/medu.14137), accessed September 2026. Listed files: `medu14137-sup-0001-Supinfo1.docx` and `medu14137-sup-0002-Supinfo2.docx`. File contents inaccessible in this audit.
