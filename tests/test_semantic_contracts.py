import pytest

from res_pipeline.evidence.semantic_contracts import SemanticExtraction, audit_semantic_extraction

TEXT = "The training reduced diagnostic errors compared with control at one week."


def extraction():
    evidence = [{"page": 1, "quote": TEXT}]
    return SemanticExtraction(
        entities=[
            {
                "local_id": "E1",
                "label": "training",
                "role": "resource",
                "representation": "explicit_mention",
                "evidence": evidence,
                "interpretation_note": "Fixture",
            },
            {
                "local_id": "E2",
                "label": "diagnostic errors",
                "role": "outcome",
                "representation": "explicit_mention",
                "evidence": evidence,
                "interpretation_note": "Fixture",
            },
        ],
        assertions=[
            {
                "local_id": "A1",
                "subject_id": "E1",
                "predicate": "reduced",
                "object_id": "E2",
                "kind": "reported_effect",
                "context": "Fixture learners",
                "comparator": "control",
                "timepoint": "one week",
                "outcome_definition": "diagnostic errors",
                "statistical_direction": "decrease",
                "educational_interpretation": "benefit",
                "inference_status": "reported_result",
                "explanation": "Fixture only",
                "evidence": evidence,
                "limitations": [],
            }
        ],
        omissions_and_uncertainties=[],
    )


def test_decreased_errors_are_not_forced_to_mean_harm():
    output = audit_semantic_extraction(extraction(), {1: TEXT}, "TEST")
    relation = output["assertions"][0]
    assert relation["statistical_direction"] == "decrease"
    assert relation["educational_interpretation"] == "benefit"
    assert relation["source_checks_passed"]
    assert relation["semantic_review"] == "pending" and relation["human_approval"] is None


def test_null_is_not_relabelled_as_harm():
    value = extraction()
    value.assertions[0].statistical_direction = "no_statistical_difference"
    value.assertions[0].educational_interpretation = "harm"
    output = audit_semantic_extraction(value, {1: TEXT}, "TEST")
    assert (
        "null_difference_cannot_be_benefit_or_harm" in output["assertions"][0]["validation_issues"]
    )


def test_relation_evidence_is_checked_separately_from_entity_quotes():
    value = extraction()
    value.assertions[0].evidence[0].quote = "Training increased diagnostic errors."
    output = audit_semantic_extraction(value, {1: TEXT}, "TEST")
    assert all(e["source_checks_passed"] for e in output["entities"])
    assert "unlocated_relation_evidence" in output["assertions"][0]["validation_issues"]


def test_dangling_endpoint_and_inference_inflation_are_not_admitted():
    value = extraction()
    value.assertions[0].subject_id = "ABSENT"
    value.assertions[0].inference_status = "model_hypothesis"
    output = audit_semantic_extraction(value, {1: TEXT}, "TEST")
    assert set(output["assertions"][0]["validation_issues"]) == {
        "unknown_entity_endpoint:ABSENT",
        "inference_cannot_be_labelled_measured_contrast",
    }


def test_duplicate_entities_are_not_silently_overwritten():
    value = extraction()
    value.entities.append(value.entities[0].model_copy(deep=True))
    with pytest.raises(ValueError, match="Duplicate"):
        audit_semantic_extraction(value, {1: TEXT}, "TEST")
