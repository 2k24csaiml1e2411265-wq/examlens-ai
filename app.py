import html
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from pdf_utils import extract_text_from_multiple_pdfs
from gemini_helper import analyze_all_in_one, generate_mcqs
from pdf_generator import (
    generate_predictions_pdf, generate_roadmap_pdf,
    generate_mcq_pdf, generate_extracted_questions_pdf,
)

st.set_page_config(
    page_title="ExamLens AI v3",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Light theme ----------
# ExamLens AI v3 uses a deliberately light, professional visual system.
# The palette is kept high-contrast and print-friendly for students.
BG = "#F7F9FC"
CARD = "#FFFFFF"
CARD_ALT = "#F1F5F9"
BORDER = "#E2E8F0"
TEXT = "#172033"
MUTED = "#64748B"
ACCENT = "#4F46E5"
ACCENT2 = "#3730A3"
GOOD = "#059669"
WARN = "#D97706"
INPUT_BG = "#FFFFFF"
CHART_GRID = "#E2E8F0"
HERO_START = "#EEF2FF"
HERO_END = "#C7D2FE"

st.markdown(f"""
<style>
:root {{
    --el-bg: {BG};
    --el-card: {CARD};
    --el-card-alt: {CARD_ALT};
    --el-border: {BORDER};
    --el-text: {TEXT};
    --el-muted: {MUTED};
    --el-accent: {ACCENT};
    --el-accent-2: {ACCENT2};
    --el-good: {GOOD};
    --el-warn: {WARN};
    --el-input: {INPUT_BG};
    --el-grid: {CHART_GRID};
}}

/* Base */
html, body, [data-testid="stAppViewContainer"], .stApp {{
    background: var(--el-bg) !important;
    color: var(--el-text) !important;
}}

.block-container {{
    max-width: 1280px;
    padding: 1.75rem 2rem 4rem;
}}

/* Typography */
h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{
    color: var(--el-text);
}}

[data-testid="stCaptionContainer"], .stCaption {{
    color: var(--el-muted) !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: #FFFFFF !important;
    border-right: 1px solid var(--el-border);
    box-shadow: 8px 0 30px rgba(15, 23, 42, .035);
}}
section[data-testid="stSidebar"] > div {{
    background: #FFFFFF !important;
}}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    color: var(--el-text) !important;
}}
section[data-testid="stSidebar"] hr {{
    border-color: var(--el-border) !important;
}}

/* Hero */
.hero {{
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, {HERO_START} 0%, #FFFFFF 52%, {HERO_END} 100%);
    border: 1px solid #D9E0F2;
    padding: clamp(1.7rem, 4vw, 2.8rem) clamp(1.2rem, 4vw, 2.4rem);
    border-radius: 26px;
    margin-bottom: 1.7rem;
    text-align: center;
    box-shadow: 0 18px 50px rgba(79, 70, 229, .10);
}}
.hero::before {{
    content: "";
    position: absolute;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    background: rgba(99, 102, 241, .10);
    top: -120px;
    right: -60px;
}}
.hero h1 {{
    position: relative;
    color: #111827 !important;
    font-size: clamp(2rem, 5vw, 2.85rem);
    font-weight: 850;
    margin: 0;
    letter-spacing: -1.5px;
}}
.hero-version {{ color: var(--el-accent); }}
.hero p {{
    position: relative;
    color: #475569 !important;
    font-size: 1rem;
    margin: .65rem 0 0;
}}
.pill {{
    display: inline-block;
    margin: 12px 3px 0;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(255,255,255,.82);
    color: #3730A3;
    font-size: .76rem;
    font-weight: 650;
    border: 1px solid #C7D2FE;
    box-shadow: 0 2px 8px rgba(79,70,229,.06);
}}

/* Cards */
.card, .metric, .priority, .pred, .day, .formula {{
    background: var(--el-card) !important;
    color: var(--el-text) !important;
    border-color: var(--el-border) !important;
}}
.card {{
    border: 1px solid var(--el-border);
    border-radius: 16px;
    padding: 1rem;
    box-shadow: 0 5px 18px rgba(15,23,42,.035);
}}
.metric {{ text-align: center; padding: 1.05rem .7rem; }}
.metric .n {{
    font-size: 2rem;
    font-weight: 850;
    color: var(--el-accent);
    line-height: 1.1;
}}
.metric .l {{
    margin-top: .35rem;
    font-size: .70rem;
    color: var(--el-muted);
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 650;
}}
.priority {{
    padding: .72rem .9rem;
    margin: .45rem 0;
    border-radius: 11px;
    border: 1px solid var(--el-border);
    box-shadow: 0 2px 8px rgba(15,23,42,.025);
}}
.pred {{
    padding: .9rem 1rem;
    margin: .45rem 0;
    border-radius: 12px;
    border: 1px solid var(--el-border);
    border-left: 4px solid var(--el-accent) !important;
    box-shadow: 0 3px 12px rgba(15,23,42,.03);
}}
.day {{
    padding: 1rem;
    margin: .55rem 0;
    border-radius: 14px;
    border: 1px solid var(--el-border);
    border-left: 4px solid var(--el-accent) !important;
}}
.formula {{
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    padding: .8rem;
    margin: .4rem 0;
    border-radius: 10px;
    background: #F5F3FF !important;
    border: 1px solid #DDD6FE;
}}
.notice {{
    padding: .9rem 1rem;
    border-radius: 12px;
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
    margin: .7rem 0;
    color: #065F46;
}}

/* Inputs and uploader */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {{
    background: var(--el-input) !important;
    border-color: var(--el-border) !important;
    border-radius: 10px !important;
}}
[data-testid="stFileUploaderDropzone"] {{
    background: #FFFFFF !important;
    border: 1.5px dashed #C7D2FE !important;
    border-radius: 14px !important;
    transition: border-color .15s ease, box-shadow .15s ease;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: var(--el-accent) !important;
    box-shadow: 0 8px 24px rgba(79,70,229,.07);
}}
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span {{
    color: var(--el-muted) !important;
}}

/* Buttons */
.stButton > button, .stDownloadButton > button {{
    min-height: 42px;
    border-radius: 10px !important;
    border: 1px solid var(--el-border) !important;
    background: #FFFFFF !important;
    color: var(--el-text) !important;
    font-weight: 650 !important;
    transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    transform: translateY(-1px);
    border-color: #A5B4FC !important;
    box-shadow: 0 8px 22px rgba(79,70,229,.12);
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #4F46E5, #6366F1) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 8px 20px rgba(79,70,229,.18);
}}
.stButton > button[kind="primary"]:hover {{
    box-shadow: 0 11px 26px rgba(79,70,229,.24);
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    border-bottom: 1px solid var(--el-border);
}}
.stTabs [data-baseweb="tab"] {{
    color: var(--el-muted) !important;
    font-weight: 600;
    padding: .7rem .85rem;
}}
.stTabs [data-baseweb="tab"][aria-selected="true"] {{
    color: var(--el-accent) !important;
    border-bottom-color: var(--el-accent) !important;
}}

/* Alerts/status */
[data-testid="stAlert"] {{ border-radius: 12px !important; }}
[data-testid="stStatusWidget"] {{ border-radius: 12px !important; }}

/* Dataframes */
[data-testid="stDataFrame"] {{
    border: 1px solid var(--el-border);
    border-radius: 12px;
    overflow: hidden;
}}

/* Links */
a {{ color: var(--el-accent) !important; }}

/* Responsive */
@media (max-width: 768px) {{
    .block-container {{ padding: 1rem .8rem 2rem; }}
    .hero {{ border-radius: 20px; padding: 1.5rem 1rem; }}
    .hero h1 {{ letter-spacing: -1px; }}
    .metric .n {{ font-size: 1.55rem; }}
    .pill {{ font-size: .70rem; padding: 5px 9px; }}
}}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
subjects = [
    "Engineering Mathematics", "Engineering Physics", "Engineering Chemistry",
    "AIML / Machine Learning", "Deep Learning", "NLP (Natural Language Processing)",
    "Computer Vision", "Data Structures & Algorithms", "DBMS (Database Management)",
    "Operating Systems", "Artificial Intelligence", "Computer Networks",
    "Software Engineering", "Theory of Computation", "Compiler Design",
    "Digital Electronics", "Microprocessor & Microcontroller",
    "Object Oriented Programming", "Web Technologies", "Other",
]

with st.sidebar:
    st.markdown("## 🎯 ExamLens AI")
    st.caption("v3 • light edition • evidence-first exam analysis")
    st.divider()
    subject = st.selectbox("📚 Subject", subjects)
    st.divider()
    st.markdown("### Pipeline")
    for x in ["Upload PDFs", "Extract text", "Analyze patterns", "Predict questions",
              "Build roadmap", "Practice MCQs", "Export PDFs"]:
        st.write("✓ " + x)
    st.divider()
    st.caption("🔐 PDFs are processed in the current session. The app does not save uploaded files to a database.")

# ---------- Header ----------
st.markdown("""
<div class="hero">
<h1>🎯 ExamLens AI <span class="hero-version">v3</span></h1>
<p>Turn previous-year papers into a focused, evidence-based study plan.</p>
<span class="pill">⚡ Groq + Llama</span>
<span class="pill">📄 Multi-PDF</span>
<span class="pill">📊 Topic Patterns</span>
<span class="pill">🎯 Predictions</span>
<span class="pill">🗺️ 7-Day Plan</span>
<span class="pill">📝 MCQs</span>
</div>
""", unsafe_allow_html=True)

# ---------- Upload ----------
st.subheader("📄 1. Upload previous-year papers")
files = st.file_uploader(
    "Upload selectable-text PDFs", type=["pdf"], accept_multiple_files=True,
    help="Best results come from selectable-text PDFs. Scanned PDFs may need OCR.",
)

if files:
    st.success(f"{len(files)} paper(s) selected: " + ", ".join(f.name for f in files))

if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "mcqs" not in st.session_state:
    st.session_state.mcqs = None
if "paper_meta" not in st.session_state:
    st.session_state.paper_meta = []
if "analysis_subject" not in st.session_state:
    st.session_state.analysis_subject = ""

if st.session_state.analysis_subject != subject:
    st.session_state.analysis = None
    st.session_state.paper_meta = []
    st.session_state.analysis_subject = subject

analyze = st.button("🔍 Analyze papers", type="primary", disabled=not files, use_container_width=True)

if analyze:
    with st.status("Running ExamLens AI pipeline…", expanded=True) as status:
        st.write("Extracting text from uploaded PDFs…")
        raw, meta = extract_text_from_multiple_pdfs(files)
        st.session_state.paper_meta = meta
        readable = sum(1 for m in meta if m["status"] == "ok")
        st.write(f"Readable papers: {readable}/{len(meta)}")

        if not raw.strip() or readable == 0:
            status.update(label="No readable PDF text found", state="error")
            st.error("These PDFs appear to be scanned/image-only or have no extractable text. Add OCR support or upload selectable-text PDFs.")
            st.stop()

        st.write(f"Analyzing {subject} with the selected model…")
        data = analyze_all_in_one(raw, subject)
        st.session_state.analysis = data

        if data.get("analysis_status") == "success":
            status.update(label="Analysis complete", state="complete")
        else:
            status.update(label="Analysis failed", state="error")

# ---------- Results ----------
d = st.session_state.analysis
if d and d.get("analysis_status") == "success":
    tf = d.get("topic_frequency", {})
    hp = d.get("high_priority_topics", [])
    mp = d.get("medium_priority_topics", [])
    lp = d.get("low_priority_topics", [])
    questions = d.get("extracted_questions", "")
    roadmap = d.get("roadmap", [])
    formulas = d.get("key_formulas", [])

    st.markdown('<div class="notice">✅ <b>Evidence-first result:</b> topic frequency and priorities are derived from the extracted paper text; predictions are forecasts, not guarantees.</div>', unsafe_allow_html=True)

    cols = st.columns(5)
    metrics = [
        (len(files), "Papers"), (d.get("total_questions_analyzed", 0), "Questions"),
        (len(tf), "Topics"), (len(hp), "High priority"),
        (sum(m.get("characters", 0) for m in st.session_state.paper_meta), "Extracted chars"),
    ]
    for col, (n, label) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="card metric"><div class="n">{n}</div><div class="l">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("### Results")
    tabs = st.tabs(["📊 Patterns", "🎯 Predictions", "🗺️ Roadmap", "📐 Formulas", "📝 MCQs", "📋 Questions"])

    with tabs[0]:
        if tf:
            df = pd.DataFrame({"Topic": list(tf.keys()), "Frequency": list(tf.values())}).sort_values("Frequency", ascending=False)
            fig = px.bar(df, x="Topic", y="Frequency", text="Frequency", title=f"Recurring topics — {subject}")
            fig.update_layout(height=420, xaxis_tickangle=-30, paper_bgcolor=BG, plot_bgcolor=BG, font_color=TEXT, hoverlabel=dict(bgcolor=CARD, font_color=TEXT), xaxis=dict(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID), yaxis=dict(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No reliable topic-frequency data was returned.")

        a, b = st.columns(2)
        with a:
            st.markdown("#### 🔥 Priority")
            for t in hp: st.markdown(f'<div class="priority">🔥 {html.escape(str(t))}</div>', unsafe_allow_html=True)
            for t in mp: st.markdown(f'<div class="priority">🟡 {html.escape(str(t))}</div>', unsafe_allow_html=True)
            for t in lp: st.markdown(f'<div class="priority">🟢 {html.escape(str(t))}</div>', unsafe_allow_html=True)
        with b:
            diff = d.get("difficulty_distribution", {})
            if diff:
                fig2 = go.Figure(go.Bar(
                    x=list(diff.values()), y=list(diff.keys()), orientation="h",
                    text=list(diff.values()), textposition="outside"
                ))
                fig2.update_layout(title="Difficulty distribution", height=300, paper_bgcolor=BG, plot_bgcolor=BG, font_color=TEXT, hoverlabel=dict(bgcolor=CARD, font_color=TEXT), xaxis=dict(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID), yaxis=dict(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID))
                st.plotly_chart(fig2, use_container_width=True)

        with st.expander("Paper extraction quality"):
            st.dataframe(pd.DataFrame(st.session_state.paper_meta), use_container_width=True, hide_index=True)

    with tabs[1]:
        p10, p2 = d.get("predicted_10mark", []), d.get("predicted_2mark", [])
        st.markdown("#### 🎯 Longer-answer predictions")
        for i, q in enumerate(p10, 1):
            st.markdown(f'<div class="pred"><b>{i}.</b> {html.escape(str(q))}</div>', unsafe_allow_html=True)
        st.markdown("#### ⚡ Short-answer predictions")
        for i, q in enumerate(p2, 1):
            st.markdown(f'<div class="pred"><b>{i}.</b> {html.escape(str(q))}</div>', unsafe_allow_html=True)

        if d.get("wildcard_question"):
            st.warning(f"Wildcard: {d['wildcard_question']}\n\nReason: {d.get('wildcard_reason','')}")

        text = "## Predicted long-answer questions\n" + "\n".join(f"{i}. {q}" for i, q in enumerate(p10, 1))
        text += "\n\n## Predicted short-answer questions\n" + "\n".join(f"{i}. {q}" for i, q in enumerate(p2, 1))
        if d.get("wildcard_question"):
            text += f"\n\n## Wildcard\n{d['wildcard_question']}\nReason: {d.get('wildcard_reason','')}"
        st.download_button("⬇️ Export predictions PDF", generate_predictions_pdf(text, subject),
                           "examlens_predictions.pdf", "application/pdf")

    with tabs[2]:
        if not roadmap:
            st.info("No roadmap was returned.")
        for day in roadmap:
            st.markdown(f"""<div class="day">
            <b>Day {day.get('day','')} • {day.get('hours',3)} hours</b><br>
            <strong>{html.escape(str(day.get('topic','')))}</strong><br>
            <span style="color:{MUTED}">{html.escape(str(day.get('focus','')))}</span><br><br>
            {" • ".join(html.escape(str(x)) for x in day.get("tasks", []))}<br>
            <small>💡 {html.escape(str(day.get('tip','')))}</small>
            </div>""", unsafe_allow_html=True)
        tips = d.get("quick_tips", [])
        if tips:
            st.info("Exam tips\n\n" + "\n".join("• " + str(x) for x in tips))
        rm_text = "## 7-Day Roadmap\n\n"
        for day in roadmap:
            rm_text += f"Day {day.get('day')}: {day.get('topic')}\nFocus: {day.get('focus')}\n"
            rm_text += "\n".join("- " + str(x) for x in day.get("tasks", [])) + f"\nTip: {day.get('tip')}\n\n"
        st.download_button("⬇️ Export roadmap PDF", generate_roadmap_pdf(rm_text, subject),
                           "examlens_roadmap.pdf", "application/pdf")

    with tabs[3]:
        if formulas:
            for i, f in enumerate(formulas, 1):
                st.markdown(f'<div class="formula">📐 {i}. {html.escape(str(f))}</div>', unsafe_allow_html=True)
        else:
            st.info("No formulas/definitions were returned.")

    with tabs[4]:
        if not hp:
            st.info("Run an analysis with at least one detected topic first.")
        else:
            topic = st.selectbox("Topic", hp, key="mcq_topic_select")
            n = st.slider("Number of MCQs", 3, 10, 5)
            if st.button("🎲 Generate MCQs", key="generate_mcqs"):
                with st.spinner("Generating MCQs…"):
                    try:
                        st.session_state.mcqs = generate_mcqs(subject, topic, n)
                        st.session_state.mcq_topic_name = topic
                    except Exception as exc:
                        st.error(str(exc))
            if st.session_state.get("mcqs"):
                st.markdown(st.session_state.mcqs)
                st.download_button(
                    "⬇️ Export MCQs PDF",
                    generate_mcq_pdf(st.session_state.mcqs, st.session_state.get("mcq_topic_name", topic)),
                    "examlens_mcqs.pdf", "application/pdf"
                )

    with tabs[5]:
        if questions:
            st.text_area("Extracted questions", questions, height=480)
            st.download_button(
                "⬇️ Export extracted questions PDF",
                generate_extracted_questions_pdf(questions, subject),
                "examlens_extracted_questions.pdf", "application/pdf"
            )
        else:
            st.info("No questions were extracted.")

else:
    st.markdown("### How it works")
    a, b, c = st.columns(3)
    for col, title, body in [
        (a, "1 • Upload", "Add previous-year papers for one subject."),
        (b, "2 • Analyze", "Extract text and detect recurring concepts."),
        (c, "3 • Prepare", "Use predictions, roadmap, formulas and MCQs."),
    ]:
        with col:
            st.markdown(f'<div class="card"><h4>{title}</h4><p style="color:{MUTED}">{body}</p></div>', unsafe_allow_html=True)
    st.info("Tip: for the most reliable analysis, upload clear selectable-text PDFs from the same subject.")
