"""Attributed synthesis revisions with immutable parents and pending revalidation.

Preparation creates an empty ledger. Application requires actual supplied edit records.
Neither action authenticates human identity, validates scientific claims or trains a model.
"""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import Field

from res_pipeline.evidence.provenance import digest, read_json, write_json
from res_pipeline.evidence.schemas import Record, Synthesis, Theory

INPUTS = (
    "programme_theory.json",
    "findings.json",
    "source_pages.json",
    "corpus_manifest.json",
    "reference_snapshot.json",
    "config.json",
)


def record_hash(value: dict) -> str:
    return digest(json.dumps(value, sort_keys=True, ensure_ascii=False).encode())


def snapshot_code(destination: Path) -> dict:
    hashes = {}
    for name in ("interventions.py", "schemas.py", "provenance.py"):
        raw = (Path(__file__).parent / name).read_bytes()
        target = destination / "code_snapshot" / name
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(raw)
        hashes[name] = digest(raw)
    return hashes


def render_record(record: dict | None, changed: set[str] | None = None) -> str:
    if record is None:
        return "<p>No record in this version.</p>"
    fields = []
    for key, value in record.items():
        label = html.escape(key.replace("_", " ").capitalize())
        if isinstance(value, list):
            text = (
                "<ul>" + "".join(f"<li>{html.escape(str(v))}</li>" for v in value) + "</ul>"
                if value
                else "None recorded"
            )
        else:
            text = html.escape(str(value)) if value is not None else "Not recorded"
        style = ' style="background:#fff0c9"' if key in (changed or set()) else ""
        fields.append(f"<div{style}><dt>{label}</dt><dd>{text}</dd></div>")
    return (
        "<dl>"
        + "".join(fields)
        + "</dl><details><summary>Machine-readable record</summary><pre>"
        + html.escape(json.dumps(record, ensure_ascii=False, indent=2))
        + "</pre></details>"
    )


class Attribution(Record):
    actor: str = Field(min_length=1)
    actor_type: Literal["human", "human_with_ai_assistance", "ai_assistant"]
    recorded_at: datetime
    minutes: float = Field(ge=0, allow_inf_nan=False)
    assistance_disclosure: str = Field(min_length=1)


class TheoryEdit(Record):
    edit_id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]*$")
    action: Literal["replace", "add", "withdraw"]
    theory_id: str = Field(pattern=r"^PT[0-9]{2,}$")
    before_sha256: str | None
    replacement: Theory | None
    reason: str = Field(min_length=1)
    basis_finding_ids: list[str] = Field(min_length=1)
    source_locator_and_note: str = Field(min_length=1)
    attribution: Attribution


class SummaryEdit(Record):
    before_sha256: str
    overview: str = Field(min_length=1)
    unanswered_questions: list[str]
    reason: str = Field(min_length=1)
    attribution: Attribution


class RevisionSubmission(Record):
    parent_input_sha256: dict[str, str]
    edits: list[TheoryEdit]
    summary_edit: SummaryEdit | None


def parent_inputs(source: Path) -> tuple[dict, dict, list[dict]]:
    hashes = {n: digest((source / n).read_bytes()) for n in INPUTS}
    synthesis, findings = read_json(source / INPUTS[0]), read_json(source / INPUTS[1])
    ids = [r["theory_id"] for r in synthesis["theories"]]
    fids = [r["finding_id"] for r in findings]
    if len(ids) != len(set(ids)) or len(fids) != len(set(fids)):
        raise ValueError("Parent has duplicate theory/finding IDs")
    for row in synthesis["theories"]:
        Theory.model_validate({k: row[k] for k in Theory.model_fields})
        if set(row["finding_ids"]) - set(fids):
            raise ValueError("Parent theory links to unknown evidence")
    return hashes, synthesis, findings


def check_attribution(value: Attribution):
    if not value.actor.strip() or not value.assistance_disclosure.strip():
        raise ValueError("Attribution must name an actor and disclose assistance")
    if value.recorded_at.utcoffset() is None:
        raise ValueError("Use an explicit timezone for revision attribution")


def validate_and_revise(
    parent: dict, findings: list[dict], submission: RevisionSubmission
) -> tuple[dict, list[dict]]:
    if not submission.edits and submission.summary_edit is None:
        raise ValueError("Empty ledger is preparation, not an intervention")
    old = {r["theory_id"]: r for r in parent["theories"]}
    allowed = {r["finding_id"] for r in findings}
    records = dict(old)
    events, ids, targets = [], set(), set()
    for edit in submission.edits:
        check_attribution(edit.attribution)
        if not edit.reason.strip() or not edit.source_locator_and_note.strip():
            raise ValueError("Each edit requires a reason and source explanation")
        if edit.edit_id == "SUMMARY" or edit.edit_id in ids or edit.theory_id in targets:
            raise ValueError("Duplicate edit ID or competing edits to one theory")
        ids.add(edit.edit_id)
        targets.add(edit.theory_id)
        if (
            len(edit.basis_finding_ids) != len(set(edit.basis_finding_ids))
            or set(edit.basis_finding_ids) - allowed
        ):
            raise ValueError("Edit cites duplicate or unknown evidence IDs")
        before = old.get(edit.theory_id)
        if edit.action == "add":
            if before is not None or edit.before_sha256 is not None:
                raise ValueError("Addition requires a new ID and no previous record hash")
        elif before is None or edit.before_sha256 != record_hash(before):
            raise ValueError("Stale or unknown theory revision")
        if edit.action == "withdraw":
            if edit.replacement is not None:
                raise ValueError("Withdrawal must not supply a replacement")
            after = None
            del records[edit.theory_id]
        else:
            if edit.replacement is None:
                raise ValueError("Add/replace requires a complete revised theory")
            after = {
                **edit.replacement.model_dump(),
                "theory_id": edit.theory_id,
                "human_approval": None,
            }
            if (
                not after["finding_ids"]
                or len(after["finding_ids"]) != len(set(after["finding_ids"]))
                or set(after["finding_ids"]) - allowed
            ):
                raise ValueError("Revised theory needs unique existing finding IDs")
            if any(
                not after[k].strip()
                for k in ("title", "context", "resource", "response", "outcome", "explanation")
            ):
                raise ValueError("Required theory text cannot be blank")
            if before is not None and all(before[k] == after[k] for k in Theory.model_fields):
                raise ValueError("No-op replacement is not an intervention")
            records[edit.theory_id] = after
        events.append(
            {
                **edit.model_dump(mode="json"),
                "before": before,
                "after": after,
                "after_sha256": record_hash(after) if after is not None else None,
            }
        )
    result = {
        "overview": parent["overview"],
        "theories": list(records.values()),
        "unanswered_questions": parent["unanswered_questions"],
    }
    summary = submission.summary_edit
    if summary:
        check_attribution(summary.attribution)
        before = {k: parent[k] for k in ("overview", "unanswered_questions")}
        if summary.before_sha256 != record_hash(before):
            raise ValueError("Stale synthesis-summary revision")
        after = {"overview": summary.overview, "unanswered_questions": summary.unanswered_questions}
        if before == after or not summary.overview.strip() or not summary.reason.strip():
            raise ValueError("Invalid or no-op synthesis-summary revision")
        result.update(after)
        events.append(
            {
                "edit_id": "SUMMARY",
                **summary.model_dump(mode="json"),
                "before": before,
                "after": after,
                "after_sha256": record_hash(after),
            }
        )
    Synthesis.model_validate(
        {**result, "theories": [{k: r[k] for k in Theory.model_fields} for r in result["theories"]]}
    )
    return result, events


def distinct_sibling(source: Path, destination: Path):
    if source == destination or source.parent != destination.parent:
        raise ValueError("Use a new sibling run, never the frozen parent")
    if destination.exists():
        raise FileExistsError("Revision/preparation destination already exists")


def prepare(source: Path, destination: Path) -> dict:
    source, destination = source.resolve(), destination.resolve()
    distinct_sibling(source, destination)
    hashes, parent, _ = parent_inputs(source)
    destination.mkdir(parents=True)
    code_hashes = snapshot_code(destination)
    write_json(
        destination / "revision_submission.json",
        {"parent_input_sha256": hashes, "edits": [], "summary_edit": None},
    )
    write_json(destination / "submission_schema.json", RevisionSubmission.model_json_schema())
    write_json(destination / "parent_theories.json", parent)
    write_json(
        destination / "record_hashes.json",
        {r["theory_id"]: record_hash(r) for r in parent["theories"]},
    )
    write_json(
        destination / "summary_record_hash.json",
        {"sha256": record_hash({k: parent[k] for k in ("overview", "unanswered_questions")})},
    )
    manifest = {
        "status": "prepared_no_intervention",
        "parent_run": source.name,
        "parent_input_sha256": hashes,
        "theory_count": len(parent["theories"]),
        "recorded_changes": 0,
        "human_validation": "pending",
        "code_sha256": code_hashes,
    }
    write_json(destination / "manifest.json", manifest)
    content = [
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Prepare attributed synthesis revisions</title>',
        "<style>body{font:17px/1.6 system-ui;max-width:1050px;margin:2rem auto;padding:1rem}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f6fa;padding:1rem}details{padding:1rem;border-bottom:1px solid #ccd}dt{font-weight:650;margin-top:.7rem}dd{margin-left:1rem}</style>",
        "<h1>Prepare attributed synthesis revisions</h1><p>No intervention has been applied. The empty ledger is not a human review or an improved result.</p>",
        '<p><a href="revision_submission.json">Empty submission ledger</a> | <a href="submission_schema.json">Required structure</a> | <a href="record_hashes.json">Parent record hashes</a></p>',
        "<p>Each actual edit must state who made it, human/AI assistance, date/time, minutes, reason, source explanation, existing finding IDs and the exact old record hash. Revisions go to a new sibling run and remain pending source support and comparison. Do not fabricate reviewers.</p>",
        "<p>Add/replace supplies a complete theory record. Withdraw preserves the old record in history. Splitting uses one withdrawal and additions with new PT IDs. Changed overview/questions need their own summary edit. Correct source findings in a separate experiment; this ledger does not alter them.</p>",
    ]
    for row in parent["theories"]:
        target = (
            "report.html#" + row["theory_id"]
            if (source / "report.html").exists()
            else "programme_theory.json"
        )
        content.append(
            f'<details id="{html.escape(row["theory_id"])}"><summary>{html.escape(row["theory_id"])}: {html.escape(row["title"])}</summary><p><a href="../{html.escape(source.name)}/{html.escape(target)}">Original run record</a></p>{render_record(row)}</details>'
        )
    (destination / "index.html").write_text("\n".join(content) + "</html>", encoding="utf-8")
    if any(digest((source / n).read_bytes()) != h for n, h in hashes.items()):
        raise ValueError("Parent changed during preparation")
    return manifest


def apply_revision(source: Path, submission_path: Path, destination: Path) -> dict:
    source, destination = source.resolve(), destination.resolve()
    distinct_sibling(source, destination)
    hashes, parent, findings = parent_inputs(source)
    submitted_bytes = submission_path.read_bytes()
    submission = RevisionSubmission.model_validate_json(submitted_bytes)
    if submission.parent_input_sha256 != hashes:
        raise ValueError("Parent/reference/source identities changed; review the new version")
    revised, events = validate_and_revise(parent, findings, submission)
    destination.mkdir(parents=True)
    code_hashes = snapshot_code(destination)
    for name in INPUTS:
        if name not in {"programme_theory.json", "config.json"}:
            (destination / name).write_bytes((source / name).read_bytes())
    (destination / "parent_programme_theory.json").write_bytes(
        (source / "programme_theory.json").read_bytes()
    )
    write_json(destination / "programme_theory.json", revised)
    (destination / "revision_submission.json").write_bytes(submitted_bytes)
    write_json(destination / "revision_events.json", events)
    config = read_json(source / "config.json")
    config["protocol_version"] = "attributed-synthesis-revision-v1"
    config["prior_budget_runs"] = list(
        dict.fromkeys([*config.get("prior_budget_runs", []), source.name])
    )
    write_json(destination / "config.json", config)
    actors = {e["attribution"]["actor_type"] for e in events}
    status = {
        "revision_status": "recorded_pending_revalidation",
        "parent_run": source.name,
        "parent_input_sha256": hashes,
        "submission_sha256": digest(submitted_bytes),
        "revised_theory_sha256": digest((destination / "programme_theory.json").read_bytes()),
        "reference_sha256": hashes["reference_snapshot.json"],
        "code_sha256": code_hashes,
        "edit_count": len(events),
        "claimed_actor_types": sorted(actors),
        "declared_minutes": sum(e["attribution"]["minutes"] for e in events),
        "human_identity_authentication": "not established by recorded names",
        "human_validation": "pending",
        "source_support_revalidation": "pending",
        "comparison": "not executed",
        "training": "none; neither RLHF nor fine-tuning",
        "intervention_effect": None,
        "summary_review": "revised_pending_review"
        if submission.summary_edit
        else "inherited_summary_requires_review_after_theory_changes",
    }
    write_json(destination / "run_status.json", status)
    safe = html.escape
    rows = []
    for event in events:
        before, after = event["before"] or {}, event["after"] or {}
        changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
        rows.append(
            f'<section><h2>{safe(event["edit_id"])}</h2><p>{safe(event["reason"])}</p><p>Declared actor: {safe(event["attribution"]["actor"])} ({safe(event["attribution"]["actor_type"])})</p><p>Changed fields: {safe(", ".join(sorted(changed)))}.</p><div class="pair"><div><h3>Before</h3>{render_record(event["before"], changed)}</div><div><h3>After</h3>{render_record(event["after"], changed)}</div></div></section>'
        )
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Attributed synthesis revision</title><style>body{font:16px/1.5 system-ui;max-width:1450px;margin:2rem auto;padding:1rem}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}dt{font-weight:650;margin-top:.7rem}dd{margin-left:1rem}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f8;padding:1rem}@media(max-width:850px){.pair{grid-template-columns:1fr}}</style><h1>Attributed synthesis revision</h1><p>Changes are recorded, not independently validated. This report does not show that the revision improved scientific quality. The original source and reference are fixed; new source review and comparison remain pending.</p>'
        + "".join(rows)
        + "</html>"
    )
    (destination / "index.html").write_text(page, encoding="utf-8")
    if any(digest((source / n).read_bytes()) != h for n, h in hashes.items()):
        status["revision_status"] = "invalid_parent_changed_during_application"
        write_json(destination / "run_status.json", status)
        raise ValueError("Parent changed during revision; do not use these outputs")
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--submission", type=Path)
    args = parser.parse_args()
    result = (
        apply_revision(args.source_run, args.submission, args.output_dir)
        if args.submission
        else prepare(args.source_run, args.output_dir)
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
