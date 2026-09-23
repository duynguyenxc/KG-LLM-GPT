"""Resume a semantic run through its verified frozen code, offline by default."""

import argparse
import json
import runpy
import sys
from pathlib import Path

from res_pipeline.evidence.provenance import digest, read_json


def replay(directory: Path, *, execute: bool = False) -> None:
    directory = directory.resolve()
    manifest = read_json(directory / "manifest.json")
    config = read_json(directory / "config.json")
    source_name = manifest["source_run"]
    if Path(source_name).name != source_name or source_name in {".", ".."}:
        raise ValueError("Invalid source-run identity")
    codes = manifest["code_sha256"]
    if not isinstance(codes, dict) or "semantic_pipeline.py" not in codes:
        raise ValueError("Not a semantic code snapshot")
    for name, expected in codes.items():
        if Path(name).name != name:
            raise ValueError("Invalid snapshot filename")
        if digest((directory / "code_snapshot" / name).read_bytes()) != expected:
            raise ValueError("Frozen semantic code changed")
        # The frozen entry point imports these dependencies from the active package.
        if (
            name != "semantic_pipeline.py"
            and digest((Path(__file__).parent / name).read_bytes()) != expected
        ):
            raise ValueError(
                "Active dependency differs from frozen version; use an isolated matching checkout"
            )
    if digest(json.dumps(config, sort_keys=True).encode()) != manifest["config_sha256"]:
        raise ValueError("Frozen semantic configuration changed")
    argv = [
        str(directory / "code_snapshot/semantic_pipeline.py"),
        "--source-run",
        str(directory.parent / source_name),
        "--output-dir",
        str(directory),
        "--papers",
        *manifest["selected_papers"],
    ]
    for name in config.get("prior_budget_runs", []):
        argv += ["--budget-run", name]
    if execute:
        argv.append("--execute")
    previous = sys.argv
    try:
        sys.argv = argv
        runpy.run_path(argv[0], run_name="__main__")
    finally:
        sys.argv = previous


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    replay(args.run_dir, execute=args.execute)


if __name__ == "__main__":
    main()
