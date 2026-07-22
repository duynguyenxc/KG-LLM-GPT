"""Initial Programme Theory (IPT) manager — the theory-first "seed" (Gap 1).

In a realist review the IPT is authored BEFORE the main analysis and STEERS
extraction and synthesis; the corpus then confirms, refines, or rejects it
(Richmond §2, L171-203; the professor's "seed → iterative modifier → human exam").

This module loads the versioned seed (``config/initial_programme_theory.yaml``),
renders it as a compact prompt block that is injected into the extractor and the
programme-theory composer, and records ratification + refinement in Postgres so the
theory's evolution is auditable.

CONTAMINATION BOUNDARY: the IPT contains only public pre-existing theory and
hypotheses — never the benchmark's answers. It is loaded here; the gold standard is
never read by this module.
"""

from __future__ import annotations

import json

from res_pipeline.core.config import load_yaml_config
from res_pipeline.core.db import get_connection, log_audit_event


def load_ipt() -> dict:
    return load_yaml_config("initial_programme_theory")


def ipt_prompt_block() -> str:
    """Render the IPT as the theory-being-tested block for extractor/composer prompts.

    If the theory has been refined by earlier retroduction rounds, the most recent
    refinement note is appended so downstream re-reads see the *evolving* theory.
    """
    ipt = load_ipt()
    dims = "; ".join(
        f"{d['id']} (from {d['from_theory']}: {d['to_test']})"
        for d in ipt.get("hypothesised_context_dimensions", [])
    )
    levels = ", ".join(lv["level"] for lv in ipt.get("context_levels_to_investigate", []))
    resources = "; ".join(ipt.get("hypothesised_mechanism_resources", []))
    block = (
        "CURRENT PROGRAMME THEORY (the theory you are TESTING and REFINING — "
        "hypotheses from public learning-science, NOT settled answers):\n"
        f"- Realist skeleton: {ipt['cmo_skeleton'].strip()}\n"
        f"- Investigate contexts at these levels: {levels}.\n"
        f"- Candidate context dimensions to confirm/refine/reject: {dims}.\n"
        f"- Candidate mechanism-resources to look for: {resources}.\n"
    )
    note = latest_refinement_notes()
    if note:
        block += f"- THEORY REFINEMENT so far (from evidence already read): {note}\n"
    block += (
        "Use this theory to guide WHERE you look, but let the paper speak: extract every "
        "configuration THIS paper evidences — typically 2-5, including secondary and "
        "negative/backfiring pathways — confirming, extending, or contradicting the theory "
        "as the evidence dictates. Do not omit a well-evidenced configuration merely because "
        "it is absent from the hypotheses, and never invent one the text cannot support."
    )
    return block


def latest_refinement_notes() -> str:
    """The most recent retroduction refinement summary, if any."""
    with get_connection() as conn:
        _ensure_table(conn)
        row = conn.execute(
            "SELECT refinement_note FROM ipt_versions WHERE refinement_note IS NOT NULL "
            "ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
    return row["refinement_note"] if row and row["refinement_note"] else ""


def record_refinement(confirmed: list[str], refined: list[str], rejected: list[str],
                      summary: str, run_id: str) -> str:
    """Append a refined IPT version (the retroduction 'modifier'); returns new version."""
    ipt = load_ipt()
    with get_connection() as conn:
        _ensure_table(conn)
        n = conn.execute("SELECT count(*) AS c FROM ipt_versions").fetchone()["c"]
        new_version = f"{ipt['version'].split('-')[0]}-refined-r{n}"
        note = (f"CONFIRMED: {'; '.join(confirmed) or '—'}. "
                f"REFINED: {'; '.join(refined) or '—'}. "
                f"REJECTED: {'; '.join(rejected) or '—'}. {summary}")
        payload = {**ipt, "version": new_version,
                   "refinement_log": [*ipt.get("refinement_log", []),
                                      {"confirmed": confirmed, "refined": refined,
                                       "rejected": rejected, "summary": summary}]}
        conn.execute(
            "INSERT INTO ipt_versions (version, ipt_json, status, refinement_note, run_id) "
            "VALUES (%s,%s,'draft',%s,%s)",
            (new_version, json.dumps(payload), note, run_id),
        )
    log_audit_event(run_id, "ipt_manager", "ipt_refined",
                    detail={"version": new_version, "confirmed": len(confirmed),
                            "refined": len(refined), "rejected": len(rejected)})
    return new_version


def _ensure_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ipt_versions (
            id BIGSERIAL PRIMARY KEY,
            version TEXT NOT NULL,
            ipt_json JSONB NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',   -- draft | ratified | superseded
            ratified_by TEXT,
            refinement_note TEXT,
            run_id TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )


def register_seed(run_id: str) -> str:
    """Insert the seed IPT as a draft version if not already present. Returns version."""
    ipt = load_ipt()
    version = ipt["version"]
    with get_connection() as conn:
        _ensure_table(conn)
        exists = conn.execute(
            "SELECT 1 FROM ipt_versions WHERE version=%s", (version,)
        ).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO ipt_versions (version, ipt_json, status, run_id) "
                "VALUES (%s,%s,'draft',%s)",
                (version, json.dumps(ipt), run_id),
            )
    log_audit_event(run_id, "ipt_manager", "ipt_seed_registered", detail={"version": version})
    return version


def ratify(version: str, ratifier: str, run_id: str) -> None:
    """HITL-0: a human ratifies the IPT before it drives a production run."""
    with get_connection() as conn:
        _ensure_table(conn)
        conn.execute(
            "UPDATE ipt_versions SET status='ratified', ratified_by=%s WHERE version=%s",
            (ratifier, version),
        )
        conn.execute(
            "INSERT INTO hitl_feedback (checkpoint, subject_ref, action, feedback, payload, "
            "run_id) VALUES ('HITL-0',%s,'approve',%s,'{}',%s)",
            (f"ipt-{version}", f"Ratified by {ratifier}", run_id),
        )
    log_audit_event(run_id, f"human:{ratifier}", "hitl0_ipt_ratified",
                    subject_ref=f"ipt-{version}")


def current_status() -> dict:
    """The latest IPT version and whether it has been ratified (for gating/reporting)."""
    with get_connection() as conn:
        _ensure_table(conn)
        row = conn.execute(
            "SELECT version, status, ratified_by FROM ipt_versions "
            "ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
    return dict(row) if row else {"version": None, "status": "absent", "ratified_by": None}
