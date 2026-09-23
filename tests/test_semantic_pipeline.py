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


def mixed_source(source):
    corpus = read_json(source / "corpus_manifest.json")
    paper = corpus["papers"][0]
    paper.update(availability="partial_pdf_plus_abstract", pages=2, text_characters=len(TEXT) + 8)
    write_json(source / "corpus_manifest.json", corpus)
    write_json(
        source / "source_pages.json",
        [
            {"paper_id": "S001", "page": 1, "text": "PDF text"},
            {"paper_id": "S001", "page": 2, "text": TEXT},
        ],
    )
    write_json(
        source / "source_locators.json",
        [
            {
                "paper_id": "S001",
                "source_unit": 1,
                "kind": "original_partial_pdf_page",
                "original_page": 1,
            },
            {
                "paper_id": "S001",
                "source_unit": 2,
                "kind": "pubmed_abstract",
                "original_page": None,
                "pmid": "12345",
                "assistant_note": "NEVER SEND",
            },
        ],
    )


def test_abstract_locator_survives_execution_csv_graph_and_readable_report(source, candidate):
    import csv

    mixed_source(source)
    for record in [*candidate.entities, *candidate.assertions]:
        for quote in record.evidence:
            quote.page = 2

    class SyntheticClient:
        def call(self, name, model, system, user, schema):
            assert "NEVER SEND" not in user
            if schema is SemanticExtraction:
                assert "source-unit" in system
                abstract = json.loads(user)["source_pages"][1]
                assert abstract["kind"] == "abstract" and abstract["original_page"] is None
                return candidate
            return review_for(candidate)

    dest = source.parent / "mixed-run"
    pipeline.run(source, dest, execute=True, client=SyntheticClient())
    q = read_json(dest / "assertions.json")[0]["evidence"][0]
    assert q["source_locator"]["kind"] == "abstract"
    assert q["source_locator"]["original_page"] is None
    assert q["source_locator"]["source_url"] == "https://pubmed.ncbi.nlm.nih.gov/12345/"
    with (dest / "assertions.csv").open(encoding="utf-8", newline="") as f:
        row = next(csv.DictReader(f))
    assert json.loads(row["evidence"])[0]["source_locator"] == q["source_locator"]
    graph_quote = read_json(dest / "semantic_graph.json")["edges"][0]["qualified_assertion"][
        "evidence"
    ][0]
    assert graph_quote["source_locator"] == q["source_locator"]
    for path in (dest / "index.html", dest / "sources/S001.html"):
        text = path.read_text(encoding="utf-8")
        assert "PubMed abstract (source unit 2; no PDF page)" in text
        assert "Source page 2" not in text
    # The independent-review exporter must use the same source identity and locator.
    from res_pipeline.evidence.correspondence_review import export_packet

    root = source.parent
    write_json(
        root / "gold/richmond_gold.json",
        {
            "entities": {"E01": {"label": "Synthetic reference", "location": "Synthetic"}},
            "relationships": [],
        },
    )
    (root / "data").mkdir(exist_ok=True)
    (root / "data/paper-Richmond-original.pdf").write_bytes(b"Synthetic path fixture, not a PDF")
    export_packet(root, source, root / "review", semantic_run=dest)
    review_packet = read_json(root / "review/packet.json")
    assert review_packet["pages"][1]["source_locator"]["original_page"] is None
    assert review_packet["pages"][1]["source_locator"]["kind"] == "abstract"
    assert "semantic_review" not in json.dumps(review_packet["candidates"])
    rows = read_json(dest / "locators.json")
    rows[-1]["label"] = "Wrong display"
    write_json(dest / "locators.json", rows)
    with pytest.raises(ValueError, match="locators differ"):
        export_packet(root, source, root / "bad-review", semantic_run=dest)


@pytest.mark.parametrize(
    "change", ["missing", "duplicate", "invented_pdf_page", "wrong_kind", "bad_pmid"]
)
def test_malformed_locator_map_rejected_before_preparation(source, change):
    mixed_source(source)
    path = source / "source_locators.json"
    rows = read_json(path)
    if change == "missing":
        rows.pop()
    elif change == "duplicate":
        rows.append(rows[-1])
    elif change == "invented_pdf_page":
        rows[-1]["original_page"] = 2
    elif change == "wrong_kind":
        rows[0]["kind"] = "metadata_snippet"
    else:
        rows[-1]["pmid"] = "javascript:alert(1)"
    write_json(path, rows)
    destination = source.parent / "bad-map"
    with pytest.raises(ValueError):
        pipeline.run(source, destination)
    assert not destination.exists()


def test_locator_snapshot_tampering_is_rejected(source):
    dest = source.parent / "prepared"
    pipeline.run(source, dest)
    write_json(dest / "locators.json", [])
    with pytest.raises(ValueError, match="locator snapshot"):
        pipeline.run(source, dest)


def test_frozen_replay_is_offline_and_rejects_changed_dependency_snapshot(source, monkeypatch):
    from res_pipeline.evidence.replay_semantic import replay

    dest = source.parent / "replay"
    pipeline.run(source, dest)
    before = {p.relative_to(dest): p.read_bytes() for p in dest.rglob("*") if p.is_file()}
    monkeypatch.setattr(pipeline, "RunClient", lambda *a, **k: pytest.fail("API initialization"))
    replay(dest)
    after = {p.relative_to(dest): p.read_bytes() for p in dest.rglob("*") if p.is_file()}
    assert after == before and not (dest / "calls").exists()
    (dest / "code_snapshot/source_units.py").write_text("tampered")
    with pytest.raises(ValueError, match="Frozen semantic code"):
        replay(dest)
