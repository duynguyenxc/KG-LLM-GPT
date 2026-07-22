"""Unit tests for pure pipeline logic (no API / no DB required)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def test_screening_combine_is_recall_first():
    from res_pipeline.core.screening import ScreeningVote, _combine

    def vote(d):
        return ScreeningVote(decision=d, rationale="x" * 25, confidence=0.9)

    # Any include -> include (union-of-includes).
    assert _combine(vote("include"), vote("uncertain")) == "include"
    assert _combine(vote("exclude"), vote("include")) == "include"
    # Both exclude -> exclude.
    assert _combine(vote("exclude"), vote("exclude")) == "exclude"
    # Otherwise uncertain (routed to HITL-1).
    assert _combine(vote("uncertain"), vote("exclude")) == "uncertain"
    assert _combine(vote("uncertain"), vote("uncertain")) == "uncertain"


def test_span_normalization_dehyphenates_and_maps_offsets():
    from res_pipeline.plugins.realist.span_repair import _normalize_quote, _normalize_with_map

    text = "The diag-\nnostic accuracy improved   significantly across the cohort."
    norm, index_map = _normalize_with_map(text)
    assert "diagnostic accuracy improved significantly" in norm
    assert len(norm) == len(index_map)  # every normalized char maps back
    # Offsets are monotonically non-decreasing into the original text.
    assert all(index_map[i] <= index_map[i + 1] for i in range(len(index_map) - 1))

    quote = "diagnostic accuracy improved significantly"
    pos = norm.find(_normalize_quote(quote))
    assert pos != -1
    original_start = index_map[pos]
    assert text[original_start:original_start + 4].lower() == "diag"


def test_relation_demotion_preserves_untyped_candidate():
    from res_pipeline.plugins.realist.ontology import (
        EntityInstance,
        EntityType,
        Predicate,
        Provenance,
        TypedRelation,
    )

    prov = Provenance(
        study_id="S001", text_unit_id="S001-tu-0001", char_start=0, char_end=10,
        verbatim_quote="evidence", extractor_model="t", prompt_version="v", confidence=0.8,
    )
    outcome = EntityInstance(entity_id="a", entity_type=EntityType.OUTCOME,
                             label="accuracy", provenance=prov)
    context = EntityInstance(entity_id="b", entity_type=EntityType.CONTEXT,
                             label="novice", provenance=prov)
    # Outcome PROVIDES Context is nonsense under the ontology, but as UNTYPED_CANDIDATE
    # it must be preservable (surfaced for HITL-2, never silently dropped).
    rel = TypedRelation(relation_id="r", predicate=Predicate.UNTYPED_CANDIDATE,
                        subject=outcome, object=context, provenance=prov)
    assert rel.predicate is Predicate.UNTYPED_CANDIDATE
