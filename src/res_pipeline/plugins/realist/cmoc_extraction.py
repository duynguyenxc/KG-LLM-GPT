"""CMOC Extraction Agent: full text -> typed, span-grounded, verified configurations.

Design constraints (ARCHITECTURE D1/D4; SOTA_REPORT Q1-Q4):
  * NARROW schema — a list of CMOCs, each with few fields (ExtractBench lesson:
    wide schemas collapse extraction fidelity).
  * Every entity mention MUST carry a verbatim quote; quotes are resolved to
    character spans against the canonical text (exact match, then a whitespace-
    normalized fallback). Unresolvable quotes are flagged, never fabricated.
  * Relations use the five fixed predicates; domain/range violations are demoted
    to UNTYPED_CANDIDATE (preserved for HITL-2, not silently dropped).
  * A second, cheaper verifier model scores whether the quotes actually support
    each configuration (cross-critique pattern) — low-support CMOCs are flagged
    for HITL-2 review.
"""

from __future__ import annotations

import re
import uuid

from pydantic import BaseModel, Field

from res_pipeline.core.agents import persona
from res_pipeline.core.db import get_connection, log_audit_event
from res_pipeline.core.llm import call_structured
from res_pipeline.plugins.realist.ontology import EntityType, Predicate, domain_range_map

PROMPT_VERSION = "cmoc-extraction-v3.0-ipt+checker"

_ENTITY_FIELD_TO_TYPE: dict[str, EntityType] = {
    "contexts": EntityType.CONTEXT,
    "interventions": EntityType.INTERVENTION,
    "mechanism_resources": EntityType.MECHANISM_RESOURCE,
    "mechanism_responses": EntityType.MECHANISM_RESPONSE,
    "outcomes": EntityType.OUTCOME,
}


class ExtractedEntity(BaseModel):
    label: str = Field(description="Short noun-phrase label for the concept (<=12 words).")
    verbatim_quote: str = Field(
        description="EXACT verbatim quote from the paper (10-40 words) evidencing this element. "
        "Copy characters exactly; do not paraphrase."
    )


class ExtractedRelation(BaseModel):
    subject_label: str
    predicate: str = Field(
        pattern=r"^(PROVIDES|TRIGGERS|ENABLES|LEADS_TO|CONSTRAINS)$"
    )
    object_label: str


class ExtractedCMOC(BaseModel):
    contexts: list[ExtractedEntity] = Field(min_length=1)
    interventions: list[ExtractedEntity] = Field(default_factory=list)
    mechanism_resources: list[ExtractedEntity] = Field(default_factory=list)
    mechanism_responses: list[ExtractedEntity] = Field(
        min_length=1,
        description="At least one — the learner's cognitive OR emotional reaction. Capture "
        "affective responses explicitly (e.g. panic, frustration, fear, stress, gratitude, "
        "confidence, confusion, cognitive overload) when the text evidences them.",
    )
    outcomes: list[ExtractedEntity] = Field(min_length=1)
    relations: list[ExtractedRelation] = Field(default_factory=list)
    polarity: str = Field(pattern=r"^(positive|negative|mixed)$")
    narrative_statement: str = Field(
        description="One italicisable realist sentence: 'When <context>, <resource/intervention> "
        "triggers <response>, leading to <outcome>.'"
    )


class ExtractionResult(BaseModel):
    cmocs: list[ExtractedCMOC]
    study_limitations: str = Field(
        description="Honest note on source limitations (e.g., abstract-only, partial text)."
    )


class VerifierVerdict(BaseModel):
    support_score: float = Field(ge=0.0, le=1.0,
                                 description="Do the quotes genuinely support the configuration?")
    notes: str


class CMOCCheck(BaseModel):
    cmoc_index: int = Field(description="0-based index of the CMOC in the list, as given.")
    agrees: bool = Field(description="Does the second reviewer accept this configuration as coded?")
    issue: str = Field(
        default="",
        description="If not agreed: the specific defect — mislabelled C/M/O, unsupported causal "
        "reading, resource/response conflated, over-claim, or a missed pathway. Empty if agreed.",
    )


class ConsistencyReview(BaseModel):
    """The second reviewer's independent consistency check over one study's CMOCs."""
    checks: list[CMOCCheck]
    study_note: str = Field(description="One-line overall judgement of the study's coding.")


_SYSTEM = """You are a realist-synthesis subject-matter expert performing CMOC \
(Context-Mechanism-Outcome Configuration) extraction, following RAMESES standards.

DEFINITIONS (label elements EXPLICITLY and SEPARATELY — RAMESES II requirement):
- Context: pre-existing condition of learner/group/setting affecting how an intervention is \
received (e.g., low prior knowledge, high self-confidence, mixed-knowledge group).
- Intervention: the educational teaching process/method/resource being studied.
- Mechanism_Resource: what the intervention offers into the context.
- Mechanism_Response: the cognitive/emotional reaction of participants to that resource.
- Outcome: the measured or theorised effect (e.g., diagnostic accuracy, illness-script \
development, negative learning outcome).

BOUNDARY RULE (the most-mistyped distinction — apply it deliberately):
- A Mechanism_Resource is a THING the intervention SUPPLIES: a case, a worked example, an \
expert explanation, feedback, an instruction/prompt, a simulator. Test: can you say "the \
teaching PROVIDES this"? If yes → Resource.
- A Mechanism_Response is the learner's INTERNAL reaction: understanding, insight, panic, \
frustration, felt pressure, stress, confidence, confusion, cognitive load. Test: does the \
learner FEEL it or do it in their head? If yes → Response, NOT Resource. (e.g. "pressure to \
perform", "felt stress" are Responses.)
- A Context is a condition that exists BEFORE and INDEPENDENT of the intervention (prior \
knowledge level, self-confidence level, group composition). If it describes who the learner \
ALREADY is → Context, NOT a Response.

RULES:
1. Extract 2-5 CMOCs per paper — cover BOTH the beneficial pathways AND any harmful/no-effect \
pathways the study reports (realist reviews care especially about when interventions FAIL or \
BACKFIRE). Only configurations genuinely evidenced by the text.
2. EVERY element requires a verbatim quote copied EXACTLY from the text (10-40 words). \
Never paraphrase inside verbatim_quote. Copy punctuation and words as they appear. If you \
cannot quote it, do not extract it.
3. ALWAYS populate mechanism_responses — the learner's cognitive or emotional reaction is the \
heart of realist mechanism. Emotions matter: when the text reports panic, resentment, \
frustration, fear, stress, pressure, cognitive overload, confusion, gratitude, confidence, or \
engagement, extract it as a Mechanism_Response with its quote. Responses may be inferred from \
reported behaviour/affect, but the quote must contain the evidence.
4. Capture NEGATIVE chains explicitly: e.g., low-knowledge learner + demanding resource → \
overload/confusion/fear → poor illness-script formation / negative learning outcome. Do not \
report only the success stories.
5. Relations: use ONLY these directed predicates — PROVIDES (Intervention→Resource or \
Intervention→Response), TRIGGERS (Intervention/Resource→Response or →Outcome), ENABLES \
(Context→Response/Outcome), LEADS_TO (Response→Response/Outcome), CONSTRAINS (Context→Outcome). \
Provide a relation for every causal link you can support; subject/object labels must exactly \
match entity labels you extracted.
6. polarity: 'positive' if beneficial outcomes, 'negative' if harmful/no-benefit, 'mixed' otherwise.
7. Do NOT fabricate; fewer well-evidenced CMOCs beat speculative ones — but DO be thorough about \
the mechanisms and negative pathways the study actually reports."""


def _resolve_span(quote: str, canonical_text: str) -> tuple[int | None, int | None, bool]:
    """Locate a quote in the canonical text: exact, then whitespace-normalized."""
    idx = canonical_text.find(quote)
    if idx != -1:
        return idx, idx + len(quote), True
    # Whitespace-normalized fallback: build a regex tolerant to whitespace runs.
    tokens = [re.escape(t) for t in quote.split() if t]
    if len(tokens) >= 4:
        pattern = r"\s+".join(tokens)
        match = re.search(pattern, canonical_text, flags=re.IGNORECASE)
        if match:
            return match.start(), match.end(), True
    return None, None, False


def extract_study_cmocs(study_id: str, run_id: str) -> dict:
    """Extract, verify, resolve, validate, and persist CMOCs for one study."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT ct.canonical_text, s.title, s.year, s.source_kind "
            "FROM canonical_texts ct JOIN studies s USING (study_id) WHERE ct.study_id=%s",
            (study_id,),
        ).fetchone()
    canonical_text, title = row["canonical_text"], row["title"]

    # Per-paper CMOC coding stays DATA-DRIVEN and pristine (Richmond §2.2): the IPT
    # steers synthesis/retroduction, NOT per-paper extraction — injecting it here was
    # measured to suppress CMOC yield and quote-support (a MetaGPT-style dilution). The
    # faithful per-paper addition is the independent Checker (below), not a prompt change.
    user_prompt = (
        f"STUDY {study_id}: {title} ({row['year'] or 'year unknown'}); "
        f"source: {row['source_kind']}.\n\nFULL TEXT:\n{canonical_text}\n\n"
        "Extract the CMOCs."
    )
    result = call_structured(
        tier="extraction", system_prompt=_SYSTEM, user_prompt=user_prompt,
        schema=ExtractionResult, run_id=run_id,
    )

    stats = {"cmocs": 0, "entities": 0, "relations": 0, "unresolved_quotes": 0,
             "demoted_relations": 0, "low_support": 0, "checker_flagged": 0}
    persisted: list[tuple[str, ExtractedCMOC]] = []  # (cmoc_id, cmoc) for the Checker pass

    for cmoc in result.cmocs:
        cmoc_id = f"{study_id}-cmoc-{uuid.uuid4().hex[:6]}"

        # Verifier pass (cross-critique): do the quotes support the configuration?
        verdict = call_structured(
            tier="extraction_verifier",
            system_prompt="You are a sceptical audit reviewer. Given a CMOC and its quotes, "
            "judge whether the quotes GENUINELY support each labelled element and the causal "
            "reading. Penalise paraphrased or off-topic quotes.",
            user_prompt=cmoc.model_dump_json(indent=1),
            schema=VerifierVerdict, run_id=run_id,
        )
        if verdict.support_score < 0.6:
            stats["low_support"] += 1

        label_to_entity: dict[str, tuple[str, EntityType]] = {}
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO cmocs (cmoc_id, study_id, polarity, narrative_statement, "
                "verifier_support, verifier_notes, run_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (cmoc_id, study_id, cmoc.polarity, cmoc.narrative_statement,
                 verdict.support_score, verdict.notes, run_id),
            )
            for field_name, entity_type in _ENTITY_FIELD_TO_TYPE.items():
                for extracted in getattr(cmoc, field_name):
                    entity_id = f"{cmoc_id}-e-{uuid.uuid4().hex[:6]}"
                    start, end, resolved = _resolve_span(
                        extracted.verbatim_quote, canonical_text
                    )
                    if not resolved:
                        stats["unresolved_quotes"] += 1
                    conn.execute(
                        "INSERT INTO entity_instances (entity_id, study_id, cmoc_id, "
                        "entity_type, label, verbatim_quote, char_start, char_end, "
                        "quote_resolved, extractor_model, prompt_version, confidence, run_id) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (entity_id, study_id, cmoc_id, entity_type.value, extracted.label,
                         extracted.verbatim_quote, start, end, resolved,
                         "tier:extraction", PROMPT_VERSION, verdict.support_score, run_id),
                    )
                    label_to_entity[extracted.label.strip().lower()] = (entity_id, entity_type)
                    stats["entities"] += 1

            dr_map = domain_range_map()
            for relation in cmoc.relations:
                subj = label_to_entity.get(relation.subject_label.strip().lower())
                obj = label_to_entity.get(relation.object_label.strip().lower())
                if not subj or not obj:
                    continue  # dangling labels — extractor error, skip (counted implicitly)
                predicate = Predicate(relation.predicate)
                domain, range_ = dr_map[predicate]
                valid = subj[1] in domain and obj[1] in range_
                stored_predicate = predicate.value if valid else Predicate.UNTYPED_CANDIDATE.value
                if not valid:
                    stats["demoted_relations"] += 1
                conn.execute(
                    "INSERT INTO typed_relations (relation_id, study_id, cmoc_id, predicate, "
                    "subject_entity_id, object_entity_id, constraint_valid, run_id) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (f"{cmoc_id}-r-{uuid.uuid4().hex[:6]}", study_id, cmoc_id,
                     stored_predicate, subj[0], obj[0], valid, run_id),
                )
                stats["relations"] += 1
        stats["cmocs"] += 1
        persisted.append((cmoc_id, cmoc))

    # ── Consistency Checker (Gap 3): an independent second reviewer, DIFFERENT model
    #    family, checks every study's CMOCs against their quotes — Richmond's "all 28
    #    checked for consistency by another reviewer" convention (L248-250). ──────────
    if persisted:
        _run_consistency_checker(study_id, persisted, run_id, stats)

    log_audit_event(run_id, "cmoc_extraction_agent", "study_extracted",
                    subject_ref=study_id,
                    detail={**stats, "prompt_version": PROMPT_VERSION,
                            "limitations": result.study_limitations})
    return stats


def _run_consistency_checker(
    study_id: str, persisted: list[tuple[str, ExtractedCMOC]], run_id: str, stats: dict
) -> None:
    """Second-reviewer pass: independently confirm/flag each CMOC; persist verdicts.

    Disagreements are recorded on the cmocs row and surfaced at HITL-2 for the human
    to adjudicate — the machine never silently overrides one expert with another.
    """
    _cats = ("contexts", "mechanism_resources", "mechanism_responses", "outcomes")

    def _one(i: int, cmoc: ExtractedCMOC) -> str:
        quotes = [e.verbatim_quote[:120] for cat in _cats for e in getattr(cmoc, cat)]
        return (
            f"CMOC #{i} (polarity={cmoc.polarity}):\n"
            f"  statement: {cmoc.narrative_statement}\n"
            f"  contexts: {[e.label for e in cmoc.contexts]}\n"
            f"  resources: {[e.label for e in cmoc.mechanism_resources]}\n"
            f"  responses: {[e.label for e in cmoc.mechanism_responses]}\n"
            f"  outcomes: {[e.label for e in cmoc.outcomes]}\n"
            f"  quotes: {quotes}"
        )

    listing = "\n\n".join(_one(i, cmoc) for i, (_, cmoc) in enumerate(persisted))
    review = call_structured(
        tier="gold_coder",  # deliberately a different model family than the extractor
        system_prompt=persona("consistency_checker"),
        user_prompt=(
            f"STUDY {study_id}. The lead coder proposed these CMOCs. Independently check each "
            f"one for consistency with its quotes and realist coding conventions.\n\n{listing}"
        ),
        schema=ConsistencyReview, run_id=run_id,
    )
    verdict_by_index = {c.cmoc_index: c for c in review.checks}
    with get_connection() as conn:
        conn.execute("ALTER TABLE cmocs ADD COLUMN IF NOT EXISTS checker_agrees BOOLEAN")
        conn.execute("ALTER TABLE cmocs ADD COLUMN IF NOT EXISTS checker_notes TEXT")
        for i, (cmoc_id, _) in enumerate(persisted):
            chk = verdict_by_index.get(i)
            agrees = chk.agrees if chk else True
            note = (chk.issue if chk else "") or review.study_note
            if not agrees:
                stats["checker_flagged"] += 1
            conn.execute(
                "UPDATE cmocs SET checker_agrees=%s, checker_notes=%s WHERE cmoc_id=%s",
                (agrees, note, cmoc_id),
            )
