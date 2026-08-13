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
    page_title="ExamLens AI v2",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
dark = st.session_state.dark_mode

if dark:
    BG, CARD, BORDER, TEXT, MUTED = "#0b1020", "#11182b", "#26324a", "#eef2ff", "#9aa8c7"
    ACCENT, ACCENT2, GOOD, WARN = "#7c6ff7", "#4f46e5", "#10b981", "#f59e0b"
else:
    BG, CARD, BORDER, TEXT, MUTED = "#f7f8fc", "#ffffff", "#dfe3ef", "#172033", "#647089"
    ACCENT, ACCENT2, GOOD, WARN = "#5b5bd6", "#4338ca", "#059669", "#d97706"

st.markdown(f"""
<style>
html, body, .stApp {{ background:{BG}!important; color:{TEXT}!important; }}
.block-container {{ max-width:1250px; padding-top:1.4rem; }}
section[data-testid="stSidebar"] > div {{ background:{CARD}!important; border-right:1px solid {BORDER}; }}
section[data-testid="stSidebar"] * {{ color:{TEXT}!important; }}
.hero {{ background:linear-gradient(135deg,#11142d,#4f46e5); padding:2.3rem 2rem;
         border-radius:24px; margin-bottom:1.5rem; text-align:center; }}
.hero h1 {{ color:white; font-size:2.7rem; margin:0; letter-spacing:-1px; }}
.hero p {{ color:#c7d2fe; margin:.5rem 0 0; }}
.pill {{ display:inline-block; margin:10px 3px 0; padding:5px 11px; border-radius:999px;
         background:rgba(255,255,255,.12); color:white; font-size:.76rem; }}
.card {{ background:{CARD}; border:1px solid {BORDER}; border-radius:16px; padding:1rem; }}
.metric {{ text-align:center; }}
.metric .n {{ font-size:2rem; font-weight:800; color:{ACCENT}; }}
.metric .l {{ font-size:.72rem; color:{MUTED}; text-transform:uppercase; letter-spacing:.08em; }}
.priority {{ padding:.7rem .9rem; margin:.45rem 0; border-radius:10px; background:{CARD};
             border:1px solid {BORDER}; }}
.pred {{ padding:.85rem 1rem; margin:.45rem 0; border-radius:12px; background:{CARD};
         border:1px solid {BORDER}; border-left:4px solid {ACCENT}; }}
.day {{ padding:1rem; margin:.55rem 0; border-radius:14px; background:{CARD};
        border:1px solid {BORDER}; border-left:4px solid {ACCENT}; }}
.formula {{ font-family:monospace; padding:.8rem; margin:.4rem 0; border-radius:10px;
            background:rgba(79,70,229,.08); border:1px solid {BORDER}; }}
.notice {{ padding:.85rem 1rem; border-radius:12px; background:rgba(16,185,129,.08);
           border:1px solid rgba(16,185,129,.25); margin:.7rem 0; }}
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
    st.caption("v2 • evidence-first exam analysis")
    if st.button(("☀️ Light mode" if dark else "🌙 Dark mode"), use_container_width=True):
        st.session_state.dark_mode = not dark
        st.rerun()

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
<h1>🎯 ExamLens AI <span style="color:#a5b4fc">v2</span></h1>
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
            fig.update_layout(height=420, xaxis_tickangle=-30, paper_bgcolor=BG, plot_bgcolor=BG, font_color=TEXT)
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
                fig2.update_layout(title="Difficulty distribution", height=300, paper_bgcolor=BG, plot_bgcolor=BG, font_color=TEXT)
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
