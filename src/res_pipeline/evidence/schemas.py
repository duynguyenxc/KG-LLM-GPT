"""Explicit separation of source observations, explanatory inferences and review decisions."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(Record):
    role: Literal["context", "resource", "response", "outcome", "limitation"]
    page: int = Field(ge=1)
    quote: str = Field(min_length=10)


class Finding(Record):
    context: str
    resource: str
    response: str
    outcome: str
    direction: Literal["positive", "negative", "null", "mixed", "unmeasured"]
    comparator: str
    timepoint: str
    response_status: Literal["reported", "author_inference", "model_hypothesis", "not_reported"]
    outcome_status: Literal["measured", "reported_perception", "author_inference", "not_reported"]
    explanation: str
    limitations: list[str]
    evidence: list[Evidence]


class Extraction(Record):
    design: str
    population: str
    sample_description: str
    source_limitations: list[str]
    findings: list[Finding]


class FindingReview(Record):
    finding_index: int = Field(ge=0)
    verdict: Literal["supported", "partial", "unsupported", "uncertain"]
    response_evidence: Literal["reported", "author_inference", "model_hypothesis", "not_reported"]
    outcome_evidence: Literal["measured", "reported_perception", "author_inference", "not_reported"]
    rationale: str
    problems: list[str]


class ExtractionReview(Record):
    assessments: list[FindingReview]
    missed_evidence: list[str]


class QuoteReplacement(Record):
    finding_index: int
    evidence_index: int
    replacements: list[Evidence]
    explanation: str


class QuoteRepairs(Record):
    repairs: list[QuoteReplacement]


class LineSpan(Record):
    page: int = Field(ge=1)
    first_line: int = Field(ge=1)
    last_line: int = Field(ge=1)


class CitationSpanRepair(Record):
    citation_id: str
    spans: list[LineSpan]
    explanation: str


class CitationSpanRepairs(Record):
    repairs: list[CitationSpanRepair]


class Theory(Record):
    title: str
    context: str
    resource: str
    response: str
    outcome: str
    direction: Literal["positive", "negative", "null", "mixed", "unmeasured"]
    finding_ids: list[str]
    explanation: str
    rival_explanations: list[str]
    limitations: list[str]
    evidence_gaps: list[str]


class Synthesis(Record):
    overview: str
    theories: list[Theory]
    unanswered_questions: list[str]


class Dimension(Record):
    dimension: Literal["context", "resource", "response", "outcome", "direction", "qualifiers"]
    match: Literal["equivalent", "partial", "different", "absent", "uncertain"]
    reason: str


class Comparison(Record):
    theory_ids: list[str]
    finding_ids: list[str]
    verdict: Literal["equivalent", "partial", "contradictory", "not_recovered", "uncertain"]
    dimensions: list[Dimension]
    rationale: str
    critical_difference: str
    review_question: str
