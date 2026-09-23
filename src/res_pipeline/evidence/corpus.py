"""Freeze an offline source supplement; never change an existing research run."""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8"))


def local_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Source path escapes the project root")
    return path


def validate_pages(papers: list[dict], pages: list[dict]) -> None:
    ids = [p["paper_id"] for p in papers]
    if not ids or len(ids) != len(set(ids)) or any(not re.fullmatch(r"S\d{3}", p) for p in ids):
        raise ValueError("Invalid or duplicate paper IDs")
    if set(p["paper_id"] for p in pages) - set(ids):
        raise ValueError("Unknown paper in source pages")
    for paper in papers:
        rows = [p for p in pages if p["paper_id"] == paper["paper_id"]]
        if sorted(p["page"] for p in rows) != list(range(1, paper["pages"] + 1)):
            raise ValueError("Missing or duplicate source pages")
        if any(not isinstance(p["text"], str) for p in rows):
            raise ValueError("Source text must be a string")
        if sum(len(p["text"]) for p in rows) != paper["text_characters"]:
            raise ValueError("Source text length mismatch")


def prepare(root: Path, baseline: Path, acquisition: Path, destination: Path) -> dict:
    """Use XML-matched abstracts, not assistant notes, to build a new source snapshot."""
    root, baseline, acquisition, destination = (
        p.resolve() for p in (root, baseline, acquisition, destination)
    )
    if not all(p.is_relative_to(root) for p in (baseline, acquisition, destination)):
        raise ValueError("Inputs and destination must remain in the project")
    if destination.exists() or destination.parent != baseline.parent:
        raise ValueError("Choose a new sibling destination; overwriting is forbidden")
    report = read(acquisition)
    if any(Path(name).name != name for name in report["baseline_hashes_after"]):
        raise ValueError("Invalid baseline identity filename")
    before = {name: checksum(baseline / name) for name in report["baseline_hashes_after"]}
    required = {"corpus_manifest.json", "source_pages.json", "config.json"}
    if not required <= before.keys() or before != report["baseline_hashes_after"]:
        raise ValueError("Baseline differs from the acquisition checkpoint")
    manifest = read(baseline / "corpus_manifest.json")
    papers = copy.deepcopy(manifest["papers"])
    pages = read(baseline / "source_pages.json")
    validate_pages(papers, pages)
    original = {p["paper_id"]: copy.deepcopy(p) for p in papers}
    raw = local_path(root, report["acquisition"]["raw_path"])
    if checksum(raw) != report["acquisition"]["raw_sha256"]:
        raise ValueError("Raw PubMed response hash mismatch")
    xml = ET.parse(raw).getroot()
    articles = xml.findall("PubmedArticle")
    by_pmid = {a.findtext("./MedlineCitation/PMID"): a for a in articles}
    if len(by_pmid) != len(articles):
        raise ValueError("Duplicate PMID in raw response")
    supplements, input_hashes = {}, {str(raw.relative_to(root)): checksum(raw)}
    entries = report["records"]
    ids = [e["paper_id"] for e in entries]
    pmids = [e["pmid"] for e in entries]
    if len(ids) != len(set(ids)) or len(pmids) != len(set(pmids)) or not ids:
        raise ValueError("Duplicate or empty supplement selection")
    if set(pmids) != set(by_pmid):
        raise ValueError("Supplement population differs from raw response")
    for entry in entries:
        pid = entry["paper_id"]
        if pid not in original or original[pid]["availability"] not in {
            "metadata_snippet_only",
            "partial_pdf",
        }:
            raise ValueError("Supplement must identify an incomplete baseline source")
        path = local_path(root, entry["source_record_path"])
        if checksum(path) != entry["source_record_sha256"]:
            raise ValueError("Parsed source record hash mismatch")
        record = read(path)
        if record["paper_id"] != pid or record["pmid"] != entry["pmid"]:
            raise ValueError("Parsed identity mismatch")
        if (
            record["source_batch_sha256"] != checksum(raw)
            or record["availability"] != "abstract_only"
        ):
            raise ValueError("Incorrect source provenance or availability")
        a = by_pmid[entry["pmid"]]
        article = a.find("./MedlineCitation/Article")
        title = "".join(article.find("ArticleTitle").itertext())
        sections = [
            {"label": n.get("Label"), "text": "".join(n.itertext())}
            for n in article.findall("./Abstract/AbstractText")
        ]
        if not sections or any(not s["text"].strip() for s in sections):
            raise ValueError("Empty source abstract")
        if record["title"] != title or record["abstract_sections"] != sections:
            raise ValueError("Parsed abstract differs from primary XML")
        dois = [
            n.text.lower()
            for n in a.findall("./PubmedData/ArticleIdList/ArticleId")
            if n.get("IdType") == "doi"
        ]
        expected = original[pid]["doi"].lower()
        if record["doi_expected"].lower() != expected or entry["doi"].lower() != expected:
            raise ValueError("Expected DOI differs from baseline")
        if dois and expected not in dois:
            raise ValueError("Primary DOI mismatch")
        if not dois:
            normalize = lambda value: re.sub(r"\W+", "", value.lower())
            if normalize(title) != normalize(original[pid]["title"]):
                raise ValueError("Missing DOI requires matching normalized title")
        text = "PUBMED ABSTRACT — NOT ARTICLE FULL TEXT\n" + "\n\n".join(
            ((s["label"] + "\n") if s["label"] else "") + s["text"] for s in sections
        )
        supplements[pid] = {
            "text": text,
            "title": title,
            "record": record,
            "path": path,
            "pmid": entry["pmid"],
            "doi_present": bool(dois),
        }
        input_hashes[str(path.relative_to(root))] = checksum(path)
    report_hash = checksum(acquisition)
    new_pages, locators, changed = [], [], []
    for paper in papers:
        pid = paper["paper_id"]
        old_pages = [p for p in pages if p["paper_id"] == pid]
        if pid not in supplements:
            new_pages.extend(old_pages)
            locators.extend(
                {
                    "paper_id": pid,
                    "source_unit": p["page"],
                    "kind": "original_baseline_page",
                    "original_page": p["page"],
                }
                for p in old_pages
            )
            continue
        supplement = supplements[pid]
        retained = old_pages if paper["availability"] == "partial_pdf" else []
        unit = len(retained) + 1
        rows = retained + [{"paper_id": pid, "page": unit, "text": supplement["text"]}]
        new_pages.extend(rows)
        locators.extend(
            {
                "paper_id": pid,
                "source_unit": p["page"],
                "kind": "original_partial_pdf_page",
                "original_page": p["page"],
            }
            for p in retained
        )
        locators.append(
            {
                "paper_id": pid,
                "source_unit": unit,
                "kind": "pubmed_abstract",
                "original_page": None,
                "pmid": supplement["pmid"],
                "source_url": supplement["record"]["source_url"],
            }
        )
        paper.update(
            title=supplement["title"],
            abstract=supplement["text"],
            pdf_path=None,
            availability="partial_pdf_plus_abstract" if retained else "abstract_only",
            source_kind="partial_pdf_plus_abstract" if retained else "abstract_only",
            pages=len(rows),
            text_characters=sum(len(p["text"]) for p in rows),
        )
        paper["baseline_source"] = original[pid]
        source_path = destination / "sources" / f"{pid}.json"
        paper["source_path"] = source_path.relative_to(root).as_posix()
        source_bundle = {
            "paper_id": pid,
            "baseline_source": original[pid],
            "abstract_record": supplement["record"],
            "source_units": rows,
        }
        supplement["bundle"] = source_bundle
        paper["source_sha256"] = hashlib.sha256(
            json.dumps(source_bundle, ensure_ascii=False, indent=2).encode("utf-8")
        ).hexdigest()
        changed.append(
            {
                "paper_id": pid,
                "before": original[pid]["availability"],
                "after": paper["availability"],
                "retained_pdf_pages": len(retained),
                "abstract_unit": unit,
                "doi_present_in_xml": supplement["doi_present"],
            }
        )
    validate_pages(papers, new_pages)
    config = read(baseline / "config.json")
    config["prior_budget_runs"] = list(
        dict.fromkeys([*config.get("prior_budget_runs", []), baseline.name])
    )
    for name in config["prior_budget_runs"]:
        if (
            Path(name).name != name
            or name in {".", "..", destination.name}
            or not (baseline.parent / name).is_dir()
        ):
            raise ValueError("Invalid shared budget run")
    # All identity and content checks precede directory creation.
    destination.mkdir()
    for name in required:
        path = destination / "parent_snapshot" / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes((baseline / name).read_bytes())
    for pid, supplement in supplements.items():
        write(destination / "sources" / f"{pid}.json", supplement["bundle"])
        path = destination / "acquisition_snapshot" / f"{pid}_abstract.json"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(supplement["path"].read_bytes())
    (destination / "acquisition_snapshot" / "pubmed_batch.xml").write_bytes(raw.read_bytes())
    (destination / "acquisition_snapshot" / "report.json").write_bytes(acquisition.read_bytes())
    manifest.update(
        papers=papers,
        corpus_version=destination.name,
        source_policy="Supplemented fixed corpus; abstract source units are not PDF pages",
        parent_corpus_sha256=before["corpus_manifest.json"],
    )
    write(destination / "corpus_manifest.json", manifest)
    write(destination / "source_pages.json", new_pages)
    write(destination / "source_locators.json", locators)
    write(destination / "config.json", config)
    result = {
        "status": "prepared_corpus_not_executed",
        "baseline": baseline.name,
        "baseline_hashes": before,
        "acquisition_report_sha256": report_hash,
        "acquisition_input_hashes": input_hashes,
        "changed_sources": changed,
        "papers": len(papers),
        "unchanged_papers": len(papers) - len(changed),
        "fulltext_count_increased": False,
        "model_calls": 0,
        "human_validation": "pending",
        "new_research_results": False,
        "builder_sha256": checksum(Path(__file__)),
        "output_sha256": {
            n: checksum(destination / n)
            for n in (
                "corpus_manifest.json",
                "source_pages.json",
                "source_locators.json",
                "config.json",
            )
        },
    }
    write(destination / "corpus_version.json", result)
    (destination / "builder_snapshot.py").write_bytes(Path(__file__).read_bytes())
    if (
        any(checksum(baseline / n) != h for n, h in before.items())
        or checksum(acquisition) != report_hash
        or any(checksum(local_path(root, n)) != h for n, h in input_hashes.items())
    ):
        write(destination / "invalid.json", {"reason": "Inputs changed during preparation"})
        raise RuntimeError("Inputs changed during preparation; do not use this corpus")
    rows = "".join(
        f"<tr><td>{c['paper_id']}</td><td>{c['before']}</td><td>{c['after']}</td>"
        f"<td>{c['retained_pdf_pages']}</td><td>{c['abstract_unit']}</td></tr>"
        for c in changed
    )
    page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>Frozen supplemented corpus</title>
<style>body{{font:17px/1.6 system-ui;max-width:1050px;margin:35px auto;padding:15px}}table{{border-collapse:collapse;width:100%}}td,th{{padding:10px;border:1px solid #bbc}}.note{{background:#fff2c9;padding:18px}}</style>
<h1>Frozen supplemented corpus</h1><p>{html.escape(destination.name)}</p>
<p class="note">Prepared inputs only. No extraction, new findings, synthesis, improvement score or human validation.</p>
<p>{len(papers)} paper records; {len(changed)} supplemented; {len(papers) - len(changed)} unchanged. No additional full-text PDF.</p>
<table><tr><th>Paper</th><th>Before</th><th>After</th><th>PDF pages retained</th><th>Abstract source unit</th></tr>{rows}</table>
<p>Source-unit numbers identify frozen text blocks. An abstract unit has no original PDF page. S009 retains its original partial PDF text before the new abstract. Use source_locators.json to resolve citations.</p>
<p>Only primary abstract content enters model packets. Acquisition notes, prior findings, reference coding and human judgments are excluded.</p>
<p>Use the semantic extraction runner with this directory as source-run and a new sibling output directory. The historical evidence.pipeline loader rebuilds its registry and is not a loader for this supplemented corpus.</p>
<p><a href="corpus_version.json">Version and hashes</a> · <a href="source_locators.json">Citation locator map</a></p></html>"""
    (destination / "index.html").write_text(page, encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--acquisition", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            prepare(args.project_root, args.baseline, args.acquisition, args.output_dir), indent=2
        )
    )


if __name__ == "__main__":
    main()
