# Content correspondence: this system vs. Richmond et al. (2020)

> Source of the standard: **Richmond, A. et al. (2020). The student is key: A realist review of educational interventions to develop analytical and non-analytical clinical reasoning ability. Medical Education, 54(8), 709-719. https://doi.org/10.1111/medu.14137**  
> The reference below is the analytic content Richmond's human team published — every item cites its location in their paper. Each row shows whether this system independently recovered that content, and from which study and verbatim quote, so the correspondence can be checked directly against the paper. Semantic matches are LLM-judged and flagged for human ratification; they are not a self-assigned grade.

_Verification data: `verification_report.json` — entity matcher sampled 3× and majority-voted._

## Contexts — the student and setting conditions Richmond identified

| Richmond (code · location) | Richmond describes | This system recovered |
|---|---|---|
| `E01` · Conclusions, p.717 | undergraduate students in medical or health care professions education | our concept **non-expert surgical learners** (studies S003, S004, S007, S014…) — quote: *"this study was performed among fourth-year medical students just before attaining the license of medical doctor."* |
| `E02` · Results 3.2 / Figure 2, pp.712-714 | students with 'low knowledge,' low clinical domain-specific knowledge, or an inability to use knowledge in a reasoning situation | our concept **novices not using nonanalytic reasoning** (studies S006, S013, S016, S018…) — quote: *"Therefore, they are not yet likely to have well-developed illness scripts."* |
| `E03` · Results 3.2, pp.712-714 | students with high clinical domain-specific knowledge | our concept **clinically different expertise levels** (studies S001, S009, S022) — quote: *"Scores were compared between groups of different levels of expertise: surgeons (licensed surgeon), residents (surgical trainee), interns (has experience as phys…"* ⟂ *(role differs from Richmond)* |
| `E04` · Results 3.2, pp.712-714 | positive student coping strategies or appropriate level of self-confidence or self-efficacy | our concept **easy comparison with near-peer reasoning** (studies S007, S022, S026) — quote: *"which allows the latter to relate to it easily and to appreciate similarities and differences."* ⟂ *(role differs from Richmond)* |
| `E05` · Results 3.2, pp.712-714 | negative student coping strategies or lacking self-confidence or self-efficacy | **not recovered** |
| `E06` · Results 3.2, pp.712-714 | students with different levels of knowledge within a group | **not recovered** |

## Interventions — the educational resources/activities

| Richmond (code · location) | Richmond describes | This system recovered |
|---|---|---|
| `E07` · Results 3.2.2, p.714 | an expert's reasoning processes or thoughts are explicitly revealed and discussed | our concept **case-based clinical reasoning seminar intervention** (studies S001, S003, S004, S005…) — quote: *"This case-based clinical reasoning seminar intervention, designed to bring students insight into cognitive features of their reasoning, improved aspects of diag…"* |
| `E08` · Results 3.2.2, p.714 | instructed to use analytical reasoning alone | our concept **spontaneous reasoning instruction** (studies S005) — quote: *"whereas the other half were given no instructions regarding how best to approach the diagnosis of test cases (i.e. the spontaneous reasoning condition)."* |
| `E09` · Results 3.2.3, p.714 | teaching resources that allow them to make mistakes | our concept **worked examples with errors and elaborated feedback** (studies S006) — quote: *"In order to enhance the effectiveness of the approach, two additional measures were implemented: erroneous examples and elaborated feedback."* |
| `E10` · Results 3.2.3, p.714 | real-life scenarios, including simulation and simulated patients | our concept **diagnostic decision tree VP cases** (studies S011, S015) — quote: *"Diagnostic decision tree software can be used to create VP cases that give virtual experience of these real-time clinical reasoning techniques."* |
| `E11` · Results 3.2.3, p.714 | real cases | our concept **practice with ECG examples** (studies S005, S011, S017, S022) — quote: *"For each diagnostic category, participants were presented with 4 examples. For the first 2 ECGs in each category, the instructor identified key features"* ⟂ *(role differs from Richmond)* |
| `E12` · Results 3.2.5, p.716 | strategies that promote knowledge retention | our concept **diligent study and practice** (studies S009) — quote: *"with expertise developed over years of diligent study and practice, become increasingly adept at learning to trace back"* |
| `E13` · Results 3.2.5, p.716 | accurate and timely feedback | our concept **computer-assisted key feature testing** (studies S027) — quote: *"Testing was spaced across weeks and students were given immediate educational feedback on their answers."* |
| `E14` · Results 3.2.5, p.716 | feedback is absent, incomplete or contains errors | our concept **unsupported similar-case reasoning with reduced feedback** (studies S018) — quote: *"what medical students learn spontaneously from reasoning through a series of cases that have a similar underlying biomedical problem and where only reduced feed…"* |
| `E15` · Figure 3, p.715 | explicit and clear explanation of expert's reasoning | our concept **comprehension-stage teacher-led consultation** (studies S028) — quote: *"following the demonstration and deconstruction phase, the next consultation should again be performed by the teaching clinician"* |
| `E16` · Figure 3, p.715 | passive observation of experts without receiving explanation about their reasoning processes | our concept **combined self-explanation and SE model observation** (studies S025, S026) — quote: *"Participants of the peer-SE and expert-SE groups were then instructed to listen to an 8-min recording of either peer or expert SE"* |
| `E17` · Figure 3, p.715 | listen to near-peer think aloud their reasoning with the use of prompts and examples | our concept **combined self-explanation and SE model observation** (studies S025, S026) — quote: *"Participants of the peer-SE and expert-SE groups were then instructed to listen to an 8-min recording of either peer or expert SE"* |
| `E18` · Figure 3, p.715 | instructing to use both 'non-analytical' or pattern recognition and analytical or step-wise approach to reasoning | our concept **final combined-strategy testing phase** (studies S021) — quote: *"Prior to a final test (test 3), participants in both groups were instructed to adopt a combined analytic/nonanalytic diagnostic strategy."* |

## Mechanisms (Resource) — what the intervention offers

| Richmond (code · location) | Richmond describes | This system recovered |
|---|---|---|
| `E19` · Figure 2, p.713 | multiple relevant resources | our concept **multiple tasks and acutely unwell patients** (studies S011, S015, S022, S023…) — quote: *"During their simulation session, the students were faced with multiple tasks and acutely unwell patients, and therefore had to prioritise."* ⟂ *(role differs from Richmond)* |

## Mechanisms (Response) — how students reason/react

| Richmond (code · location) | Richmond describes | This system recovered |
|---|---|---|
| `E20` · Results 3.2.2, p.714 | understanding | our concept **insufficient deep conceptual understanding** (studies S006) — quote: *"For most students, the information that a speciﬁc diagnostic conclusion or procedure is not adequate seems not to be sufﬁcient to induce deep conceptual underst…"* |
| `E23` · Results 3.2.2, p.714 | frustrated | our concept **student frustration** (studies S022) — quote: *"Of the students, 8 of 17 found the game frustrating (compared to 1 of 11 trainees and 1 of 6 experts)."* |
| `E24` · Results 3.2.2, p.714 | rely on non-analytical reasoning | our concept **greater analytic-tendency reliance** (studies S004) — quote: *"the aim of the feature manipulation was to induce people towards placing greater reliance on their analytic tendencies"* |
| `E26` · Results 3.2.3, p.714 | grateful for the learning experience | **not recovered** |
| `E27` · Results 3.2.3, p.714 | build understanding | our concept **knowledge elaboration and reorganisation** (studies S013, S016, S025, S026) — quote: *"This process of elaboration on the case information and search for meaning helps to activate additional relevant knowledge and fosters the integration and reorg…"* |
| `E31` · Results 3.2.3, p.714 | pressure that their decision making could have a real impact | **not recovered** |
| `E32` · Results 3.2.4, p.716 | fear | our concept **reduced fear during senior referral** (studies S015) — quote: *"SB2 – The SBAR structure was really useful. It took a bit of the fear away definitely"* |
| `E33` · Results 3.2.4, p.716 | stress | our concept **stress from competing patient and pager demands** (studies S015) — quote: *"SA3 – It was stressful. When you have a sick patient and then the page goes off, that was stressful."* |
| `E34` · Results 3.2.4, p.716 | pressure to perform | our concept **ten-second case time limit** (studies S022) — quote: *"The player had a maximum of 10 s to solve each case."* ⟂ *(role differs from Richmond)* |
| `E35` · Results 3.2.4, p.716 | cognitive load is increased | our concept **cognitive load overwhelm** (studies S016, S024, S025, S028) — quote: *"may simply overwhelm an individual’s cognitive load without any effect on outcomes."* |
| `E39` · Results 3.2.5, p.716 | build upon what they already know | our concept **knowledge elaboration and reorganisation** (studies S013, S016, S025, S026) — quote: *"This process of elaboration on the case information and search for meaning helps to activate additional relevant knowledge and fosters the integration and reorg…"* |
| `E42` · Results 3.2.5, p.716 | develop understanding of their successes and failures and generate plans for improvement | our concept **reflection on and improvement of reasoning** (studies S028) — quote: *"the benefits of reflecting upon and improving one’s own reasoning may include:"* |
| `E45` · Results 3.2.5, p.716 | confusion | our concept **possible confusion from combined instructions** (studies S021) — quote: *"An alternative explanation for the relatively poor performance in the final test, which occurred in both groups of participants, is the possibility that partici…"* |

## Outcomes — the reasoning/learning results

| Richmond (code · location) | Richmond describes | This system recovered |
|---|---|---|
| `E21` · Results 3.2.2, p.714 | insight into the reasoning process when diagnosing and managing patients | our concept **reduced ability to exploit cases** (studies S004, S018, S019, S021…) — quote: *"this result raises doubts about the students’ ability to take full advantage of learning from cases."* |
| `E22` · Results 3.2.2, p.714 | positive learning experience | our concept **perceived usefulness for developing consulting skills** (studies S009, S011, S015, S025…) — quote: *"Thus the added value of SE models was altogether subtle, only evidenced on training cases, and expert SE models were not more effective than peer SE models."* |
| `E25` · Results 3.2.2, p.714 | high diagnostic accuracy | our concept **improved diagnostic accuracy** (studies S003, S004, S005, S019…) — quote: *"Mean diagnostic accuracy scores were significantly higher in the analytic reasoning group than in the control group"* |
| `E28` · Results 3.2.3, p.714 | positive impact on learning | our concept **intended acquisition of primary-care reasoning skills** (studies S001, S011, S018, S023) — quote: *"Follow-up of and reflection on patients is a powerful discipline for the learning and construction of clinical reasoning skills (Kassirer 2010), but this is lim…"* |
| `E29` · Results 3.2.3, p.714 | more complete illness scripts | our concept **illness-script development for diagnosis** (studies S023) — quote: *"pools of similar cases are required so that students can properly develop their illness scripts in order to make suitable and valid diagnoses"* |
| `E30` · Results 3.2.3, p.714 | more accurate non-analytical reasoning | our concept **faster nonanalytic responses** (studies S018, S021) — quote: *"Speed of response to test images was generally faster under nonanalytic than under analytic conditions."* |
| `E36` · Results 3.2.4, p.716 | poor illness script development | our concept **insufficient biomedical integration in illness scripts** (studies S018, S024) — quote: *"unsupported case analyses are in no way sufﬁcient for integrating biomedical knowledge in illness scripts."* |
| `E37` · Results 3.2.4, p.716 | faulty future non-analytical reasoning | our concept **combined-strategy accuracy hypothesis not supported** (studies S021) — quote: *"The hypothesis that a combined nonanalytic/analytic reasoning strategy can achieve diagnostic accuracy greater than that employing either method alone is theref…"* ⟂ *(role differs from Richmond)* |
| `E38` · Results 3.2.4, p.716 | negative learning outcomes | our concept **increased learning time** (studies S004, S005, S006, S013…) — quote: *"in our study, elaborated feedback resulted in a substantial increase in learning time."* |
| `E40` · Results 3.2.5, p.716 | increased learning | our concept **intended acquisition of primary-care reasoning skills** (studies S001, S011, S018, S023) — quote: *"Follow-up of and reflection on patients is a powerful discipline for the learning and construction of clinical reasoning skills (Kassirer 2010), but this is lim…"* |
| `E41` · Results 3.2.5, p.716 | further engagement | our concept **objective prioritisation learning** (studies S014, S015, S022) — quote: *"Making it readily available increased the use of SBAR. The students felt more comfortable using the structured, SBAR approach"* |
| `E43` · Results 3.2.5, p.716 | complete illness scripts | our concept **illness-script development for diagnosis** (studies S023) — quote: *"pools of similar cases are required so that students can properly develop their illness scripts in order to make suitable and valid diagnoses"* |
| `E44` · Results 3.2.5, p.716 | successful non-analytical reasoning in the future | our concept **faster nonanalytic responses** (studies S018, S021) — quote: *"Speed of response to test images was generally faster under nonanalytic than under analytic conditions."* |
| `E46` · Figure 3, p.715 | increase in learning gain or outcomes, or increase in diagnostic accuracy | our concept **improved diagnostic accuracy** (studies S003, S004, S005, S019…) — quote: *"Mean diagnostic accuracy scores were significantly higher in the analytic reasoning group than in the control group"* |
| `E47` · Figure 3, p.715 | decrease in learning gain or outcomes, or decrease in diagnostic accuracy | our concept **increased learning time** (studies S004, S005, S006, S013…) — quote: *"in our study, elaborated feedback resulted in a substantial increase in learning time."* |

## Causal relationships Richmond asserts

Three fairness levels, all reported (a realist review cares most about the **pattern**, not exact concept-string identity):

- **Type-level pattern** (e.g. *Context CONSTRAINS Outcome* exists in our graph): **39/40**
- **Anchored** (same predicate, one endpoint the exact matched concept, other of the right role): **22/40**
- **Concept-exact** (both endpoints the exact matched concepts — deliberately harsh): **0/40**

| Richmond relation | Subject → predicate → object | Concept-exact | Anchored |
|---|---|---|---|
| `R01` | an expert's reasoning processes or thoug —PROVIDES→ understanding | — | — |
| `R02` | students with high clinical domain-speci —ENABLES→ understanding | — | ✅ |
| `R03` | understanding —LEADS_TO→ insight into the reasoning process when  | — | ✅ |
| `R04` | understanding —LEADS_TO→ positive learning experience | — | ✅ |
| `R05` | instructed to use analytical reasoning a —TRIGGERS→ frustrated | — | — |
| `R06` | students with high clinical domain-speci —ENABLES→ rely on non-analytical reasoning | — | ✅ |
| `R07` | rely on non-analytical reasoning —LEADS_TO→ high diagnostic accuracy | — | ✅ |
| `R08` | teaching resources that allow them to ma —TRIGGERS→ grateful for the learning experience | — | — |
| `R09` | real-life scenarios, including simulatio —TRIGGERS→ grateful for the learning experience | — | — |
| `R10` | positive student coping strategies or ap —ENABLES→ grateful for the learning experience | — | — |
| `R11` | grateful for the learning experience —LEADS_TO→ build understanding | — | — |
| `R12` | build understanding —LEADS_TO→ positive impact on learning | — | ✅ |
| `R13` | build understanding —LEADS_TO→ more complete illness scripts | — | ✅ |
| `R14` | build understanding —LEADS_TO→ more accurate non-analytical reasoning | — | ✅ |
| `R15` | real cases —TRIGGERS→ pressure that their decision making coul | — | ✅ |
| `R16` | pressure that their decision making coul —LEADS_TO→ positive learning experience | — | ✅ |
| `R17` | negative student coping strategies or la —CONSTRAINS→ negative learning outcomes | — | ✅ |
| `R18` | real-life scenarios, including simulatio —TRIGGERS→ fear | — | — |
| `R19` | real-life scenarios, including simulatio —TRIGGERS→ stress | — | — |
| `R20` | real-life scenarios, including simulatio —TRIGGERS→ pressure to perform | — | — |
| `R21` | fear —LEADS_TO→ cognitive load is increased | — | — |
| `R22` | stress —LEADS_TO→ cognitive load is increased | — | — |
| `R23` | pressure to perform —LEADS_TO→ cognitive load is increased | — | — |
| `R24` | cognitive load is increased —LEADS_TO→ poor illness script development | — | ✅ |
| `R25` | cognitive load is increased —LEADS_TO→ faulty future non-analytical reasoning | — | ✅ |
| `R26` | cognitive load is increased —LEADS_TO→ negative learning outcomes | — | ✅ |
| `R27` | strategies that promote knowledge retent —TRIGGERS→ build upon what they already know | — | ✅ |
| `R28` | build upon what they already know —LEADS_TO→ understanding | — | — |
| `R29` | understanding —LEADS_TO→ increased learning | — | ✅ |
| `R30` | understanding —LEADS_TO→ further engagement | — | ✅ |
| `R31` | students with different levels of knowle —ENABLES→ build upon what they already know | — | ✅ |
| `R32` | accurate and timely feedback —TRIGGERS→ develop understanding of their successes | — | — |
| `R33` | develop understanding of their successes —LEADS_TO→ complete illness scripts | — | ✅ |
| `R34` | develop understanding of their successes —LEADS_TO→ successful non-analytical reasoning in t | — | ✅ |
| `R35` | feedback is absent, incomplete or contai —TRIGGERS→ confusion | — | ✅ |
| `R36` | confusion —LEADS_TO→ negative learning outcomes | — | ✅ |
| `R37` | explicit and clear explanation of expert —TRIGGERS→ increase in learning gain or outcomes, o | — | — |
| `R38` | passive observation of experts without r —TRIGGERS→ decrease in learning gain or outcomes, o | — | — |
| `R39` | listen to near-peer think aloud their re —TRIGGERS→ increase in learning gain or outcomes, o | — | — |
| `R40` | instructing to use both 'non-analytical' —TRIGGERS→ increase in learning gain or outcomes, o | — | — |

## Programme-theory chains (the heart of the realist review)

Richmond's five context-specific C→M→O chains, and how closely this system's programme theory corresponds to each (model-judged, human rating required before publication).

| Chain | Richmond context | Canonical chain | Correspondence | Assessor note |
|---|---|---|---|---|
| `PTS1` | Students with low clinical domain-specific knowledge | `E07/E15/E18 → E19 → E20/E27 → E25/E29/E30` | 0.893 | Strong correspondence. The SYSTEM theory has a closely matching low-knowledge/novice context and describes explicit expert-reasoning visibil… |
| `PTS2` | Students with high clinical domain-specific knowledge | `E10/E11 → E19 → E24/E39 → E25/E30/E43/E44` | 0.503 | Partial correspondence. The SYSTEM theory includes case exposure, simulation/virtual/realistic cases, repeated varied cases, feedback, build… |
| `PTS3` | Students with positive coping / self-efficacy | `E09/E10/E11 → E19 → E26/E27 → E22/E28/E40/E41` | 0.317 | Low-to-moderate correspondence. The SYSTEM theory contains some related positive affective and engagement outcomes, especially in bounded si… |
| `PTS4` | Students with negative coping / lacking self-efficacy | `E09/E10/E14 → E19 → E23/E32/E33/E34/E35/E45 → E36/E37/E38/E47` | 0.593 | Moderate correspondence. The SYSTEM theory clearly includes negative pathways involving thin/absent guidance or feedback, excessive complexi… |
| `PTS5` | Students with different levels of knowledge within a group | `E07/E17 → E19 → E27/E39/E42 → E29/E43/E44/E46` | 0.39 | Partial but limited correspondence. The SYSTEM theory includes expert-reasoning visibility, modelling, prompts, comparison with one's own id… |

## Honest tally (a summary OF the correspondence above, not a grade)

- Contexts/interventions/mechanisms/outcomes Richmond describes: **43 of 47** independently recovered (of which 37 with the same realist role as Richmond, 6 the same construct under a different role).
- Causal relationships: type-level pattern **39/40**, anchored **22/40**, concept-exact **0/40**.
- Programme-theory correspondence (mean, model-judged): **0.5392** (range 0.5–0.56).
- Citation faithfulness (quotes that resolve exactly to source text): **501/517**.

_Every recovered item above is traceable to a Richmond page location and an extracted verbatim quote; every semantic match is LLM-judged and awaits human ratification. This report is the verification — the numbers only summarise it._
