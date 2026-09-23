"""Source-grounded entity and conditional-relation contracts; not a trained NER model."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from res_pipeline.evidence.provenance import locate_quote
from res_pipeline.evidence.schemas import Record


class SourceQuotation(Record):
    page: int = Field(ge=1)
    quote: str = Field(min_length=10)


class SemanticEntity(Record):
    local_id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]*$")
    label: str = Field(min_length=1)
    role: Literal[
        "context", "resource", "response", "outcome", "population", "assessment", "study_design"
    ]
    representation: Literal["explicit_mention", "source_grounded_abstraction"]
    evidence: list[SourceQuotation] = Field(min_length=1)
    interpretation_note: str


class ConditionalAssertion(Record):
    local_id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]*$")
    subject_id: str
    predicate: str = Field(min_length=1)
    object_id: str
    kind: Literal[
        "reported_effect", "explanatory_link", "measurement", "population_link", "composition"
    ]
    context: str = Field(min_length=1)
    comparator: str = Field(min_length=1)
    timepoint: str = Field(min_length=1)
    outcome_definition: str = Field(min_length=1)
    statistical_direction: Literal[
        "increase", "decrease", "no_statistical_difference", "mixed", "unmeasured", "not_applicable"
    ]
    educational_interpretation: Literal[
        "benefit", "harm", "no_detected_difference", "mixed", "unclear", "not_applicable"
    ]
    inference_status: Literal[
        "reported_result", "author_inference", "model_hypothesis", "design_description"
    ]
    explanation: str
    evidence: list[SourceQuotation] = Field(min_length=1)
    limitations: list[str]


class SemanticExtraction(Record):
    entities: list[SemanticEntity]
    assertions: list[ConditionalAssertion]
    omissions_and_uncertainties: list[str]


def audit_semantic_extraction(
    extraction: SemanticExtraction, pages: dict[int, str], paper_id: str
) -> dict:
    """Locate source text and check graph integrity; semantic support stays unreviewed."""
    entity_ids = [e.local_id for e in extraction.entities]
    assertion_ids = [a.local_id for a in extraction.assertions]
    if len(entity_ids) != len(set(entity_ids)) or len(assertion_ids) != len(set(assertion_ids)):
        raise ValueError("Duplicate local entity/assertion IDs")
    if set(entity_ids) & set(assertion_ids):
        raise ValueError("Entity and assertion IDs must occupy distinct namespaces")
    entities, assertions = [], []

    def locate(evidence):
        result = []
        for quote in evidence:
            text = pages.get(quote.page, "")
            location = locate_quote(text, quote.quote)
            result.append(
                {
                    **quote.model_dump(),
                    **location,
                    "source_span": text[location["start"] : location["end"]]
                    if location["located"]
                    else None,
                }
            )
        return result

    for entity in extraction.entities:
        evidence = locate(entity.evidence)
        issues = [] if all(q["located"] for q in evidence) else ["unlocated_entity_evidence"]
        if entity.representation == "explicit_mention" and not any(
            locate_quote(q.quote, entity.label)["located"] for q in entity.evidence
        ):
            issues.append("explicit_label_not_in_evidence")
        entities.append(
            {
                **entity.model_dump(),
                "entity_id": f"{paper_id}:{entity.local_id}",
                "paper_id": paper_id,
                "evidence": evidence,
                "validation_issues": issues,
                "source_checks_passed": not issues,
                "semantic_review": "pending",
                "human_approval": None,
            }
        )
    audited = {e["local_id"]: e for e in entities}
    for assertion in extraction.assertions:
        evidence = locate(assertion.evidence)
        issues = [] if all(q["located"] for q in evidence) else ["unlocated_relation_evidence"]
        for endpoint in (assertion.subject_id, assertion.object_id):
            if endpoint not in audited:
                issues.append("unknown_entity_endpoint:" + endpoint)
            elif not audited[endpoint]["source_checks_passed"]:
                issues.append("unlocated_entity_endpoint:" + endpoint)
        if (
            assertion.statistical_direction == "no_statistical_difference"
            and assertion.educational_interpretation in {"benefit", "harm"}
        ):
            issues.append("null_difference_cannot_be_benefit_or_harm")
        if assertion.inference_status in {
            "author_inference",
            "model_hypothesis",
            "design_description",
        } and assertion.statistical_direction not in {"unmeasured", "not_applicable"}:
            issues.append("inference_cannot_be_labelled_measured_contrast")
        assertions.append(
            {
                **assertion.model_dump(),
                "assertion_id": f"{paper_id}:{assertion.local_id}",
                "paper_id": paper_id,
                "subject_entity_id": f"{paper_id}:{assertion.subject_id}",
                "object_entity_id": f"{paper_id}:{assertion.object_id}",
                "evidence": evidence,
                "validation_issues": sorted(set(issues)),
                "source_checks_passed": not issues,
                "semantic_review": "pending",
                "human_approval": None,
            }
        )
    return {
        "paper_id": paper_id,
        "entities": entities,
        "assertions": assertions,
        "omissions_and_uncertainties": extraction.omissions_and_uncertainties,
        "interpretation": "Source checks locate quotes and check structural consistency; they do not establish relation entailment or causal validity. No canonical merges are performed.",
    }
