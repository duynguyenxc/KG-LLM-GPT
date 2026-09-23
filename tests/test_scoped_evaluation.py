"""The theory evaluator must not count source-only evidence as synthesis recovery."""

from res_pipeline.evidence.evaluation import ScopedComparison, validate_scoped_comparison


def assessment(**changes):
    value = dict(
        theory_ids=["PT01"],
        finding_ids=["F01"],
        verdict="partial",
        dimensions=[
            dict(
                dimension=d,
                match="partial",
                reason="Fixture correspondence",
                theory_anchors=[
                    dict(theory_id="PT01", field="context", quote="Novices in a specific task")
                ],
            )
            for d in ("context", "resource", "response", "outcome", "direction", "qualifiers")
        ],
        rationale="Fixture",
        critical_difference="Fixture",
        review_question="Fixture",
    )
    value.update(changes)
    return ScopedComparison(**value)


THEORIES = {"PT01": {"context": "Novices in a specific task", "finding_ids": ["F01"]}}
FINDINGS = {"F01": {}, "F02": {}}


def test_partial_cannot_borrow_evidence_from_an_unselected_theory():
    issues = validate_scoped_comparison(assessment(finding_ids=["F02"]), THEORIES, FINDINGS)
    assert "evidence_outside_selected_theories" in issues


def test_source_only_partial_is_not_a_theory_match():
    issues = validate_scoped_comparison(assessment(theory_ids=[]), THEORIES, FINDINGS)
    assert "verdict_requires_theory_and_linked_evidence" in issues


def test_anchor_cannot_change_a_theorys_polarity():
    value = assessment()
    value.dimensions[0].theory_anchors[0].quote = "Experts in a specific task"
    assert "invalid_theory_anchor:context:PT01" in validate_scoped_comparison(
        value, THEORIES, FINDINGS
    )


def test_valid_scope_does_not_claim_semantic_validation():
    assert validate_scoped_comparison(assessment(), THEORIES, FINDINGS) == []
    # Matching exact text only establishes location: the fixture uses the same context
    # span for every dimension, which an independent semantic reviewer must reject.


def test_no_counterpart_cannot_simultaneously_claim_matched_dimensions():
    value = assessment(theory_ids=[], finding_ids=[], verdict="not_recovered")
    assert "not_recovered_conflicts_with_selected_counterpart" in validate_scoped_comparison(
        value, THEORIES, FINDINGS
    )
    for dim in value.dimensions:
        dim.match = "absent"
        dim.theory_anchors = []
    assert validate_scoped_comparison(value, THEORIES, FINDINGS) == []
