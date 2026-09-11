"""Render the primary research documents into clean, readable PDFs."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]


def inline(text: str) -> str:
    text = text.replace("–", "-").replace("—", "-").replace("‑", "-")
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" color="#333333">\1</a>', text)
    text = re.sub(r"\[\^(\d+)\]", r"<super>[\1]</super>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    return re.sub(r"`([^`]+)`", r'<font name="ResearchMono" size="8.3">\1</font>', text)


def build(source: Path, target: Path) -> None:
    pdfmetrics.registerFont(TTFont("ResearchBody", "C:/Windows/Fonts/arial.ttf"))
    pdfmetrics.registerFont(TTFont("ResearchBold", "C:/Windows/Fonts/arialbd.ttf"))
    pdfmetrics.registerFont(TTFont("ResearchItalic", "C:/Windows/Fonts/ariali.ttf"))
    pdfmetrics.registerFont(TTFont("ResearchMono", "C:/Windows/Fonts/consola.ttf"))
    pdfmetrics.registerFontFamily(
        "ResearchBody",
        normal="ResearchBody",
        bold="ResearchBold",
        italic="ResearchItalic",
        boldItalic="ResearchBold",
    )
    body = ParagraphStyle(
        "Research",
        fontName="ResearchBody",
        fontSize=10.2,
        leading=15.3,
        spaceAfter=9,
        alignment=TA_LEFT,
        splitLongWords=True,
        allowWidows=0,
        allowOrphans=0,
    )
    heading = ParagraphStyle(
        "Section",
        parent=body,
        fontName="ResearchBold",
        fontSize=15,
        leading=19,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True,
    )
    subsection = ParagraphStyle(
        "Subsection", parent=heading, fontSize=11.5, leading=15, spaceBefore=12, spaceAfter=7
    )
    title = ParagraphStyle(
        "ResearchTitle", parent=heading, fontSize=23, leading=28, spaceBefore=0, spaceAfter=22
    )
    cell = ParagraphStyle("Cell", parent=body, fontSize=8.1, leading=11.3, spaceAfter=0)
    source_style = ParagraphStyle("Source", parent=body, fontSize=9.2, leading=12.4, spaceAfter=7)
    story = []
    lines = source.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                values = [part.strip() for part in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[:\- ]+", value) for value in values):
                    rows.append([Paragraph(inline(value), cell) for value in values])
                index += 1
            columns = len(rows[0])
            widths = [174 * mm / columns] * columns
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#bbbbbb")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 7),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                )
            )
            story.extend([KeepTogether([table]) if len(rows) <= 7 else table, Spacer(1, 10)])
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), title))
        elif line.startswith("## "):
            if line == "## Sources" and source.name == "METHOD_AND_VERIFICATION_PROTOCOL.md":
                story.append(PageBreak())
            story.append(Paragraph(inline(line[3:]), heading))
        elif line.startswith("### "):
            story.append(Paragraph(inline(line[4:]), subsection))
        else:
            paragraph = [line]
            while (
                index + 1 < len(lines)
                and lines[index + 1].strip()
                and not lines[index + 1].startswith(("#", "|", "[^"))
            ):
                index += 1
                paragraph.append(lines[index].strip())
            text = " ".join(paragraph)
            is_source = bool(re.match(r"^\[\^\d+\]:", text))
            text = re.sub(r"^\[\^(\d+)\]:", r"[\1]", text)
            story.append(Paragraph(inline(text), source_style if is_source else body))
        index += 1
    target.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(
        str(target),
        pagesize=(210 * mm, 297 * mm),
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=lines[0].lstrip("# "),
        author="",
    ).build(story)
    print(target)


if __name__ == "__main__":
    for source, output in [
        ("RICHMOND_OFFICIAL_FINDINGS.md", "Richmond_Official_Findings.pdf"),
        ("METHOD_AND_VERIFICATION_PROTOCOL.md", "Research_Method_and_Verification.pdf"),
    ]:
        build(ROOT / "docs/research" / source, ROOT / "output/pdf" / output)
