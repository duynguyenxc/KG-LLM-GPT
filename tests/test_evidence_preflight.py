import json

import pytest

from res_pipeline.evidence.preflight import CachedOnlyClient, CacheMiss
from res_pipeline.evidence.provenance import digest, request_payload, write_json
from res_pipeline.evidence.schemas import Extraction


def test_offline_cache_never_creates_requests_or_falls_back_to_network(tmp_path):
    config = {"reasoning_effort": "medium", "max_completion_tokens": 100}
    client = CachedOnlyClient(tmp_path, config)
    with pytest.raises(CacheMiss):
        client.call("extract_S001", "fixture", "instructions", "source", Extraction)
    assert not list(tmp_path.iterdir())
    assert not hasattr(client, "client")


def test_preflight_rejects_tampered_parsed_response_and_changed_input(tmp_path):
    config = {"reasoning_effort": "medium", "max_completion_tokens": 100}
    client = CachedOnlyClient(tmp_path, config)
    request = request_payload("fixture", "instructions", "source", Extraction, config)
    value = dict(
        design="fixture",
        population="fixture",
        sample_description="fixture",
        source_limitations=[],
        findings=[],
    )
    call = tmp_path / "calls/extract_S001"
    write_json(call / "request.json", request)
    write_json(
        call / "identity.json",
        {"request_sha256": digest(json.dumps(request, sort_keys=True).encode())},
    )
    write_json(
        call / "response.json",
        {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(value)}}]},
    )
    write_json(call / "parsed.json", value)
    assert (
        client.call("extract_S001", "fixture", "instructions", "source", Extraction).design
        == "fixture"
    )
    with pytest.raises(ValueError, match="identity changed"):
        client.call("extract_S001", "fixture", "instructions", "changed source", Extraction)
    write_json(call / "parsed.json", {**value, "population": "edited after generation"})
    with pytest.raises(ValueError, match="differs from the recorded"):
        client.call("extract_S001", "fixture", "instructions", "source", Extraction)


def test_synthesis_packet_excludes_local_paths_and_evaluation_metadata():
    from res_pipeline.evidence.pipeline import production_evidence

    fields = [
        "finding_id",
        "paper_id",
        "study_family_id",
        "availability",
        "context",
        "resource",
        "response",
        "outcome",
        "direction",
        "comparator",
        "timepoint",
        "response_status",
        "outcome_status",
        "explanation",
        "limitations",
        "evidence",
    ]
    finding = {key: "scientific fixture" for key in fields}
    finding.update(
        source_path="data/20-paper-of-Richmond/example.pdf",
        human_verdict="secret verdict",
        benchmark_match="RC01",
        critic={"rationale": "review-only metadata"},
    )
    value = production_evidence(finding)
    assert set(value) == set(fields)
    assert "Richmond" not in json.dumps(value)
    assert value["context"] == finding["context"]
    assert value["evidence"] == finding["evidence"]
