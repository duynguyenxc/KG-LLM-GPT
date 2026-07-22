# Richmond's Human Workflow, and How Our Multi-Agent System Mirrors It

_The intellectual backbone of the project. Part 1 reconstructs, from a close reading of the primary
source, **how Richmond and colleagues actually worked** — their division of labour, their
coordination and consensus conventions, and their reasoning moves. Part 2 maps each human operation
to a machine agent. Part 3 is an **honest fidelity audit**: what our system copies faithfully, what
it does not yet, and what it deliberately refuses to copy. Part 4 records what we borrowed from
comparable multi-agent systems. Part 5 is the architecture-cleanup decision list._

_Every claim about Richmond's process is grounded in the primary source: Richmond A, Cooper N, Gay S,
Atiomo W, Patel R. (2020) "The student is key", Medical Education 54(8):709–719. Line references
(Lxxx) point to the extracted full text; section references (§) to the paper's own numbering. Every
claim about what we must deliver is grounded in the professor's own documents (the RRE abstract, the
8-step verification plan) and the 28 May 2026 meeting transcript._

---

## Part 0 — What the professor and the journal actually asked for (the brief)

Before mirroring Richmond, the system must satisfy the brief the professor committed to the journal.
Three authoritative sources define it; they agree, and our reading of Richmond (Part 1) matches them.

**(a) The RRE abstract** (`documents/abstract-from-professor/abstract.md`) — the journal commitment.
It is a **methodological-innovation paper**: an *agentic pipeline for systematic review in education*,
first of its kind for education. Committed components: **specialized agents for screening, coding,
synthesis, contradiction checks, citation validation**; **researcher-definable prompt templates +
rule-based decision logic**; **human–AI collaboration (HITL)**; a **Literature Knowledge Graph (LKG)**
of typed entities+relations; **GraphRAG** retrieval over subgraphs; and — named as the *key conceptual
novelty* — **community-defined conceptual entities**: "emergent, literature-derived abstractions, not
predefined ontologies or keywords." Evaluation is module- *and* system-level against a published
review, with F1 / κ / recall / citation-faithfulness / contradiction metrics + expert-panel judging.

**(b) The 8-step verification plan** (`documents/plan_verification_text.txt`) — the professor's own
statement of Richmond's method as **five operational activities**: (1) iterative, theory-informed
search; (2) screening for explanatory relevance; (3) CMO extraction; (4) cross-study pattern
synthesis; (5) programme-theory articulation — *"leaving normative theory judgment to humans, which is
exactly what realist methodology requires."* This is identical to the workflow we reconstruct in
Part 1 from the paper — independent confirmation that our reading is correct. It also specifies
**community detection (Leiden)** as the concrete mechanism for producing the conceptual entities
(Step 4), and defines success as *structural/conceptual correspondence, not verbatim matching*.

**(c) The 28 May 2026 meeting** (`transcript-meetings/GMT20260528…vtt`) — the professor, in his own
words, pinned down two things our design must honour:
- **Typed, named, directed relations** — he asked pointedly "*do you have a set of relation types
  defined? how do you specify the type of relation? … they have some name — what type of relation?*"
  and wanted them shown with direction on the diagram. → This is *why* we use a **fixed 5-predicate
  typed ontology** with domain/range, not free-form LLM relations. Our D3 decision answers his concern.
- **Seed → iterative modify → human exam** — "*we need some seed, and then we need to go through a
  different modifier … an iterative process … they come out on result and the human exam*" (≈14:20).
  → This is exactly the **IPT-first + retroduction loop + HITL** rhythm (Gaps 1, 2 below).

**The synthesis:** the professor wants **typed relations *and* emergent, community-clustered
conceptual entities** — reconciled by our hybrid ontology (fixed *types*, emergent *instances*, then
clustered). Method must lead, platform must serve, and the human stays sovereign.

---

## Part 1 — What Richmond and colleagues actually did (the human workflow)

A realist review is **not** a statistical meta-analysis. Its goal is a **programme theory**: a set of
statements of the form *"in context C, an intervention offers resource M<sub>resource</sub>, which
triggers response M<sub>response</sub>, producing outcome O"* (a **CMOC** — context–mechanism–outcome
configuration; §2, L138–140). The work is **theory-building, not theory-testing** (L256–258), and it
is **iterative and retroductive**: the theory is drafted early, then repeatedly revised as evidence
accumulates.

### 1.1 The team and its one non-negotiable precondition — domain expertise

All five authors "were **clinical teachers with expertise in the development and education of clinical
reasoning**" (L174–177). This is the single most important and most easily-missed fact: the review
was performed by **domain experts**, not generalist screeners. Their judgements about what "counts",
what a mechanism *is*, and when two studies describe the "same" pattern rested on years of tacit
expertise. **Any system that mimics this workflow must inject that expertise explicitly**, or it will
make novice mistakes at exactly the points where Richmond's team made expert ones.

### 1.2 Division of labour (from §2 and the Author Contributions, L649–658)

| Person | Role in the workflow |
|---|---|
| **AR** (lead, PhD candidate) | background scoping search; drafted CMOCs; built protocol; ran searches; **performed the initial data extraction for all 28**; synthesised results; drew Figures 2–3; wrote the draft. |
| **RP, SG, NC** (senior experts) | each **independently reviewed a sample of full texts**; **checked AR's CMOC coding for consistency**; gave feedback on the developing theory. |
| **WA** (supervisor) | conceived the study; principal PhD supervisor; oversight. |
| **All five** | agreed the Initial Programme Theory by consensus; **agreed the final output** before submission (L657–658). |

The shape is **one lead analyst + a panel of senior checkers + a supervisor + consensus gates**. It
is *not* five equal agents doing the same thing; it is an **asymmetric team with a review hierarchy**.

### 1.3 The actual sequence of operations

1. **Seed an Initial Programme Theory (IPT) BEFORE the main search.** Literature from a *scoping*
   search + expert opinion + researcher experience were synthesised into an IPT (Abstract L40–44;
   §2 L171–188). AR "developed **consensus** amongst the research team" about which interventions
   promote analytical vs non-analytical reasoning; those outputs became "initial drafts of CMOCs";
   "**following feedback from the research team, an initial programme theory (IPT) was
   constructed**" (L178–188). External theories — **Cognitive Flexibility Theory** and **Situativity
   theory** — were folded into the IPT, and *these theories told them where to look* (at the level of
   student, teacher, and learning activity) (L191–203). **The theory came first and steered the
   search.** This is the defining move of a realist review.

2. **Theory-driven, iterative search.** Four databases (MEDLINE, PsycINFO, ERIC, CINAHL), May 2017,
   using "key themes developed from the IPT" (§2.1 L214–219). From year 2000 (post *To Err Is Human*).
   Crucially, a **supplementary search** was added *mid-review* — for "pattern recognition, deliberate
   practice, illness scripts, knowledge acquisition and recall" — because "initial searching
   highlighted these concepts as relevant" (L224–228). The search **expanded as the theory grew**.

3. **Relevance-to-theory screening, not PICO eligibility.** The title/abstract screen assessed
   **relevance**, and a study was retrieved "if [it was] deemed to **contribute to theory building**"
   (L232–234). At full text, they additionally judged **methodological rigour** — "were the methods
   credible and trustworthy" (L235–236) — and applied a working definition of "educational
   intervention" (L237–239). Reference-list ("snowball") searching added 2 more (L244–245).

4. **CMOC extraction with a mandatory second-checker.** "The CMOCs were devised for all included full
   texts. **Initial CMOC coding was undertaken by AR and all 28 articles were checked for consistency
   by another reviewer (RP, SG or NC)**" (§2.2 L248–250). Data-extraction forms were kept for every
   study. **This is the conflict-avoidance convention: one primary coder, one independent
   consistency-checker per article.** Agreement was reached not by voting but by *a second expert
   confirming the first expert's configuration was defensible against the text.*

5. **Cross-study comparison → recurrent patterns.** "Comparisons were made between studies and
   **recurrent patterns of CMOCs were identified**" (L251–252). "Some studies particularly highlighted
   contexts whereas others shed more light on mechanisms" (L252–253) — i.e. they *combined partial
   evidence across studies* into fuller configurations.

6. **Retroduction — the iterative re-analysis loop.** "**Studies identified earlier were re-analysed
   in light of theories arising from papers included later in the review**" (L253–255). This is the
   signature realist loop: the theory is provisional, and **each new study can send you back to
   re-read the old ones**. Tools: NVivo (store + code contexts), Excel (map which contexts affected
   which mechanisms/outcomes) (L259–262).

7. **Converge on the programme theory.** "Key contexts and mechanisms for determining effectiveness
   were eventually produced as outputs from the synthesis through this iterative process" (L262–264).
   They intended to theorise at student / teacher / organisation levels, but the evidence clustered at
   the **individual-student level**, yielding **five contexts** (§3.2 L289–344), each written as an
   italicised CMOC statement + an explanation of its supporting evidence.

8. **Triangulate with outside theory.** Throughout the Discussion they *interpret* their configurations
   against established theory they did not derive from the 28 papers — **cognitive load theory**,
   the **expertise-reversal effect**, the **Matthew effect** (§4 L466–534). Realist method explicitly
   licenses "triangulating insights from other sources to increase the accuracy of results" (L626–628).

9. **Consensus gates.** Two explicit consensus moments bracket the work: the **IPT agreed by the team**
   at the start (L178–188), and **all authors agreeing the final output** at the end (L657–658).

### 1.4 The reasoning conventions that make it "expert"

- **Generative, not successionist, causation.** They never say "intervention X → outcome Y". They say
  the intervention *offers a resource* into a *context*, which *triggers a response*, which *produces*
  an outcome (§2 L147–155). Mechanisms are split into **resource** and **response** — the offering and
  the reaction to it. Our ontology's `Mechanism_Resource` / `Mechanism_Response` split exists *because
  Richmond's method demands it*, not for tidiness.
- **The same intervention can help and harm.** The headline finding is that one intervention "may
  'work' across many contexts, but the effect is not the same across them all" (§4 L512–515). So
  **contradiction is expected data, not error** — it is resolved by finding the *moderating context*.
- **Absence handled by inference, not omission.** Mechanisms/outcomes "not always explicit… can be
  theorised… or inferred" (L151–158). Experts fill gaps with theory; they do not silently drop them.
- **Provisional and revisable.** Earlier conclusions are re-opened when later evidence warrants
  (retroduction, L253–255).

---

## Part 2 — Our multi-agent system as a mirror of that workflow

The design principle (borrowed from **MetaGPT**): *encode the human SOP as the agent topology*. Each
Richmond operation becomes an agent or a checkpoint, agents carry **expert personas**, and they
exchange **typed, schema-validated messages** (Pydantic), never free text — which is what stops the
"cascading hallucination" MetaGPT warns about.

| # | Richmond human operation (Part 1) | Machine realisation | Type |
|---|---|---|---|
| 1 | Domain-expert team | Expert-persona system prompts on every analytic agent (encode clinical-reasoning + realist-method expertise) | Agent config |
| 2 | Lead analyst + senior checkers + supervisor | **Extractor agent** (lead) + **independent Checker agent** (2nd reviewer, *different model family*) + **HITL** (supervisor = the human RA/professor) | Agent topology |
| 3 | Seed the IPT first, by consensus | **IPT Manager agent (P1)** — drafts CMOC hypotheses + context levels from protocol & seed theory, versioned; human ratifies | Agent + HITL |
| 4 | Theory-driven, iterative, supplementary search | Screening rubric keyed to *theory-relevance*; corpus is given for the benchmark, so query-expansion is represented as a **documented protocol step**, not re-run live | Rubric + protocol |
| 5 | Relevance-to-theory screening + rigour appraisal | **Screening agent (A4)** dual-model recall-first vote → **HITL-1**; full-text rigour flag (A5) | Agent + HITL |
| 6 | CMOC coded once, checked for consistency on all 28 | **CMOC Extraction agent (P2)** + **Consistency-Checker agent** on every study + self-check verifier (quote-supports-triple) → **HITL-2** | Agent pair + HITL |
| 7 | Cross-study comparison → recurrent patterns | **Synthesis agent (P4)** demi-regularity motif mining over the typed CMOC graph | Agent |
| 8 | Retroduction — re-analyse earlier studies with later theory | **Retroduction loop** — re-run extraction on earlier studies once the theory updates, until stable | Control loop |
| 9 | Converge to five contexts, CMOC statement + evidence | **Programme-Theory Composer (P6)** → **HITL-4** sign-off | Agent + HITL |
| 10 | Contradiction resolved via moderating context | **Contradiction agent (P5)** → **HITL-3** human interpretive resolution | Agent + HITL |
| 11 | Triangulate with outside theory | **Deliberately constrained** (see Part 3.D) | Design choice |
| 12 | Consensus gates (IPT start, final output) | HITL ratification at IPT (checkpoint 0) and theory sign-off (checkpoint 4); audit trail = "all authors agreed" | HITL |

---

## Part 3 — Honest fidelity audit: have we copied Richmond 100%?

**No. Today the pipeline is a faithful mirror of roughly the *backbone* of Richmond's method, but it
is missing three of the signature realist operations.** Stating this plainly is more scientifically
valuable than claiming completeness — and it defines the work that actually matters.

### ✓ What we copy faithfully (strong)
- **The generative CMOC unit** (resource/response split, span-grounded) — matches §2 exactly.
- **One-coder + independent-checker principle** — realised as a *different model family* checking the
  extractor, plus dual-model screening. This is arguably a *stronger* guarantee than Richmond's, because
  the checker is blind and independent by construction.
- **Cross-study recurrent-pattern identification** (demi-regularities) — matches L251–252.
- **Contradiction-as-data, resolved by moderating context** — matches the headline finding.
- **Consensus gates via HITL** — the human holds the "all authors agreed" authority.
- **Convergence to per-context CMOC statements + evidence** — output genre matches §3.2 / Figs 2–3.

### ✗ Gap 1 — Theory-first IPT seeding (the most important gap)
Richmond **built the IPT before the main analysis and let it steer everything** (L171–203). The
professor named the same thing on 28 May — *"we need some seed, then a modifier, an iterative process,
then the human exam."* Our running pipeline extracts **bottom-up** from the 28 papers with no seeded
theory. The IPT Manager (P1) exists in the architecture but is **not actually driving extraction**.
*Consequence:* we reproduce their *outputs* but not their *reasoning order*. **Fix:** implement P1 so a
versioned IPT (seed contexts + hypothesised CMOCs, human-ratified) is authored first and injected into
the extractor/synthesis prompts as the theory being tested-and-refined.

### ✗ Gap 2 — The retroduction loop (the "iterative modifier" the professor asked for)
Richmond **re-analysed earlier studies in light of later theory** (L253–255); the professor called it
the "iterative modifier … human exam" loop. We extract in a single forward pass. *Consequence:* we
miss the iterative refinement that is the defining rhythm of realist work. **Fix:** add a control loop
— after synthesis updates the theory, re-run extraction on studies coded before the update, and
iterate until CMOCs stabilise (bounded by a max-iteration budget).

### ✗ Gap 4 — Graph community detection for the "community-defined conceptual entities"
The professor's **named key novelty** (abstract §3.1; verification Step 3–4) is to run **graph
community detection (Leiden) over the CMOC graph** so that clusters of mechanism nodes across studies
*emerge* as conceptual entities (e.g. "cognitive-load regulation"), which are then compared to
Richmond's human-articulated mechanisms. **What we actually do today** (`normalization.py`) is
**LLM label-clustering** into concept "families", and `communities.parquet` is exported from those
families — *not* from graph community detection. *Consequence:* we deliver the *goal* (emergent
conceptual entities) but not by the *named mechanism*, and we cannot report the community↔mechanism
alignment metric the professor's Step 4 asks for. **Fix:** run Leiden (via GraphRAG's own community
step, or `networkx`+`igraph`/`leidenalg`) over the typed entity graph, label each community, and add a
community-vs-Richmond-mechanism alignment report — keeping LLM label-normalisation as a pre-pass.

### ✗ Gap 3 — CMOC-level consistency checker as a first-class step
Richmond checked **every one of the 28** CMOC codings with a second reviewer (L248–250). We have an
independent *gold coder* used for **verification**, and a *self-check verifier*, but not a
**pipeline-internal second-expert checker** that must sign off each study's CMOCs before they enter
the graph. **Fix:** promote the Checker to a required in-pipeline agent at HITL-2 (extractor proposes,
checker critiques against the quotes, disagreements escalate to the human).

### ⚠ Deliberate non-copy — outside-theory triangulation (Part 1, step 8)
Richmond interpreted their findings against cognitive-load / expertise-reversal / Matthew-effect
theory *they brought from outside the 28 papers*. **We deliberately restrict the pipeline to the 28
papers only.** Reason: our scientific claim is *reproduction without contamination* — if the machine
could pull in the same external theories (including memory of Richmond's own published paper), we
could not prove it reasoned from the sources rather than recalling the answer. This is a **principled
trade-off**, not an oversight, and it must be stated as a limitation in the manuscript: the machine
under-claims exactly where Richmond used outside theory (e.g. self-efficacy, absent 0× in the corpus).

### Fidelity verdict
**Backbone faithful; ~65–70% of the full method.** Four gaps separate "produces similar outputs" from
"**works the way an expert realist team works**": **Gap 1** theory-first IPT seeding, **Gap 2** the
retroduction loop, **Gap 3** the in-pipeline CMOC consistency-checker, **Gap 4** graph community
detection for the professor's named conceptual-entity novelty. Gaps 1–2 are literally the professor's
"seed → iterative modifier → human exam"; Gap 4 is his named key contribution. They are all
implementable and are the correct next build target — closing them is what makes the paper's central
claim (*a multi-agent system that mimics the expert realist workflow*) **true rather than
approximately true**. The one deliberate non-copy (outside-theory triangulation) stays excluded for
non-contamination and is declared as a limitation.

---

## Part 4 — What we borrowed from comparable systems (grounding, not invention)

- **MetaGPT** (Hong et al., ICLR 2024, arXiv:2308.00352): the core design principle — *encode the human
  SOP as agent roles + structured message schemas + expert-persona prompts*, so intermediate results
  are verifiable and cascading hallucination is suppressed. Directly justifies our extractor/checker
  split and Pydantic-typed inter-agent messages.
- **LatteReview** (Rostam & Kojima, 2025, arXiv:2501.05468): closest prior art — modular
  review agents (screening, scoring, extraction), **sequential + parallel review rounds**, iterative
  refinement on human feedback, Pydantic validation. Confirms our topology is sound and current, and
  gives the "multiple reviewers + reconciliation" pattern we use for the checker step.
- **Human–LLM evidence synthesis** (Cochrane case study, medRxiv 2025.11.08): validates that credible
  automated evidence synthesis is **human-in-the-loop**, not autonomous — matches our HITL sovereignty.
- **Novelty confirmed:** no existing framework combines *realist synthesis + CMOC + LLM + agentic*
  (searches returned none). Our contribution is genuinely the first, per ARCHITECTURE D2.

---

## Part 5 — Architecture audit and cleanup decisions

| Component | Verdict | Action |
|---|---|---|
| CMOC ontology (5 entity + 5 relation, resource/response split) | **Keep** — grounded in §2 | none |
| Extractor + independent Checker + self-verifier | **Keep, strengthen** | make Checker a required in-pipeline step (Gap 3) |
| IPT Manager (P1) | **Keep, implement** — currently design-only | build it; it is core, not optional (Gap 1) |
| Retroduction loop | **Add** — currently absent | implement bounded loop (Gap 2) |
| Dual-model screening + HITL-1 | **Keep** | none |
| Synthesis / demi-regularity mining | **Keep** | none |
| Contradiction agent + HITL-3 | **Keep** | none |
| Programme-theory composer + HITL-4 | **Keep** | none |
| PostgreSQL source-of-truth / Parquet LKG | **Keep** | none |
| Neo4j | **Keep but optional** — derived viz only; never on the critical path | mark optional in docs |
| Live theory-driven *search* (query expansion) | **Descope to protocol note** — corpus is given for the benchmark | document, don't build |
| Outside-theory triangulation | **Intentionally excluded** | document as limitation |
| `res webui` interface | **Secondary** — a window onto the method, not the method | keep minimal; no more effort until the brain is right |
| Model config drift (5.4 vs 5.5 references) | **Fix** | reconcile `models.yaml` and docs to one truth |

**The "brain" in one sentence:** *a human-ratified initial programme theory is seeded first, then an
expert Extractor codes each paper's CMOCs against it while an independent Checker confirms every coding
against its quotes, a Synthesis agent mines recurrent patterns and contradictions across the typed CMOC
graph, and a retroduction loop re-reads earlier papers as the theory refines — with the human holding
sovereign sign-off at four checkpoints, exactly as Richmond's five authors held theirs.*
