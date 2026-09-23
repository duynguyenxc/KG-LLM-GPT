"""Synthetic engineering cases only; none are scientific evaluation observations."""

import json

import pytest

from res_pipeline.evidence import semantic_pipeline as pipeline
from res_pipeline.evidence.provenance import read_json, write_json
from res_pipeline.evidence.semantic_contracts import SemanticExtraction

TEXT = "Training reduced errors compared with control at one week."


@pytest.fixture
def candidate():
    evidence = [{"page": 1, "quote": TEXT}]
    return SemanticExtraction.model_validate(
        {
            "entities": [
                {
                    "local_id": "E1",
                    "label": "Training",
                    "role": "resource",
                    "representation": "explicit_mention",
                    "evidence": evidence,
                    "interpretation_note": "Synthetic",
                },
                {
                    "local_id": "E2",
                    "label": "errors",
                    "role": "outcome",
                    "representation": "explicit_mention",
                    "evidence": evidence,
                    "interpretation_note": "Synthetic",
                },
            ],
            "assertions": [
                {
                    "local_id": "A1",
                    "subject_id": "E1",
                    "predicate": "reduced",
                    "object_id": "E2",
                    "kind": "reported_effect",
                    "context": "Synthetic",
                    "comparator": "control",
                    "timepoint": "one week",
                    "outcome_definition": "errors",
                    "statistical_direction": "decrease",
                    "educational_interpretation": "benefit",
                    "inference_status": "reported_result",
                    "explanation": "Synthetic",
                    "evidence": evidence,
                    "limitations": [],
                }
            ],
            "omissions_and_uncertainties": [],
        }
    )


def review_for(candidate):
    return pipeline.SemanticReview.model_validate(
        {
            "assessments": [
                {
                    "record_type": kind,
                    "local_id": r.local_id,
                    "verdict": "supported",
                    "rationale": "Synthetic test judgment, never human validation",
                    "source_checks_to_revisit": [],
                }
                for kind, rows in (
                    ("entity", candidate.entities),
                    ("assertion", candidate.assertions),
                )
                for r in rows
            ],
            "omissions_and_uncertainties": [],
        }
    )


@pytest.fixture
def source(tmp_path):
    source = tmp_path / "baseline"
    write_json(
        source / "corpus_manifest.json",
        {
            "papers": [
                {
                    "paper_id": "S001",
                    "title": "Synthetic fixture",
                    "doi": None,
                    "year": 2000,
                    "availability": "metadata_snippet_only",
                    "study_family_id": "S001",
                    "source_path": "private/benchmark-named-source",
                    "pages": 1,
                    "text_characters": len(TEXT),
                    "reference_answer": "DO NOT INCLUDE",
                }
            ]
        },
    )
    write_json(source / "source_pages.json", [{"paper_id": "S001", "page": 1, "text": TEXT}])
    write_json(
        source / "config.json",
        {"extractor_model": "synthetic", "critic_model": "synthetic", "prior_budget_runs": []},
    )
    return source


def test_offline_preparation_never_creates_api_client(source, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Offline preparation initialized an API client")

    monkeypatch.setattr(pipeline, "RunClient", forbidden)
    destination = source.parent / "prepared"
    result = pipeline.run(source, destination)
    assert result["machine_stage"] == "prepared_not_executed"
    assert result["assertion_candidates"] == 0
    assert not (destination / "calls").exists()
    packet = (destination / "packets/S001.json").read_text()
    assert "DO NOT INCLUDE" not in packet and "private/" not in packet
    assert "reference_answer" not in packet


@pytest.mark.parametrize("change", ["missing", "duplicate", "unknown"])
def test_critic_must_cover_each_typed_id_once(candidate, change):
    review = review_for(candidate)
    if change == "missing":
        review.assessments.pop()
    elif change == "duplicate":
        review.assessments.append(review.assessments[0])
    else:
        review.assessments[0].local_id = "OTHER"
    with pytest.raises(ValueError, match="coverage"):
        pipeline.audit_review(candidate, review, {1: TEXT}, "S001")


def test_supported_assertion_cannot_bypass_rejected_endpoint(candidate):
    review = review_for(candidate)
    review.assessments[0].verdict = "unsupported"
    result = pipeline.audit_review(candidate, review, {1: TEXT}, "S001")
    assert result["assertions"][0]["source_checks_passed"]
    assert not result["assertions"][0]["machine_eligible"]
    assert "endpoint_not_machine_eligible" in result["assertions"][0]["validation_issues"]


def test_located_quotes_and_ai_support_do_not_promote_hypothesis(candidate):
    candidate.assertions[0].inference_status = "model_hypothesis"
    candidate.assertions[0].statistical_direction = "unmeasured"
    result = pipeline.audit_review(candidate, review_for(candidate), {1: TEXT}, "S001")
    assertion = result["assertions"][0]
    assert assertion["machine_eligible"]
    assert assertion["evidence_class"] == "model_hypothesis"
    assert assertion["human_approval"] is None


def test_ai_critic_cannot_admit_unlocated_relation_quote(candidate):
    candidate.assertions[0].evidence[0].quote = "An invented quotation absent from the source."
    result = pipeline.audit_review(candidate, review_for(candidate), {1: TEXT}, "S001")
    assert not result["assertions"][0]["machine_eligible"]
    assert result["assertions"][0]["semantic_review"]["verdict"] == "supported"


def test_synthetic_end_to_end_retains_qualifiers_and_does_not_overwrite_on_prepare(
    source, candidate
):
    class SyntheticClient:
        def call(self, name, model, system, user, schema):
            packet = json.loads(user)
            assert "reference" not in packet
            return candidate if schema is SemanticExtraction else review_for(candidate)

    destination = source.parent / "synthetic-run"
    original = (source / "source_pages.json").read_bytes()
    result = pipeline.run(source, destination, execute=True, client=SyntheticClient())
    assert result["machine_stage"] == "complete"
    assert result["human_validation"] == "pending"
    graph = read_json(destination / "semantic_graph.json")
    assertion = graph["edges"][0]["qualified_assertion"]
    assert assertion["comparator"] == "control" and assertion["timepoint"] == "one week"
    assert assertion["evidence"][0]["source_span"] == TEXT
    assert assertion["study_family_id"] == "S001"
    assert assertion["source_availability"] == "metadata_snippet_only"
    assert pipeline.run(source, destination) == result
    assert (source / "source_pages.json").read_bytes() == original


def test_bad_critic_coverage_cannot_publish_complete_run(source, candidate):
    class IncompleteCritic:
        def call(self, name, model, system, user, schema):
            if schema is SemanticExtraction:
                return candidate
            review = review_for(candidate)
            review.assessments.pop()
            return review

    destination = source.parent / "incomplete"
    with pytest.raises(ValueError, match="coverage"):
        pipeline.run(source, destination, execute=True, client=IncompleteCritic())
    assert read_json(destination / "run_status.json")["machine_stage"] != "complete"
    assert not (destination / "papers/S001.json").exists()


@pytest.mark.parametrize(
    "target",
    ["packets/S001.json", "inputs/source_pages.json", "code_snapshot/semantic_pipeline.py"],
)
def test_frozen_packet_or_snapshot_tampering_is_rejected(source, target):
    destination = source.parent / "prepared"
    pipeline.run(source, destination)
    (destination / target).write_text("changed")
    with pytest.raises(ValueError, match="Changed"):
        pipeline.run(source, destination)
    assert (destination / target).read_text() == "changed"


def test_changed_source_selection_and_budget_paths_are_rejected(source):
    destination = source.parent / "prepared"
    with pytest.raises(ValueError, match="Unknown"):
        pipeline.run(source, destination, ["S099"])
    with pytest.raises(ValueError, match="Budget"):
        pipeline.run(source, destination, budget_runs=["../unrelated"])
    pipeline.run(source, destination)
    write_json(
        source / "source_pages.json", [{"paper_id": "S001", "page": 1, "text": TEXT.upper()}]
    )
    with pytest.raises(ValueError, match="Changed manifest"):
        pipeline.run(source, destination)
