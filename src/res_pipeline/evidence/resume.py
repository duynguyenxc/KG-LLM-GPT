"""Explicitly archive unresolved requests before a user-authorized resumed attempt."""

from pathlib import Path

from res_pipeline.evidence.provenance import write_json


def prepare_resume(directory: Path) -> list[str]:
    """Never discard raw responses or clear uncertain budget reservations."""
    directory = directory.resolve()
    pending = [
        path
        for path in sorted((directory / "calls").iterdir())
        if (path / "request.json").exists() and not (path / "parsed.json").exists()
    ]
    if any((path / "response.json").exists() for path in pending):
        raise RuntimeError(
            "An unfinished call has a raw response; inspect/validate it before retrying"
        )
    history = directory / "calls_archive"
    number = 1
    while (history / f"attempt-{number:03d}").exists():
        number += 1
    archive = history / f"attempt-{number:03d}"
    for source in pending:
        target = archive / source.name
        if not source.resolve().is_relative_to(directory) or not target.resolve().is_relative_to(
            directory
        ):
            raise ValueError("Resume path escapes the run directory")
        archive.mkdir(parents=True, exist_ok=True)
        source.rename(target)
    if pending:
        write_json(
            archive / "resume_note.json",
            {
                "archived_calls": [path.name for path in pending],
                "reason": "Explicit retry of unfinished requests after inspecting interruption",
                "budget_policy": "Prior unresolved reservations retained; no assumption of zero billing",
            },
        )
    return [path.name for path in pending]
