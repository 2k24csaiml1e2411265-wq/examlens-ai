"""PDF export helpers for ExamLens AI."""
import io
import html
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER


PURPLE = colors.HexColor("#5B5BD6")


def _doc(buffer):
    return SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.7 * cm,
        leftMargin=1.7 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
    )


def _styles():
    s = getSampleStyleSheet()
    return (
        ParagraphStyle("title2", parent=s["Title"], fontSize=19, textColor=PURPLE,
                       alignment=TA_CENTER, spaceAfter=5),
        ParagraphStyle("sub2", parent=s["Normal"], fontSize=9, textColor=colors.grey,
                       alignment=TA_CENTER, spaceAfter=14),
        ParagraphStyle("h2x", parent=s["Heading2"], fontSize=13, textColor=PURPLE,
                       spaceBefore=12, spaceAfter=6),
        ParagraphStyle("bodyx", parent=s["Normal"], fontSize=9.5, leading=14,
                       spaceAfter=4),
    )


def _to_lines(value: Any) -> list[str]:
    """Normalize LLM output into printable text lines.

    The model is asked for a string, but JSON responses can occasionally return
    a list/dict. The previous implementation called splitlines() directly and
    crashed with AttributeError in that case.
    """
    if value is None:
        return []

    if isinstance(value, str):
        return value.splitlines()

    if isinstance(value, (list, tuple)):
        lines: list[str] = []
        for item in value:
            if isinstance(item, dict):
                # Preserve useful question text when the model returns objects.
                preferred = item.get("question") or item.get("text") or item.get("prompt")
                if preferred is not None:
                    lines.append(str(preferred))
                else:
                    lines.append(" • ".join(f"{k}: {v}" for k, v in item.items()))
            else:
                lines.append(str(item))
        return lines

    if isinstance(value, dict):
        return [f"{k}: {v}" for k, v in value.items()]

    return [str(value)]


def _build(title, subject, text):
    buf = io.BytesIO()
    doc = _doc(buf)
    title_s, sub_s, h2_s, body_s = _styles()
    story = [
        Paragraph(html.escape(str(title)), title_s),
        Paragraph(html.escape(f"Subject: {subject} • ExamLens AI"), sub_s),
        HRFlowable(width="100%", thickness=1, color=PURPLE),
        Spacer(1, 10),
    ]

    for raw in _to_lines(text):
        line = str(raw).strip()
        if not line:
            story.append(Spacer(1, 5))
        elif line.startswith("#"):
            story.append(Paragraph(html.escape(line.lstrip("#").strip()), h2_s))
        else:
            line = line.replace("**", "")
            story.append(Paragraph(html.escape(line), body_s))

    doc.build(story)
    return buf.getvalue()


def generate_predictions_pdf(text, subject):
    return _build("ExamLens AI — Predicted Questions", subject, text)


def generate_roadmap_pdf(text, subject):
    return _build("ExamLens AI — 7-Day Study Roadmap", subject, text)


def generate_mcq_pdf(text, topic):
    return _build(f"ExamLens AI — MCQ Practice: {topic}", topic, text)


def generate_extracted_questions_pdf(text, subject):
    return _build("ExamLens AI — Extracted Questions", subject, text)
