import csv

import pytest

from res_pipeline.evidence.pipeline import validate_comparison
from res_pipeline.evidence.provenance import locate_quote
from res_pipeline.evidence.reporting import write_csv
from res_pipeline.evidence.retrieval import retrieve_pages
from res_pipeline.evidence.review import summarize_reviews
from res_pipeline.evidence.schemas import Comparison


def test_invalid_source_line_repair_cannot_enter_synthesis():
    from res_pipeline.evidence.pipeline import audit_findings, repair_quotes
    from res_pipeline.evidence.schemas import CitationSpanRepairs, Extraction, ExtractionReview

    extraction = Extraction(
        design="fixture",
        population="fixture",
        sample_description="fixture",
        source_limitations=[],
        findings=[
            dict(
                context="fixture",
                resource="fixture",
                response="not reported",
                outcome="fixture",
                direction="null",
                comparator="fixture",
                timepoint="fixture",
                response_status="not_reported",
                outcome_status="measured",
                explanation="fixture",
                limitations=[],
                evidence=[dict(role="outcome", page=1, quote="An invented unlocated result.")],
            )
        ],
    )

    class FakeClient:
        def call(self, *args):
            return CitationSpanRepairs(
                repairs=[
                    dict(
                        citation_id="0:0",
                        spans=[dict(page=1, first_line=1, last_line=99)],
                        explanation="bad range",
                    )
                ]
            )

    paper = dict(
        paper_id="S001",
        study_family_id="S001",
        availability="fulltext_available",
        source_path="fixture.pdf",
    )
    pages = [dict(paper_id="S001", page=1, text="There was no improvement.")]
    repaired, _ = repair_quotes(
        FakeClient(), paper, pages, "", extraction, {"critic_model": "fixture"}
    )
    review = ExtractionReview(
        assessments=[
            dict(
                finding_index=0,
                verdict="supported",
                response_evidence="not_reported",
                outcome_evidence="measured",
                rationale="fixture",
                problems=[],
            )
        ],
        missed_evidence=[],
    )
    finding = audit_findings(paper, pages, repaired, review)[0]
    assert finding["evidence"][0]["quote"] == "An invented unlocated result."
    assert not finding["eligible_for_synthesis"]


def test_quote_locator_rejects_polarity_change_and_substring_fragments():
    source = "There was no improvement in diagnostic accuracy."
    assert not locate_quote(source, "There was improvement in diagnostic accuracy.")["located"]
    assert not locate_quote(
        source, "There was no improvement in diagnostic accuracy at follow-up."
    )["located"]
    found = locate_quote(source, "There was no\nimprovement in diagnostic accuracy.")
    assert found["located"] and source[found["start"] : found["end"]] == source
    assert not locate_quote(
        "Students were not able to improve.", "Students were notable to improve."
    )["located"]


def test_export_preserves_values_not_dictionary_keys(tmp_path):
    target = tmp_path / "output.csv"
    write_csv(target, [{"paper_id": "S006", "finding": "null, not harm"}], ["paper_id", "finding"])
    with target.open(encoding="utf-8-sig", newline="") as stream:
        assert list(csv.DictReader(stream)) == [{"paper_id": "S006", "finding": "null, not harm"}]


def test_pdf_typography_normalization_preserves_raw_offsets():
    source = "The ﬁnal feed-\nback showed no improvement."
    found = locate_quote(source, "The final feedback showed no improvement.")
    assert found["located"] and source[found["start"] : found["end"]] == source
    assert not locate_quote(source, "The final feedback showed improvement.")["located"]


def comparison():
    return Comparison(
        theory_ids=["PT01"],
        finding_ids=["S006-F01"],
        verdict="equivalent",
        dimensions=[
            {"dimension": dimension, "match": "equivalent", "reason": "fixture"}
            for dimension in [
                "context",
                "resource",
                "response",
                "outcome",
                "direction",
                "qualifiers",
            ]
        ],
        rationale="fixture",
        critical_difference="fixture",
        review_question="fixture",
    )


def test_partial_mechanism_cannot_receive_equivalent_configuration_verdict():
    value = comparison()
    value.dimensions[2].match = "partial"
    result = validate_comparison(value, {"PT01": {"finding_ids": ["S006-F01"]}}, {"S006-F01": {}})
    assert result["verdict"] == "partial"
    assert result["adjudicated_verdict"] is None


def test_comparison_cannot_cite_nonexistent_or_unlinked_evidence():
    with pytest.raises(ValueError, match="nonexistent"):
        validate_comparison(comparison(), {"PT01": {}}, {})
    result = validate_comparison(comparison(), {"PT01": {"finding_ids": []}}, {"S006-F01": {}})
    assert result["verdict"] == "partial"


def test_retrieval_returns_source_page_identity_and_rejects_empty_overlap():
    pages = [
        {"paper_id": "S015", "page": 4, "text": "Fear and stress during simulation"},
        {"paper_id": "S027", "page": 2, "text": "Retention following repeated testing"},
    ]
    assert retrieve_pages("stress simulation", pages)[0]["paper_id"] == "S015"
    assert retrieve_pages("unrelatedxyz", pages) == []


def test_empty_human_forms_do_not_generate_validation_metrics():
    value = summarize_reviews({}, {}, {}, 18)
    assert value["kappa"] is None and value["configuration_recovery"] is None
    assert value["adjudicated_rows"] == 0


def test_partial_human_review_does_not_become_whole_corpus_recall():
    a = {"RC01": {"verdict": "equivalent"}, "RC02": {"verdict": "partial"}}
    b = {"RC01": {"verdict": "equivalent"}, "RC02": {"verdict": "equivalent"}}
    value = summarize_reviews(a, b, {"RC01": a["RC01"]}, 18)
    assert value["paired_rows"] == 2 and value["raw_agreement"] == 0.5
    assert value["configuration_recovery"] is None


def test_resume_preserves_unfinished_requests_and_never_retries_a_raw_response(tmp_path):
    from res_pipeline.evidence.provenance import write_json
    from res_pipeline.evidence.resume import prepare_resume

    call = tmp_path / "calls" / "extract_S001"
    write_json(call / "request.json", {"model": "fixture"})
    assert prepare_resume(tmp_path) == ["extract_S001"]
    assert (tmp_path / "calls_archive/attempt-001/extract_S001/request.json").exists()
    write_json(call / "request.json", {"model": "fixture"})
    write_json(call / "response.json", {"raw": "must inspect before retry"})
    with pytest.raises(RuntimeError, match="raw response"):
        prepare_resume(tmp_path)


def test_provider_credit_rejection_is_recorded_and_halts_new_calls(tmp_path):
    from types import SimpleNamespace

    import httpx
    from openai import RateLimitError

    from res_pipeline.evidence.provenance import RunClient, read_json

    config = {
        "reasoning_effort": "medium",
        "max_completion_tokens": 100,
        "prices_per_million": {"fixture": {"input": 1, "output": 1}},
        "budget_usd": 1,
    }
    client = RunClient(tmp_path, config, "test-not-a-real-key")

    def rejected(**kwargs):
        response = httpx.Response(429, request=httpx.Request("POST", "https://example.invalid"))
        raise RateLimitError(
            "No credits", response=response, body={"code": "credit_balance_exhausted"}
        )

    client.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=rejected))
    )
    with pytest.raises(RateLimitError):
        client.call("first", "fixture", "fixture", "fixture", Comparison)
    assert read_json(tmp_path / "calls/first/error.json")["code"] == "credit_balance_exhausted"
    assert sum(row["budget_charge_usd"] for row in client.ledger()) == 0
    with pytest.raises(RuntimeError, match="halted"):
        client.call("second", "fixture", "fixture", "fixture", Comparison)


def test_complete_export_does_not_invent_or_overwrite_human_review(tmp_path):
    from res_pipeline.evidence.provenance import read_json, write_json
    from res_pipeline.evidence.reporting import export_run

    components = dict(
        context="Test learners",
        resource="Test instruction",
        response="not reported",
        outcome="No improvement",
        direction="null",
    )
    finding = {
        **components,
        "finding_id": "S006-F01",
        "paper_id": "S006",
        "study_family_id": "S006",
        "availability": "fulltext_available",
        "source_path": "test-fixture.pdf",
        "comparator": "test control",
        "timepoint": "one week",
        "response_status": "not_reported",
        "outcome_status": "measured",
        "all_quotes_located": True,
        "eligible_for_synthesis": True,
        "limitations": [],
        "critic": {"verdict": "supported", "rationale": "TEST MODEL AUDIT"},
        "evidence": [
            dict(
                role="outcome",
                page=1,
                quote="No improvement was seen.",
                source_span="No improvement was seen.",
                located=True,
                start=0,
                end=24,
                method="exact",
            )
        ],
    }
    theory = {
        **components,
        "theory_id": "PT01",
        "title": "TEST THEORY",
        "finding_ids": ["S006-F01"],
        "explanation": "TEST EXPLANATION",
        "rival_explanations": [],
        "limitations": [],
        "evidence_gaps": [],
    }
    claim = {
        **components,
        "claim_id": "RC01",
        "context_group": "TEST GROUP",
        "pdf_page": 1,
        "source_anchor": "TEST SOURCE",
    }
    result = {
        "claim_id": "RC01",
        **validate_comparison(comparison(), {"PT01": theory}, {"S006-F01": finding}),
    }
    for name, value in {
        "findings.json": [finding],
        "programme_theory.json": {"overview": "TEST ONLY", "theories": [theory]},
        "comparison.json": [result],
        "reference_snapshot.json": {"claims": [claim]},
        "corpus_manifest.json": {"papers": [{"availability": "fulltext_available"}]},
        "run_status.json": {
            "machine_stages": "complete",
            "human_validation": "pending",
            "eligible_findings": 1,
        },
    }.items():
        write_json(tmp_path / name, value)
    (tmp_path / "usage.jsonl").write_text("", encoding="utf-8")
    export_run(tmp_path)
    assert read_json(tmp_path / "metrics.json")["human_agreement_kappa"] is None
    assert "AI: equivalent" not in (tmp_path / "blind_review.html").read_text(encoding="utf-8")
    path = tmp_path / "human_review_coder_A.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert not rows[0]["verdict"]
    rows[0].update(
        verdict="partial",
        reviewer="TEST REVIEWER",
        reviewed_at="2026-09-10",
        rationale="TEST RATIONALE",
    )
    write_csv(path, rows, list(rows[0]))
    before = path.read_bytes()
    export_run(tmp_path)
    assert path.read_bytes() == before
    metrics = read_json(tmp_path / "metrics.json")
    assert metrics["human_adjudicated_rows"] == 0 and metrics["human_configuration_recall"] is None
