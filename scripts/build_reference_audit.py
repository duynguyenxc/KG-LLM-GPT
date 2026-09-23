"""Export an assistant-authored audit of the historical Richmond reference, never a ratified gold.

The notes below were checked against the supplied original PDF, including rendered Figures 2/3.
This script only assembles those explicit notes; it does not infer scientific correctness.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from collections import Counter
from pathlib import Path

# Per-concept interpretation: preserve the historical identifier and wording in the export.
ENTITY_NOTES = {
    "E01": "This specifies the review population/scope, not one of the five explanatory learner contexts. Map to population when comparing source entities.",
    "E02": "Preserve all alternatives: low general/domain-specific knowledge or difficulty applying available knowledge. Training year alone is not an equivalent context.",
    "E03": "High knowledge is domain/task-specific, not a generic senior-student designation.",
    "E04": "Appropriate confidence is calibrated to previous performance; more confidence is not unconditionally better. Coping and confidence are related alternatives, not synonyms.",
    "E05": "Preserve poor coping or insufficient appropriately calibrated confidence/self-efficacy. Do not turn any reported stress into this context.",
    "E06": "Heterogeneity within a learning group is the context; this does not mean every participant has low knowledge.",
    "E07": "A resource in the high-knowledge paragraph, with a related but differently explained low-knowledge branch. Explicit discussion cannot be merged with passive expert observation.",
    "E08": "Analytical reasoning alone is conditional on high relevant knowledge in this paragraph. Figure 2 includes easy cases and overthinking; maintained accuracy with little gain is not demonstrated harm.",
    "E09": "A resource allowing mistakes under positive coping, not a claim that mistakes always improve learning. Safe practice and learner response matter.",
    "E10": "The same real/simulated resource occurs under positive and negative coping, with different responses/outcomes. Retain the context at each occurrence.",
    "E11": "Real cases can create perceived responsibility under positive coping. Exposure alone is not the complete explanation.",
    "E12": "Retention-oriented teaching is a resource for heterogeneous knowledge groups; it is not an observed learner response or a universal guarantee of retention.",
    "E13": "Feedback must be accurate and timely. The mixed/all-knowledge discussion and low-knowledge Figure 3 give related but separately qualified explanations.",
    "E14": "Absent, incomplete and erroneous feedback are alternatives in a problematic resource condition; do not normalize away those qualifiers.",
    "E15": "Clear expert reasoning explanation in Figure 3 leads through clarity/understanding/affirmation. The response is part of the branch, not optional causal decoration.",
    "E16": "Lack of reasoning explanation is essential. Equating this with E07/E15 reverses the educational exposure.",
    "E17": "Near-peer thinking aloud includes prompts/examples. The learner perceives similar knowledge and feels at ease; generic peer teaching is a broader match only.",
    "E18": "This instructs both analytical and non-analytical reasoning in a low-knowledge context; it is not analytical-only instruction or spontaneous guessing.",
    "E19": "Figure 2 uses this as a summary placeholder for diverse low-knowledge resources expanded in Figure 3. It is not a separate universal intervention or mediator inserted into every chain.",
    "E20": "Understanding is a response in several configurations. Keep its context/resource provenance; the same word does not establish the same causal explanation.",
    "E21": "The source marks insight as Mresponse within a sentence also marking diagnostic/management reasoning as O. The historical label combines these spans; split or allow contextual roles rather than treating the whole phrase as a pure outcome.",
    "E22": "Positive learning experience appears in high-knowledge and real-case positive-coping explanations. It is not automatically measured diagnostic improvement.",
    "E23": "Frustration here belongs to high-knowledge analytical-only instruction. Figure 3 also describes frustration in distinct low-knowledge barriers; do not transfer context by sharing this word.",
    "E24": "Reliance on non-analytical reasoning is a response under sufficient domain knowledge; it is not guessing under imposed time pressure.",
    "E25": "High or maintained diagnostic accuracy is a level, not necessarily an improvement. Preserve the no-added-benefit qualification of the analytical-only branch.",
    "E26": "Gratitude is an experiential response under positive coping; the text does not separately establish that gratitude itself causes understanding.",
    "E27": "Building understanding is a learner response associated with the experience. It overlaps lexically with E20 but retains different contextual provenance.",
    "E28": "Positive learning impact is a broad outcome; do not imply every supporting paper measured an identical endpoint or effect size.",
    "E29": "More complete illness scripts are part of the positive-coping explanatory consequences. Contrast E43, which the mixed-knowledge paragraph explicitly labels Mresponse.",
    "E30": "More accurate non-analytical reasoning is an explanatory educational outcome, not permission to infer accuracy from satisfaction or confidence alone.",
    "E31": "Pressure reflects consequential decision making in real cases under positive coping. It is not interchangeable with adverse pressure under poor coping.",
    "E32": "Fear is a response under poor coping/low calibrated confidence and real/simulated encounters; the source offers a theory-informed explanation.",
    "E33": "Stress is conditional, not universally harmful. Positive-coping discussion explains why task-related emotion can also support learning.",
    "E34": "Pressure to perform is part of the negative-coping pathway, distinct from responsibility experienced positively in E31.",
    "E35": "Increased cognitive load is explicitly a response in the adverse pathway. A reduction in cognitive load is not an equivalent label.",
    "E36": "Poor illness-script development is an adverse theoretical consequence; do not turn the review into evidence that each primary study measured it.",
    "E37": "Preserve future and faulty non-analytical reasoning. This is not an immediate diagnostic-accuracy measurement.",
    "E38": "Negative learning outcomes occur in distinct explanations, including poor coping and inadequate feedback. Shared valence does not make their mechanisms equivalent.",
    "E39": "Building on existing knowledge is a response to retention-oriented strategies in heterogeneous groups, not a high-knowledge-only mechanism.",
    "E40": "Increased learning belongs to the retention/understanding explanation; maintain its conditions instead of treating any positive outcome as exact recovery.",
    "E41": "Further engagement is an outcome distinct from learning and diagnostic performance; do not count them as interchangeable observations.",
    "E42": "This bundles understanding successes/failures and improvement planning. It is a compound response that may require multiple source assertions to recover fully.",
    "E43": "Section 3.2.5 explicitly marks complete illness scripts as Mresponse, while the historical entity is Outcome. Preserve that local role or record a justified multi-role interpretation; do not silently force an outcome-only label.",
    "E44": "Successful future non-analytical reasoning is a downstream outcome; preserve future and the more-likely modality of the feedback explanation.",
    "E45": "Confusion is a response to absent/incomplete/erroneous feedback and also to erroneous peer explanations. Its origin must remain identifiable.",
    "E46": "The Figure 3 outcome box is disjunctive: increased learning gain/outcomes OR diagnostic accuracy. Do not require all endpoints or assume identical measurements.",
    "E47": "The adverse Figure 3 box is likewise disjunctive. Decreased learning/accuracy is different from no improvement, increased errors or merely more time spent learning.",
}

RELATION_NOTES = {
    "R01": "Explicit expert reasoning discussion promotes understanding given sufficient domain knowledge; PROVIDES is a project predicate, not a source verbatim causal estimate.",
    "R02": "High knowledge is a context for the expert-discussion explanation, not a sufficient standalone cause of understanding. Preserve the joint resource condition.",
    "R03": "Understanding/insight is part of the high-knowledge expert-discussion explanation; resolve E21's response/outcome compound before scoring the edge.",
    "R04": "The positive experience belongs to the qualified discussion pathway. The text does not supply an isolated effect of understanding independent of the educational resource.",
    "R05": "Analytical-only instruction may frustrate high-knowledge students. Do not generalize to all novices, all analytical scaffolds or diagnostic harm.",
    "R06": "Sufficient domain knowledge supports non-analytical reasoning in this explanation. This context association is not evidence that all high-knowledge students use only that approach.",
    "R07": "Students may maintain high diagnostic accuracy through non-analytical reasoning; preserve maintained/high versus improved accuracy and limited learning gain.",
    "R08": "Opportunities to make mistakes can evoke gratitude under positive coping/calibrated confidence; preserve safe educational exposure.",
    "R09": "Realistic/simulated encounters can evoke gratitude under positive coping. The same exposure has an adverse branch under poor coping.",
    "R10": "Positive coping modifies the response to the educational experience; it does not independently generate gratitude without the resource.",
    "R11": "The narrative says the experience enables understanding after mentioning gratitude. It does not explicitly establish gratitude as the causal antecedent of understanding. Treat these as related responses or a labelled hypothesis pending ratification.",
    "R12": "Building understanding is linked to positive learning in the positive-coping experience; retain the resource and context.",
    "R13": "The review links this learning pathway to more complete illness scripts. Do not represent it as a directly measured independent effect of understanding in every included study.",
    "R14": "More accurate non-analytical reasoning is a downstream consequence of the qualified learning pathway, not a universal effect of any understanding.",
    "R15": "Real cases generate perceived consequential responsibility under positive coping; pressure is not necessarily adverse.",
    "R16": "That responsibility-related pressure can contribute to a positive experience. Do not transfer this relation to fear/pressure under negative coping.",
    "R17": "CONSTRAINS with negative learning outcomes as its object is polarity-ambiguous and can read as preventing harm. The source instead describes an adverse pathway under poor coping after real/simulated encounters. Replace the shorthand with the explicit qualified pathway; no direct context-only effect is established.",
    "R18": "Real/simulated encounters may evoke fear under poor coping or insufficient calibrated confidence; preserve may and the context.",
    "R19": "The resource may evoke stress under poor coping; stress in other contexts can be experienced differently.",
    "R20": "Pressure to perform belongs to the adverse coping pathway, not automatically to every real/simulated encounter.",
    "R21": "Fear/stress/pressure are described together before increased load. This edge decomposes that bundle; it does not establish an independently estimated fear-to-load effect.",
    "R22": "The load explanation follows a bundle of adverse responses. Preserve joint context and theory-informed status rather than asserting an unconditional stress effect.",
    "R23": "Pressure-to-load is a decomposition of the adverse response bundle. Do not equate it with the beneficial responsibility pathway.",
    "R24": "Increased load is proposed to impair illness-script development in the negative-coping explanation; retain its theoretical inference status.",
    "R25": "Future faulty non-analytical reasoning is downstream of the adverse load explanation, not an immediate measured outcome in all studies.",
    "R26": "Negative learning consequences depend on inability to cope with the encounter; a positive cognitive-load manipulation is not automatically the same claim.",
    "R27": "Retention-oriented strategies build on existing knowledge across heterogeneous learners; do not substitute high knowledge as a required context.",
    "R28": "The text coordinates building on knowledge AND developing understanding as responses to the strategy. It does not unambiguously state a serial causal arrow from the former to the latter; revise to co-responses unless ratified otherwise.",
    "R29": "The retention/understanding explanation leads to increased learning under mixed knowledge; do not detach understanding from the resource and context.",
    "R30": "Further engagement is linked to the same qualified pathway and is distinct from measured learning gain.",
    "R31": "Group heterogeneity is the context for a retention strategy, not a standalone cause of building on prior knowledge.",
    "R32": "Accurate timely feedback helps understanding successes/failures and planning improvement across knowledge levels. Accuracy and timeliness are required qualifiers.",
    "R33": "This is a probabilistic explanatory link to complete illness scripts, explicitly Mresponse in the paragraph. Retain more-likely modality and revise the target role.",
    "R34": "Successful future non-analytical reasoning is downstream; the compressed link must retain illness-script development and future/probabilistic qualifications.",
    "R35": "Absent, incomplete OR erroneous feedback can cause confusion; these alternatives and the conditional wording cannot be removed.",
    "R36": "Confusion belongs to the problematic-feedback explanation; the reference should not claim every confusion episode reduces learning.",
    "R37": "Figure 3 links clear expert explanation through clarity/understanding/affirmation to improved learning OR accuracy under low knowledge. This is a compressed path, not a direct resource-outcome edge proving mechanism recovery.",
    "R38": "Passive expert observation without explanation leads through resentment/panic to decreased learning OR accuracy under low knowledge. Preserve the omitted response and missing explanation.",
    "R39": "Near-peer examples/prompts work through perceived similar prior knowledge and feeling at ease. A positive peer-teaching effect alone cannot establish the same explanatory path.",
    "R40": "Combined reasoning instructions work through trust in familiarity and developing ability under low knowledge. This is not evidence for analytical-only instruction or an unmediated universal benefit.",
}

CHAIN_NOTES = {
    "PTS1": "Low knowledge has ten differentiated Figure 3 branches, including negative pathways. This single slash-separated chain mixes labels from other paragraphs and inserts E19 as a mediator; it is not a verbatim published chain.",
    "PTS2": "Figure 2/high-knowledge section concerns expert reasoning discussion and analytical-only/overthinking instruction. The legacy chain instead starts with simulation/real cases and imports retention/feedback responses from other contexts. Replace it with the high-knowledge branches, not a corrected score against this chain.",
    "PTS3": "Separate safe mistakes/simulation from real-case responsibility pathways. The chain omits the responsibility response and imports increased-learning/engagement labels from the mixed-knowledge paragraph. Do not call this combined graph a verbatim transcription.",
    "PTS4": "The adverse coping pathway is real/simulated encounters through fear/stress/pressure and load. Erroneous feedback/confusion and analytical-only frustration have distinct contextual branches; their union is not a single published chain.",
    "PTS5": "Mixed knowledge primarily concerns retention and accurate/timely versus deficient feedback. Near-peer prompts belong to Figure 3's low-knowledge branch. The legacy chain therefore changes the principal resources and mixes contextual pathways.",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entity_scope(number: int) -> tuple[list[int], str]:
    if number == 1:
        return [9], "Section 5: review population"
    if number in range(2, 7):
        return [5, 6, 8], "Figure 2 and sections 3.2.1-3.2.5: five overlapping contexts"
    if number in {15, 16, 17, 18, 46, 47}:
        return [7], "Figure 3: low-knowledge branch"
    if number == 19:
        return [5, 7], "Figure 2 summary box expanded by Figure 3"
    if number in {7, 8, 23, 25}:
        return [
            5,
            6,
            7,
        ], "High-knowledge section/Figure 2, contrasted with distinct Figure 3 branches"
    if number in {10, 20, 29, 31, 32, 33, 34}:
        return [5, 6, 8], "Compare contextual roles across sections 3.2.2-3.2.5 and Figure 2"
    if number in {13, 45}:
        return [7, 8], "Figure 3 and section 3.2.5: shared label, distinct contextual explanation"
    if number in {12, 13, 14} or number >= 32:
        return [8], "Sections 3.2.4-3.2.5; interpret within the specific paragraph"
    return [6], "Sections 3.2.2-3.2.3; interpret within the specific paragraph"


def relation_scope(number: int) -> tuple[list[int], str, str]:
    groups = [
        (4, [6], "RC11", "High domain-specific knowledge; expert reasoning discussed"),
        (
            7,
            [5, 6],
            "RC12",
            "High domain-specific knowledge; analytical-only/overthinking instruction",
        ),
        (
            14,
            [5, 6],
            "RC13",
            "Positive coping/calibrated confidence; safe mistakes and real/simulated experiences",
        ),
        (16, [6], "RC14", "Positive coping; consequential real-case decisions"),
        (26, [5, 8], "RC15", "Poor coping/low calibrated confidence; real/simulated encounters"),
        (31, [8], "RC16", "Heterogeneous knowledge group; retention-oriented strategies"),
        (34, [8], "RC17", "Mixed/all knowledge levels; accurate timely feedback"),
        (36, [8], "RC18", "Problematic absent/incomplete/erroneous feedback"),
    ]
    for maximum, pages, branch, context in groups:
        if number <= maximum:
            return pages, branch, context
    return (
        [7],
        {37: "RC04", 38: "RC07", 39: "RC01", 40: "RC02"}[number],
        "Low knowledge or difficulty applying knowledge; preserve Figure 3 mediator",
    )


def build(root: Path, destination: Path) -> dict:
    original = root / "gold/richmond_gold.json"
    branch_reference = root / "gold/richmond_reference_v1.json"
    pdf = root / "data/paper-Richmond-original.pdf"
    gold = json.loads(original.read_text(encoding="utf-8"))
    assert set(ENTITY_NOTES) == set(gold["entities"]), "Audit coverage differs from source entities"
    assert set(RELATION_NOTES) == {r["id"] for r in gold["relationships"]}, (
        "Audit coverage differs from relations"
    )
    assert set(CHAIN_NOTES) == set(gold["programme_theory_statements"])
    sources = {
        str(p.relative_to(root).as_posix()): sha(p) for p in (original, branch_reference, pdf)
    }
    # The curated annotations were made against these specific versions, not arbitrary later input.
    expected = {
        "gold/richmond_gold.json": "3843043d398fa261a02a2ca693f81fa1e0360d99ba5173603b7ba781ec902674",
        "gold/richmond_reference_v1.json": "f5b40277ad2b96bd91d9ae6450834747566feb20122830d9045352a599902606",
        "data/paper-Richmond-original.pdf": "f7f82be6bc59e06fcda21bd5806a0bf254c1f139048f33cda6dfc2b136bc3cc7",
    }
    if sources != expected:
        raise ValueError("Reference/source version changed: recheck curated notes before exporting")
    concepts, relations, chains = [], [], []
    for code, original_row in gold["entities"].items():
        pages, scope = entity_scope(int(code[1:]))
        action = {
            "E01": "reclassify_population",
            "E19": "summary_placeholder_not_atomic_resource",
            "E21": "split_or_allow_contextual_roles",
            "E43": "revise_contextual_role",
        }.get(code, "retain_with_scope_qualifications")
        concepts.append(
            {
                "reference_id": code,
                "original": original_row,
                "proposed_action": action,
                "assistant_note": ENTITY_NOTES[code],
                "pdf_pages": pages,
                "scope": scope,
                "human_decision": None,
            }
        )
    for original_row in gold["relationships"]:
        code = original_row["id"]
        number = int(code[1:])
        pages, branch, scope = relation_scope(number)
        representation = "conditional_explanatory_link"
        if number in {2, 6, 10, 17, 31}:
            representation = "context_contribution_to_configuration"
        if number in {11, 28}:
            representation = "serial_causal_link_not_explicitly_established"
        if number >= 37:
            representation = "compressed_resource_to_outcome_path"
        action = "add_context_modality_and_inference_qualifiers"
        if number == 17:
            action = "rewrite_polarity_ambiguous_predicate"
        elif number in {11, 28}:
            action = "reconsider_serial_causality"
        elif number >= 37:
            action = "restore_mediator_or_score_only_path_summary"
        relations.append(
            {
                "reference_id": code,
                "original": original_row,
                "subject_label": gold["entities"][original_row["subject_code"]]["label"],
                "object_label": gold["entities"][original_row["object_code"]]["label"],
                "proposed_action": action,
                "representation": representation,
                "assistant_note": RELATION_NOTES[code],
                "pdf_pages": pages,
                "related_provisional_branch": branch,
                "scope": scope,
                "inference_status": "Published realist explanatory synthesis; not proof that every link was measured in each primary study",
                "human_decision": None,
            }
        )
    for code, original_row in gold["programme_theory_statements"].items():
        chains.append(
            {
                "reference_id": code,
                "original": original_row,
                "proposed_action": "replace_union_chain_with_conditional_branches_after_ratification",
                "assistant_note": CHAIN_NOTES[code],
                "pdf_pages": [5, 6, 7, 8],
                "human_decision": None,
            }
        )
    result = {
        "audit_version": "historical-reference-audit-20260923-v1",
        "status": "Assistant-authored source audit; human ratification pending; not a replacement gold standard",
        "author_type": "AI assistant",
        "input_sha256": sources,
        "builder_sha256": sha(Path(__file__)),
        "concepts": concepts,
        "relations": relations,
        "chains": chains,
        "omitted_from_47_concept_inventory": [
            "Several Figure 3 resources: analytical scaffold, imposed time pressure, skipped-step/pattern-based expert explanation, difficult cases, erroneous passive peer explanation.",
            "Several Figure 3 responses: perceived peer knowledge similarity/feeling at ease, trust in familiarity/developing ability, clarity/affirmation, relief/support, panic/resentment, guessing/distress and discordant illness scripts.",
            "These omissions limit the coverage of 47/40 recovery. They are not automatically new ratified codes or a revised denominator. Some broader existing labels partially overlap.",
        ],
        "rating_policy": "Keep the independent ratification packet and its blank forms unchanged. Withhold these assistant proposals during initial independent coding if assessing unaided agreement; disclose assistance if reviewers use them.",
        "system_metrics": None,
        "human_reviews_completed": 0,
        "methodological_source_locator": "PDF page 9 / journal page 717, section 4.1: theoretical inference and incomplete reporting",
    }
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "reference_audit.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    esc = html.escape
    content = [
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Richmond reference audit</title>',
        "<style>body{font:17px/1.6 system-ui;max-width:1100px;margin:2rem auto;padding:1rem;color:#20323d}summary{font-weight:650;cursor:pointer}details{padding:1rem;border-bottom:1px solid #bbb}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f8;padding:1rem}input{font:inherit;padding:.6rem;width:90%}.notice{padding:1rem;background:#fff0d6}a{margin-right:1rem}</style>",
        '<h1>Check the reference before scoring the system</h1><p class="notice">Assistant-authored proposals, not human judgments. Historical reference files remain unchanged. No system accuracy score is computed.</p>',
        "<p>47 concepts, 40 relations and five historical chains were inspected against the original paper. Each entry retains the old coding, source locator and proposed qualification. The 18 configuration branches mentioned below are also provisional project coding.</p>",
        '<p><a href="#concepts">Concepts</a><a href="#relations">Relations</a><a href="#chains">Historical chains</a><a href="reference_audit.json">Full audit JSON</a></p>',
        '<label for="search">Search IDs, labels or audit notes</label><p><input id="search" placeholder="E43, R17, feedback, context..."></p>',
    ]
    for key in ["concepts", "relations", "chains"]:
        content.append(f'<h2 id="{key}">{len(result[key])} {key}</h2>')
        for row in result[key]:
            label = row["original"].get("label") or (
                f"{row['subject_label']} → {row['original']['predicate']} → {row['object_label']}"
                if key == "relations"
                else row["original"]["context_label"]
            )
            links = " ".join(
                f'<a href="{esc(pdf.resolve().as_uri())}#page={page}">PDF p. {page} / journal p. {708 + page}</a>'
                for page in row["pdf_pages"]
            )
            content.append(
                f'<details class="record" id="{esc(row["reference_id"])}"><summary>{esc(row["reference_id"])}: {esc(label)}</summary><p><b>Proposal:</b> {esc(row["proposed_action"])}</p><p>{esc(row["assistant_note"])}</p><p>{esc(row.get("scope", "Compare full conditional branches rather than slash-separated unions"))}</p><p>{links}</p><p>Human decision: pending.</p><details><summary>Original coding and full audit record</summary><pre>{esc(json.dumps(row, indent=2, ensure_ascii=False))}</pre></details></details>'
            )
    content.append(
        "<h2>Coverage limits</h2><ul>"
        + "".join(f"<li>{esc(x)}</li>" for x in result["omitted_from_47_concept_inventory"])
        + "</ul>"
    )
    content.append('<p class="notice">' + esc(result["rating_policy"]) + "</p>")
    content.append(
        "<script>document.getElementById('search').addEventListener('input',function(){const q=this.value.toLowerCase();document.querySelectorAll('.record').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q));});function reveal(){const r=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(r&&r.tagName==='DETAILS'){r.hidden=false;r.open=true;r.scrollIntoView();}}window.addEventListener('hashchange',reveal);reveal();</script></html>"
    )
    (destination / "index.html").write_text("\n".join(content), encoding="utf-8")
    return {
        "output": str(destination),
        "counts": {k: len(result[k]) for k in ("concepts", "relations", "chains")},
        "relation_proposals": dict(Counter(r["proposed_action"] for r in relations)),
        "human_reviews_completed": 0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.root.resolve(), args.output_dir.resolve()), indent=2))
