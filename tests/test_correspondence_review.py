"""Synthetic record/linkage tests, not human or scientific evaluation observations."""

import csv

import pytest

from res_pipeline.evidence.correspondence_review import (
    DIMENSIONS,
    FIELDS,
    legacy_records,
    read_form,
    semantic_records,
    validate_packet_forms,
    validate_selection,
)
from res_pipeline.evidence.provenance import digest, write_json


@pytest.fixture
def candidates():
    return {
        "a": {
            "id": "a",
            "paper_id": "S001",
            "scope_id": "C1",
            "subject_id": "E1",
            "object_id": "E2",
            "structural_issues": [],
        },
        "b": {
            "id": "b",
            "paper_id": "S001",
            "scope_id": "C1",
            "subject_id": "E2",
            "object_id": "E3",
            "structural_issues": [],
        },
    }


def completed_row():
    return {
        "reference_id": "R01",
        "verdict": "equivalent",
        "candidate_ids": "a;b",
        "match_unit": "connected_path",
        **{k: "equivalent" for k in DIMENSIONS},
        "source_support": "uncertain",
        "source_locator_and_note": "Synthetic fixture only",
        "reference_scope_note": "Synthetic scope",
        "rationale": "Synthetic judgment only",
        "reviewer": "Fixture A",
        "reviewed_at": "2026-09-23",
        "minutes": "2",
    }


def test_connected_path_is_structural_not_semantic_validation(candidates):
    row = completed_row()
    assert validate_selection(row, "relations", candidates) == []
    assert row["source_support"] == "uncertain"


@pytest.mark.parametrize(
    "change,issue",
    [
        ("paper", "path_crosses_source_or_configuration_scope"),
        ("scope", "path_crosses_source_or_configuration_scope"),
        ("endpoint", "path_not_connected_by_actual_entity_ids"),
        ("structure", "selected_relation_has_unresolved_structure"),
    ],
)
def test_no_fabricated_path_from_separate_records(candidates, change, issue):
    if change == "paper":
        candidates["b"]["paper_id"] = "S002"
    if change == "scope":
        candidates["b"]["scope_id"] = "C2"
    if change == "endpoint":
        candidates["b"]["subject_id"] = "E_OTHER"
    if change == "structure":
        candidates["b"]["structural_issues"] = ["unresolved"]
    assert issue in validate_selection(completed_row(), "relations", candidates)


def test_equivalence_cannot_skip_dimensions_or_actual_counterpart(candidates):
    row = completed_row()
    row["context_match"] = "uncertain"
    assert "equivalence_requires_all_six_dimensions" in validate_selection(
        row, "relations", candidates
    )
    row["candidate_ids"] = ""
    assert "correspondence_requires_actual_output_ids" in validate_selection(
        row, "relations", candidates
    )


def test_legacy_adapter_withholds_scores_and_exposes_missing_relation_evidence():
    quote = "Synthetic intervention supports learning."
    original = {
        "entities": [
            {
                "id": "e1",
                "type": "Intervention",
                "title": "intervention",
                "canonical_id": "c1",
                "study_id": "S001",
                "cmoc_id": "C1",
                "description": quote,
                "confidence": 0.99,
            },
            {
                "id": "e2",
                "type": "Outcome",
                "title": "learning",
                "canonical_id": "c2",
                "study_id": "S001",
                "cmoc_id": "C1",
                "description": quote,
                "confidence": 0.99,
            },
        ],
        "relationships": [
            {
                "id": "r1",
                "source": "c1",
                "target": "c2",
                "description": "SUPPORTS",
                "study_id": "S001",
                "cmoc_id": "C1",
                "text_unit_ids": ["e1", "e2"],
                "constraint_valid": True,
            }
        ],
        "cmocs": [
            {
                "id": "C1",
                "study_id": "S001",
                "narrative_statement": "Synthetic narrative",
                "polarity": "positive",
                "verifier_support": 0.99,
            }
        ],
    }
    result = legacy_records(original, [{"paper_id": "S001", "page": 1, "text": quote}])
    assert result["relations"][0]["subject_id"] == "e1"
    assert result["relations"][0]["evidence"] == []
    assert result["entities"][0]["evidence"][0]["located"]
    assert "confidence" not in str(result) and "verifier_support" not in str(result)
    original["entities"][1]["canonical_id"] = "c1"
    original["relationships"][0]["target"] = "c1"
    ambiguous = legacy_records(original, [{"paper_id": "S001", "page": 1, "text": quote}])
    edge = ambiguous["relations"][0]
    assert edge["subject_id"] is None and edge["object_id"] is None
    assert edge["endpoint_candidate_ids"] == ["e1", "e2"]
    assert len(edge["structural_issues"]) == 2


def write_form(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_blank_forms_remain_unreviewed_and_incomplete_population_fails(tmp_path, candidates):
    packet = {
        "references": {"relations": [{"id": "R01"}, {"id": "R02"}]},
        "candidates": {"relations": list(candidates.values())},
    }
    path = tmp_path / "form.csv"
    write_form(path, [{"reference_id": "R01"}, {"reference_id": "R02"}])
    assert read_form(path, "relations", packet) == {}
    write_form(path, [completed_row()])
    with pytest.raises(ValueError, match="population"):
        read_form(path, "relations", packet)


def test_unexecuted_semantic_run_cannot_be_reported_as_missing_recovery(tmp_path):
    write_json(tmp_path / "run_status.json", {"machine_stage": "prepared_not_executed"})
    with pytest.raises(ValueError, match="not completed"):
        semantic_records(tmp_path)


def test_human_adjudication_requires_two_distinct_prior_reviewers(tmp_path, candidates):
    packet = {
        "references": {"relations": [{"id": "R01"}], "concepts": []},
        "candidates": {"relations": list(candidates.values()), "entities": []},
    }
    write_json(tmp_path / "packet.json", packet)
    write_json(
        tmp_path / "manifest.json",
        {"packet_sha256": digest((tmp_path / "packet.json").read_bytes())},
    )
    for role in ["A", "B", "adjudication"]:
        write_form(tmp_path / f"concepts_{role}.csv", [])
        write_form(tmp_path / f"relations_{role}.csv", [{"reference_id": "R01"}])
    blank = validate_packet_forms(tmp_path)
    assert blank["relations"]["ratified_reference_recovery"] is None
    a = completed_row()
    adjud = {**a, "adjudication_reason": "Synthetic reason"}
    write_form(tmp_path / "relations_adjudication.csv", [adjud])
    with pytest.raises(ValueError, match="Adjudication"):
        validate_packet_forms(tmp_path)
    for role in ["A", "B"]:
        write_form(tmp_path / f"relations_{role}.csv", [a])
    with pytest.raises(ValueError, match="same reviewer"):
        validate_packet_forms(tmp_path)
    write_form(tmp_path / "relations_B.csv", [{**a, "reviewer": "Fixture B"}])
    result = validate_packet_forms(tmp_path)
    assert result["relations"]["completed"]["adjudication"] == 1
    assert result["relations"]["ratified_reference_recovery"] is None


def test_nonfinite_review_time_is_rejected(tmp_path, candidates):
    packet = {
        "references": {"relations": [{"id": "R01"}]},
        "candidates": {"relations": list(candidates.values())},
    }
    row = completed_row()
    row["minutes"] = "inf"
    path = tmp_path / "form.csv"
    write_form(path, [row])
    with pytest.raises(ValueError, match="review time"):
        read_form(path, "relations", packet)
