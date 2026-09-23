"""Synthetic revision ledgers only; no attributed research intervention is fabricated."""

from copy import deepcopy

import pytest

from res_pipeline.evidence.interventions import (
    RevisionSubmission,
    apply_revision,
    parent_inputs,
    prepare,
    record_hash,
    validate_and_revise,
)
from res_pipeline.evidence.provenance import read_json, write_json


@pytest.fixture
def parent(tmp_path):
    source = tmp_path / "source"
    theory = {
        "theory_id": "PT01",
        "title": "Synthetic initial title",
        "context": "Synthetic learners",
        "resource": "Synthetic resource",
        "response": "Synthetic response",
        "outcome": "Synthetic outcome",
        "direction": "unmeasured",
        "finding_ids": ["S001-F01"],
        "explanation": "Synthetic hypothesis",
        "rival_explanations": [],
        "limitations": ["Synthetic test only"],
        "evidence_gaps": [],
        "human_approval": None,
    }
    write_json(
        source / "programme_theory.json",
        {"overview": "Synthetic overview", "theories": [theory], "unanswered_questions": []},
    )
    write_json(source / "findings.json", [{"finding_id": "S001-F01"}])
    write_json(source / "config.json", {"prior_budget_runs": [], "budget_usd": 50})
    for name in ("source_pages.json", "corpus_manifest.json", "reference_snapshot.json"):
        write_json(source / name, {"synthetic": True})
    return source


def proposal(source):
    hashes, original, _ = parent_inputs(source)
    old = original["theories"][0]
    replacement = {k: v for k, v in old.items() if k not in {"theory_id", "human_approval"}}
    replacement["title"] = "Synthetic revised title"
    return {
        "parent_input_sha256": hashes,
        "summary_edit": None,
        "edits": [
            {
                "edit_id": "EDIT01",
                "action": "replace",
                "theory_id": "PT01",
                "before_sha256": record_hash(old),
                "replacement": replacement,
                "reason": "Synthetic revision, not research evidence",
                "basis_finding_ids": ["S001-F01"],
                "source_locator_and_note": "Synthetic page 1",
                "attribution": {
                    "actor": "Synthetic fixture actor",
                    "actor_type": "ai_assistant",
                    "recorded_at": "2026-09-23T12:00:00+00:00",
                    "minutes": 1,
                    "assistance_disclosure": "Entirely synthetic automated test",
                },
            }
        ],
    }


def test_empty_preparation_is_not_an_intervention(parent):
    dest = parent.parent / "prepared"
    result = prepare(parent, dest)
    assert result["recorded_changes"] == 0
    assert result["status"] == "prepared_no_intervention"
    with pytest.raises(ValueError, match="Empty ledger"):
        apply_revision(parent, dest / "revision_submission.json", parent.parent / "invalid")
    assert not (parent.parent / "invalid").exists()


def test_revision_keeps_parent_reference_and_evidence_unchanged(parent):
    before = {p.name: p.read_bytes() for p in parent.iterdir()}
    submission = parent.parent / "submission.json"
    write_json(submission, proposal(parent))
    dest = parent.parent / "revision"
    status = apply_revision(parent, submission, dest)
    assert {p.name: p.read_bytes() for p in parent.iterdir()} == before
    assert (dest / "parent_programme_theory.json").read_bytes() == before["programme_theory.json"]
    assert (dest / "findings.json").read_bytes() == before["findings.json"]
    assert (dest / "reference_snapshot.json").read_bytes() == before["reference_snapshot.json"]
    revised = read_json(dest / "programme_theory.json")
    assert revised["theories"][0]["title"] == "Synthetic revised title"
    assert revised["theories"][0]["human_approval"] is None
    assert status["claimed_actor_types"] == ["ai_assistant"]
    assert status["human_validation"] == "pending" and status["intervention_effect"] is None
    with pytest.raises(FileExistsError):
        apply_revision(parent, submission, dest)


@pytest.mark.parametrize(
    "mutation,error",
    [
        ("stale_record", "Stale"),
        ("unknown_evidence", "unknown evidence"),
        ("duplicate_target", "competing edits"),
        ("noop", "No-op"),
        ("timezone", "timezone"),
    ],
)
def test_invalid_revision_has_no_silent_repair(parent, mutation, error):
    value = proposal(parent)
    edit = value["edits"][0]
    if mutation == "stale_record":
        edit["before_sha256"] = "wrong"
    if mutation == "unknown_evidence":
        edit["basis_finding_ids"] = ["MISSING"]
    if mutation == "duplicate_target":
        value["edits"].append(deepcopy(edit))
    if mutation == "noop":
        edit["replacement"]["title"] = "Synthetic initial title"
    if mutation == "timezone":
        edit["attribution"]["recorded_at"] = "2026-09-23T12:00:00"
    _, original, findings = parent_inputs(parent)
    with pytest.raises(ValueError, match=error):
        validate_and_revise(original, findings, RevisionSubmission.model_validate(value))


def test_reference_change_invalidates_old_submission(parent):
    path = parent.parent / "submission.json"
    write_json(path, proposal(parent))
    write_json(parent / "reference_snapshot.json", {"changed": True})
    with pytest.raises(ValueError, match="identities changed"):
        apply_revision(parent, path, parent.parent / "revision")


def test_split_preserves_withdrawn_record_in_history(parent):
    value = proposal(parent)
    withdrawal = value["edits"][0]
    addition = deepcopy(withdrawal)
    withdrawal.update(action="withdraw", replacement=None)
    addition.update(edit_id="EDIT02", action="add", theory_id="PT02", before_sha256=None)
    value["edits"].append(addition)
    second = deepcopy(addition)
    second.update(edit_id="EDIT03", theory_id="PT03")
    second["replacement"]["title"] = "Synthetic second branch"
    value["edits"].append(second)
    _, original, findings = parent_inputs(parent)
    revised, events = validate_and_revise(
        original, findings, RevisionSubmission.model_validate(value)
    )
    assert [t["theory_id"] for t in revised["theories"]] == ["PT02", "PT03"]
    assert events[0]["before"]["theory_id"] == "PT01" and events[0]["after"] is None


def test_same_directory_cannot_overwrite_frozen_parent(parent):
    with pytest.raises(ValueError, match="sibling"):
        prepare(parent, parent)
