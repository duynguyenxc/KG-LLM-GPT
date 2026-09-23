# Realist evidence synthesis: project continuity

Read `AGENTS.md` and `docs/research/RESEARCH_AUDIT_STATUS.md` before substantive work. The active workspace is `D:/KG-LLM/KG-LLM-GPT`. Earlier paths and July implementation/performance summaries are historical.

This is a methodological research project led by Wei Zheng for an accepted RRE proposal. Richmond et al. (2020), DOI 10.1111/medu.14137, is a worked example and external human synthesis. The central task is to produce inspectable conditional explanations with source evidence and a defensible human-comparison protocol. A software demonstration or a high label-overlap percentage is insufficient.

## Standing requirements

- Write all project artifacts, code and identifiers in English. Communicate with Duy in Vietnamese.
- Ground scientific and architectural decisions in primary sources and the professor's actual instructions. Generated briefing documents and historical AI summaries may contain errors.
- Distinguish proposed, implemented, executed and independently validated behavior. Never relabel AI review as human review, quote location as entailment, or type matching as causal reconstruction.
- Preserve previous submissions and identifiable runs. Do not silently rewrite delivered preliminary results.
- Keep private source PDFs, meeting records and credentials out of public Git history.
- Keep Richmond's reference conclusions out of production extraction/synthesis inputs. Evaluation runs after the system theory is frozen.
- Maintain project continuity and append a WALKTHROUGH entry for each work session, with completed work, limitations and the next step.

## Current source map

- `documents/abstract-from-professor/abstract.md`: accepted proposal and intended methodology.
- `transcript-meetings/`: five meetings, including July 24; use actual statements rather than unchecked speaker labels.
- `data/paper-Richmond-original.pdf`: authoritative published comparison source.
- `data/20-paper-of-Richmond/` and `data/studies_metadata.jsonl`: 28 paper records; 19 apparently full PDFs, one one-page PDF, eight short snippets.
- `docs/research/RICHMOND_OFFICIAL_FINDINGS.md`: published conclusions with exact page/figure anchors.
- `docs/research/METHOD_AND_VERIFICATION_PROTOCOL.md`: algorithm, architecture decisions, evidence and verification definitions.
- `docs/research/OUTPUT_INVENTORY_AND_CORRECTIONS.md`: actual historical outputs and unsupported preliminary claims.
- `gold/richmond_reference_v1.json`: AI-assisted 18-branch operationalization awaiting human ratification; not a machine-readable gold supplied by Richmond.
- `src/res_pipeline/evidence/`: isolated evidence-preserving experiment; legacy modules remain available for historical reproduction.

## Status

The September 23 continuation verified restored API access and completed all 28 available-source extractions/audits (180 findings, 174 machine-eligible). The fixed-corpus run is `outputs/runs/evidence-20260910-full/`. Read `docs/research/CURRENT_RUN_RESULTS.md` for the latest synthesis/comparison checkpoint before launching anything. The September 10 credit interruption is historical; do not repeat it as the current blocker. Actual legacy entities/relations and new findings are exposed in versioned inspection packages. The owner has no two independent reviewers yet and requested preparation of review materials first. Human validation remains pending unless attributable coder and adjudication records establish otherwise. The 47-concept/40-relation evaluation remains required alongside the 18-branch comparison; a completed baseline does not establish the full proposed architecture.
