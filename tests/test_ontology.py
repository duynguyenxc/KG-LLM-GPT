"""Ontology integrity tests.

The domain/range constraint map in ``config/ontology.yaml`` must admit every one of
the 40 gold-standard relations derived from Richmond et al. (2020). If a constraint
change breaks this, the ontology no longer describes the benchmark it is verified
against — fail loudly.
"""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load():
    cfg = yaml.safe_load((ROOT / "config" / "ontology.yaml").read_text(encoding="utf-8"))
    gold = json.loads((ROOT / "gold" / "richmond_gold.json").read_text(encoding="utf-8"))
    return cfg, gold


def test_gold_relations_satisfy_domain_range():
    cfg, gold = _load()
    categories = {code: spec["category"] for code, spec in gold["entities"].items()}
    constraints = {
        name: (set(spec["domain"]), set(spec["range"]))
        for name, spec in cfg["relation_predicates"].items()
    }
    violations = []
    for rel in gold["relationships"]:
        subject_type = categories[rel["subject_code"]]
        object_type = categories[rel["object_code"]]
        domain, range_ = constraints[rel["predicate"]]
        if subject_type not in domain or object_type not in range_:
            violations.append((rel["id"], rel["predicate"], subject_type, object_type))
    assert not violations, f"Gold relations violate ontology constraints: {violations}"


def test_all_gold_predicates_are_defined():
    cfg, gold = _load()
    defined = set(cfg["relation_predicates"])
    used = {rel["predicate"] for rel in gold["relationships"]}
    assert used <= defined, f"Gold uses undefined predicates: {used - defined}"


def test_entity_types_match_gold_categories():
    cfg, gold = _load()
    defined = set(cfg["entity_types"])
    used = {spec["category"] for spec in gold["entities"].values()}
    assert used <= defined, f"Gold uses undefined entity categories: {used - defined}"


def test_pydantic_models_enforce_constraints():
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from res_pipeline.plugins.realist.ontology import (
        EntityInstance,
        EntityType,
        Predicate,
        Provenance,
        TypedRelation,
    )

    prov = Provenance(
        study_id="S001",
        text_unit_id="S001-tu-0001",
        char_start=10,
        char_end=42,
        verbatim_quote="students felt panic",
        extractor_model="test",
        prompt_version="v0",
        confidence=0.9,
    )
    context = EntityInstance(
        entity_id="e1", entity_type=EntityType.CONTEXT, label="low knowledge", provenance=prov
    )
    resource = EntityInstance(
        entity_id="e2",
        entity_type=EntityType.MECHANISM_RESOURCE,
        label="explicit expert explanation",
        provenance=prov,
    )
    # Valid: Context ENABLES Mechanism_Response
    response = EntityInstance(
        entity_id="e3",
        entity_type=EntityType.MECHANISM_RESPONSE,
        label="understanding",
        provenance=prov,
    )
    TypedRelation(
        relation_id="r1",
        predicate=Predicate.ENABLES,
        subject=context,
        object=response,
        provenance=prov,
    )
    # Invalid: Context PROVIDES Mechanism_Resource (domain violation) must raise
    import pytest

    with pytest.raises(ValueError):
        TypedRelation(
            relation_id="r2",
            predicate=Predicate.PROVIDES,
            subject=context,
            object=resource,
            provenance=prov,
        )
