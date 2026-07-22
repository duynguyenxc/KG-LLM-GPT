"""Span repair: resolve quotes that failed exact matching, via normalized alignment.

PDF text extraction introduces hyphenation artifacts, line-break whitespace, and
typographic quote variants, so an honest verbatim quote from the model often fails
an exact ``str.find``. This pass builds a normalized view of the canonical text
WITH an index map back to original character offsets, normalizes the quote the
same way, and searches in normalized space — recovering exact original spans
without ever altering the stored canonical text or the quote.

Pure Python (no LLM). Quotes that still fail remain flagged (never fabricated)
and are surfaced at HITL-2.
"""

from __future__ import annotations

import re

from res_pipeline.core.db import get_connection, log_audit_event

_QUOTE_TRANSLATION = str.maketrans({
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", " ": " ",
})


def _normalize_with_map(text: str) -> tuple[str, list[int]]:
    """Lowercased, dehyphenated, whitespace-collapsed text + map to original offsets."""
    translated = text.translate(_QUOTE_TRANSLATION)
    out_chars: list[str] = []
    index_map: list[int] = []
    i, n = 0, len(translated)
    while i < n:
        ch = translated[i]
        # Dehyphenate "word-\n continuation" artifacts: hyphen followed by whitespace
        # between two letters.
        if (
            ch == "-" and out_chars and out_chars[-1].isalpha()
            and i + 1 < n and translated[i + 1].isspace()
        ):
            j = i + 1
            while j < n and translated[j].isspace():
                j += 1
            if j < n and translated[j].isalpha():
                i = j  # skip hyphen+whitespace entirely
                continue
        if ch.isspace():
            if out_chars and out_chars[-1] != " ":
                out_chars.append(" ")
                index_map.append(i)
            i += 1
            continue
        out_chars.append(ch.lower())
        index_map.append(i)
        i += 1
    return "".join(out_chars), index_map


def _normalize_quote(quote: str) -> str:
    q = quote.translate(_QUOTE_TRANSLATION).lower()
    q = re.sub(r"(?<=[a-z])-\s+(?=[a-z])", "", q)  # dehyphenate
    q = re.sub(r"\s+", " ", q).strip()
    return q


def fuzzy_repair_spans(run_id: str, min_block_ratio: float = 0.70) -> dict:
    """Second-tier repair: near-verbatim quotes located via longest-common-block.

    Accepts a span only when a single contiguous common block covers at least
    ``min_block_ratio`` of the normalized quote; the located span is recorded
    with ``match_kind='fuzzy'`` so faithfulness metrics can report exact /
    normalized / fuzzy tiers separately (never conflated).
    """
    import difflib

    with get_connection() as conn:
        studies = conn.execute(
            "SELECT DISTINCT study_id FROM entity_instances WHERE NOT quote_resolved"
        ).fetchall()

    repaired, still = 0, 0
    for study_row in studies:
        study_id = study_row["study_id"]
        with get_connection() as conn:
            canonical = conn.execute(
                "SELECT canonical_text FROM canonical_texts WHERE study_id=%s",
                (study_id,),
            ).fetchone()["canonical_text"]
            pending = conn.execute(
                "SELECT entity_id, verbatim_quote FROM entity_instances "
                "WHERE study_id=%s AND NOT quote_resolved",
                (study_id,),
            ).fetchall()
        norm_text, index_map = _normalize_with_map(canonical)
        with get_connection() as conn:
            for row in pending:
                norm_quote = _normalize_quote(row["verbatim_quote"])
                if len(norm_quote) < 20:
                    still += 1
                    continue
                matcher = difflib.SequenceMatcher(None, norm_quote, norm_text,
                                                  autojunk=False)
                block = max(matcher.get_matching_blocks(), key=lambda b: b.size)
                if block.size / len(norm_quote) < min_block_ratio:
                    still += 1
                    continue
                start = index_map[block.b]
                end = index_map[block.b + block.size - 1] + 1
                conn.execute(
                    "UPDATE entity_instances SET char_start=%s, char_end=%s, "
                    "quote_resolved=TRUE, match_kind='fuzzy' WHERE entity_id=%s",
                    (start, end, row["entity_id"]),
                )
                repaired += 1
    log_audit_event(run_id, "span_repair", "fuzzy_spans_repaired",
                    detail={"repaired": repaired, "still_unresolved": still,
                            "min_block_ratio": min_block_ratio})
    return {"repaired": repaired, "still_unresolved": still}


def repair_spans(run_id: str) -> dict:
    """Re-attempt span resolution for all unresolved quotes. Returns counts."""
    with get_connection() as conn:
        studies = conn.execute(
            "SELECT DISTINCT study_id FROM entity_instances WHERE NOT quote_resolved"
        ).fetchall()

    repaired, still_unresolved = 0, 0
    for study_row in studies:
        study_id = study_row["study_id"]
        with get_connection() as conn:
            canonical = conn.execute(
                "SELECT canonical_text FROM canonical_texts WHERE study_id=%s",
                (study_id,),
            ).fetchone()["canonical_text"]
            pending = conn.execute(
                "SELECT entity_id, verbatim_quote FROM entity_instances "
                "WHERE study_id=%s AND NOT quote_resolved",
                (study_id,),
            ).fetchall()

        norm_text, index_map = _normalize_with_map(canonical)
        with get_connection() as conn:
            for row in pending:
                norm_quote = _normalize_quote(row["verbatim_quote"])
                pos = norm_text.find(norm_quote)
                if pos == -1 or not norm_quote:
                    still_unresolved += 1
                    continue
                start = index_map[pos]
                end_norm_index = pos + len(norm_quote) - 1
                end = index_map[end_norm_index] + 1
                conn.execute(
                    "UPDATE entity_instances SET char_start=%s, char_end=%s, "
                    "quote_resolved=TRUE WHERE entity_id=%s",
                    (start, end, row["entity_id"]),
                )
                repaired += 1

    log_audit_event(run_id, "span_repair", "spans_repaired",
                    detail={"repaired": repaired, "still_unresolved": still_unresolved})
    return {"repaired": repaired, "still_unresolved": still_unresolved}
