"""PDF export helpers."""
import io
import html
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER


PURPLE = colors.HexColor("#5B5BD6")


def _doc(buffer):
    return SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=1.7*cm, leftMargin=1.7*cm,
        topMargin=1.6*cm, bottomMargin=1.6*cm
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


def _build(title, subject, text):
    buf = io.BytesIO()
    doc = _doc(buf)
    title_s, sub_s, h2_s, body_s = _styles()
    story = [
        Paragraph(html.escape(title), title_s),
        Paragraph(html.escape(f"Subject: {subject} • ExamLens AI v2"), sub_s),
        HRFlowable(width="100%", thickness=1, color=PURPLE),
        Spacer(1, 10),
    ]
    for raw in text.splitlines():
        line = raw.strip()
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
