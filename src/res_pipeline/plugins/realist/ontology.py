"""Typed realist ontology: entity types, relation predicates, and validated triples.

This module is the scientific core of the pipeline. It loads the ontology definition
from ``config/ontology.yaml`` and exposes Pydantic models that make it impossible to
construct an untyped or constraint-violating knowledge-graph statement:

* every entity instance carries one of the five fixed realist types;
* every relation carries one of the five fixed predicates, validated against the
  predicate's domain/range constraints (ontology-guided extraction pattern — see
  docs/research/SOTA_REPORT.md Q1/Q3);
* every statement carries full span-level provenance (nanopublication-style
  separation of assertion vs provenance), as RAMESES II transparency requires.

Candidates that do not fit any predicate are preserved as ``UNTYPED_CANDIDATE``
rather than silently dropped, and surfaced for human review at HITL-2.
"""

from __future__ import annotations

import enum
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator

_CONFIG_PATH = Path(__file__).resolve().parents[4] / "config" / "ontology.yaml"


class EntityType(str, enum.Enum):
    """The five fixed realist entity types (RAMESES II: label C/M/O explicitly)."""

    CONTEXT = "Context"
    INTERVENTION = "Intervention"
    MECHANISM_RESOURCE = "Mechanism_Resource"
    MECHANISM_RESPONSE = "Mechanism_Response"
    OUTCOME = "Outcome"


class Predicate(str, enum.Enum):
    """The five fixed, directed relation predicates (professor requirement, 2026-05-28)."""

    PROVIDES = "PROVIDES"
    TRIGGERS = "TRIGGERS"
    ENABLES = "ENABLES"
    LEADS_TO = "LEADS_TO"
    CONSTRAINS = "CONSTRAINS"
    UNTYPED_CANDIDATE = "UNTYPED_CANDIDATE"


@lru_cache(maxsize=1)
def load_ontology_config() -> dict:
    with _CONFIG_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@lru_cache(maxsize=1)
def domain_range_map() -> dict[Predicate, tuple[frozenset[EntityType], frozenset[EntityType]]]:
    """Predicate -> (allowed subject types, allowed object types), from ontology.yaml."""
    cfg = load_ontology_config()
    mapping: dict[Predicate, tuple[frozenset[EntityType], frozenset[EntityType]]] = {}
    for name, spec in cfg["relation_predicates"].items():
        mapping[Predicate(name)] = (
            frozenset(EntityType(t) for t in spec["domain"]),
            frozenset(EntityType(t) for t in spec["range"]),
        )
    return mapping


class Provenance(BaseModel):
    """Span-level provenance attached to every extracted statement."""

    study_id: str = Field(pattern=r"^S\d{3}$", description="Registry ID, e.g. S007")
    text_unit_id: str
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)
    verbatim_quote: str = Field(min_length=1)
    extractor_model: str
    prompt_version: str
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _span_is_ordered(self) -> "Provenance":
        if self.char_end <= self.char_start:
            raise ValueError("char_end must be greater than char_start")
        return self


class EntityInstance(BaseModel):
    """An emergent entity instance carrying one fixed realist type.

    Labels are free text from the literature (emergent); ``canonical_id`` is filled
    by the Normalization Agent when instances are merged. Mapping to Richmond
    E-codes happens only in the verification layer, never here.
    """

    entity_id: str
    entity_type: EntityType
    label: str = Field(min_length=1)
    description: str = ""
    canonical_id: str | None = None
    provenance: Provenance


class TypedRelation(BaseModel):
    """A directed, typed statement validated against domain/range constraints."""

    relation_id: str
    predicate: Predicate
    subject: EntityInstance
    object: EntityInstance
    provenance: Provenance

    @model_validator(mode="after")
    def _enforce_domain_range(self) -> "TypedRelation":
        if self.predicate is Predicate.UNTYPED_CANDIDATE:
            return self  # preserved for HITL-2 review, exempt from constraints
        domain, range_ = domain_range_map()[self.predicate]
        if self.subject.entity_type not in domain:
            raise ValueError(
                f"{self.predicate.value}: subject type {self.subject.entity_type.value} "
                f"violates domain {sorted(t.value for t in domain)}"
            )
        if self.object.entity_type not in range_:
            raise ValueError(
                f"{self.predicate.value}: object type {self.object.entity_type.value} "
                f"violates range {sorted(t.value for t in range_)}"
            )
        return self


class CMOC(BaseModel):
    """One Context-Mechanism-Outcome Configuration within a single study.

    The analytic unit of realist synthesis (RAMESES II). Bundles entity instances
    and the typed relations connecting them; ``polarity`` records whether the
    configuration describes a positive or negative outcome pathway.
    """

    cmoc_id: str
    study_id: str = Field(pattern=r"^S\d{3}$")
    contexts: list[EntityInstance] = Field(default_factory=list)
    interventions: list[EntityInstance] = Field(default_factory=list)
    mechanism_resources: list[EntityInstance] = Field(default_factory=list)
    mechanism_responses: list[EntityInstance] = Field(default_factory=list)
    outcomes: list[EntityInstance] = Field(default_factory=list)
    relations: list[TypedRelation] = Field(default_factory=list)
    polarity: str = Field(pattern=r"^(positive|negative|mixed)$")
    narrative_statement: str = ""

    @model_validator(mode="after")
    def _minimally_complete(self) -> "CMOC":
        if not (self.contexts and self.outcomes):
            raise ValueError("A CMOC requires at least one Context and one Outcome")
        if not (self.mechanism_resources or self.mechanism_responses):
            raise ValueError("A CMOC requires at least one Mechanism (resource or response)")
        return self
