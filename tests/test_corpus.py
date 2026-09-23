"""Synthetic source-version checks, not scientific evaluation results."""

import copy

import pytest

from res_pipeline.evidence import corpus, semantic_pipeline


@pytest.fixture
def inputs(tmp_path):
    baseline = tmp_path / "runs/baseline"
    baseline.mkdir(parents=True)
    papers = [
        {
            "paper_id": pid,
            "title": "Synthetic study " + pid,
            "doi": "10.1/" + pid,
            "year": 2000,
            "study_family_id": pid,
            "source_path": "original.pdf",
            "source_sha256": "fixture",
            "availability": availability,
            "pages": 1,
            "text_characters": 8,
        }
        for pid, availability in (
            ("S001", "metadata_snippet_only"),
            ("S009", "partial_pdf"),
            ("S020", "fulltext_available"),
        )
    ]
    corpus.write(baseline / "corpus_manifest.json", {"papers": papers})
    corpus.write(
        baseline / "source_pages.json",
        [{"paper_id": p["paper_id"], "page": 1, "text": "old text"} for p in papers],
    )
    corpus.write(
        baseline / "config.json",
        {"extractor_model": "synthetic", "critic_model": "synthetic", "prior_budget_runs": []},
    )
    raw = tmp_path / "capture/batch.xml"
    raw.parent.mkdir()
    raw.write_text(
        "<PubmedArticleSet>"
        + "".join(
            f"<PubmedArticle><MedlineCitation><PMID>{i}</PMID><Article><ArticleTitle>Synthetic study {pid}</ArticleTitle>"
            '<Abstract><AbstractText Label="RESULTS">New source text.</AbstractText></Abstract></Article></MedlineCitation>'
            f'<PubmedData><ArticleIdList><ArticleId IdType="doi">10.1/{pid}</ArticleId></ArticleIdList></PubmedData></PubmedArticle>'
            for i, pid in enumerate(("S001", "S009"), 1)
        )
        + "</PubmedArticleSet>",
        encoding="utf-8",
    )
    entries = []
    for i, pid in enumerate(("S001", "S009"), 1):
        p = tmp_path / f"capture/{pid}.json"
        corpus.write(
            p,
            {
                "paper_id": pid,
                "pmid": str(i),
                "title": "Synthetic study " + pid,
                "doi_expected": "10.1/" + pid,
                "availability": "abstract_only",
                "source_batch_sha256": corpus.checksum(raw),
                "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{i}/",
                "abstract_sections": [{"label": "RESULTS", "text": "New source text."}],
            },
        )
        entries.append(
            {
                "paper_id": pid,
                "pmid": str(i),
                "doi": "10.1/" + pid,
                "source_record_path": p.relative_to(tmp_path).as_posix(),
                "source_record_sha256": corpus.checksum(p),
                "note": "BENCHMARK_SECRET",
            }
        )
    report = tmp_path / "capture/report.json"
    corpus.write(
        report,
        {
            "baseline_hashes_after": {
                n: corpus.checksum(baseline / n)
                for n in ("corpus_manifest.json", "source_pages.json", "config.json")
            },
            "acquisition": {
                "raw_path": raw.relative_to(tmp_path).as_posix(),
                "raw_sha256": corpus.checksum(raw),
            },
            "records": entries,
        },
    )
    return tmp_path, baseline, report, tmp_path / "runs/enriched"


def test_source_version_preserves_partial_pdf_and_fulltext(inputs, monkeypatch):
    root, baseline, report, dest = inputs
    before = {p.name: p.read_bytes() for p in baseline.iterdir()}
    result = corpus.prepare(*inputs)
    assert result["papers"] == 3 and result["unchanged_papers"] == 1
    assert not result["new_research_results"] and result["model_calls"] == 0
    assert before == {p.name: p.read_bytes() for p in baseline.iterdir()}
    papers = {p["paper_id"]: p for p in corpus.read(dest / "corpus_manifest.json")["papers"]}
    old = {p["paper_id"]: p for p in corpus.read(baseline / "corpus_manifest.json")["papers"]}
    assert papers["S020"] == old["S020"]
    assert papers["S009"]["availability"] == "partial_pdf_plus_abstract"
    pages = corpus.read(dest / "source_pages.json")
    assert [p for p in pages if p["paper_id"] == "S009"][0]["text"] == "old text"
    assert len([p for p in pages if p["paper_id"] == "S009"]) == 2
    locators = corpus.read(dest / "source_locators.json")
    assert (
        next(p for p in locators if p["paper_id"] == "S009" and p["source_unit"] == 2)[
            "original_page"
        ]
        is None
    )
    for pid in ("S001", "S009"):
        assert corpus.checksum(root / papers[pid]["source_path"]) == papers[pid]["source_sha256"]
    monkeypatch.setattr(
        semantic_pipeline, "RunClient", lambda *a, **k: pytest.fail("Offline API client")
    )
    status = semantic_pipeline.run(dest, root / "runs/prepared")
    assert status["machine_stage"] == "prepared_not_executed"
    packet = (root / "runs/prepared/packets/S001.json").read_text(encoding="utf-8")
    assert "BENCHMARK_SECRET" not in packet and "NOT ARTICLE FULL TEXT" in packet
    assert corpus.read(root / "runs/prepared/config.json")["prior_budget_runs"] == [
        "baseline",
        "enriched",
    ]


@pytest.mark.parametrize(
    "kind", ["baseline", "raw", "parsed", "duplicate", "path", "xml_disagreement"]
)
def test_bad_identity_rejected_before_creation(inputs, kind):
    root, baseline, report_path, dest = inputs
    report = corpus.read(report_path)
    if kind == "baseline":
        (baseline / "config.json").write_text("{}")
    elif kind == "raw":
        (root / "capture/batch.xml").write_text("<wrong/>")
    elif kind in {"parsed", "xml_disagreement"}:
        p = root / report["records"][0]["source_record_path"]
        value = corpus.read(p)
        value["abstract_sections"][0]["text"] = "Invented result"
        corpus.write(p, value)
        if kind == "xml_disagreement":
            report["records"][0]["source_record_sha256"] = corpus.checksum(p)
    elif kind == "duplicate":
        report["records"].append(copy.deepcopy(report["records"][0]))
    elif kind == "path":
        report["records"][0]["source_record_path"] = "../outside.json"
    corpus.write(report_path, report)
    with pytest.raises(ValueError):
        corpus.prepare(*inputs)
    assert not dest.exists()


def test_refuse_existing_destination(inputs):
    inputs[3].mkdir()
    sentinel = inputs[3] / "keep.txt"
    sentinel.write_text("Preserved")
    with pytest.raises(ValueError, match="overwriting"):
        corpus.prepare(*inputs)
    assert sentinel.read_text() == "Preserved"


def test_missing_page_rejected_even_if_parent_hash_updated(inputs):
    root, baseline, report_path, dest = inputs
    corpus.write(baseline / "source_pages.json", [])
    report = corpus.read(report_path)
    report["baseline_hashes_after"]["source_pages.json"] = corpus.checksum(
        baseline / "source_pages.json"
    )
    corpus.write(report_path, report)
    with pytest.raises(ValueError, match="Missing"):
        corpus.prepare(*inputs)
    assert not dest.exists()
