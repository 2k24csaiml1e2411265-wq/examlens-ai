import hashlib
import html
import json
import re
from datetime import date, timedelta

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
    page_title="ExamLens AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Light theme ----------
# ExamLens AI uses a deliberately light, professional visual system.
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

/* Inputs, selectboxes, textareas and uploader — force the entire control into light mode */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
[data-testid="stTextArea"] > div,
[data-testid="stTextArea"] textarea {{
    background: #FFFFFF !important;
    background-color: #FFFFFF !important;
    border-color: var(--el-border) !important;
    border-radius: 10px !important;
    color: var(--el-text) !important;
    color-scheme: light !important;
    -webkit-text-fill-color: var(--el-text) !important;
}}

/* Text-area text was inheriting Streamlit/browser dark-mode colors. */
[data-testid="stTextArea"] textarea,
[data-testid="stTextArea"] textarea:focus {{
    color: #172033 !important;
    background: #FFFFFF !important;
    background-color: #FFFFFF !important;
    caret-color: #4F46E5 !important;
    -webkit-text-fill-color: #172033 !important;
    color-scheme: light !important;
    opacity: 1 !important;
}}
[data-testid="stTextArea"] textarea::selection {{
    background: #C7D2FE !important;
    color: #172033 !important;
}}

/* Selectbox closed state and its internal text/icons. */
[data-baseweb="select"] > div,
[data-baseweb="select"] [role="combobox"] {{
    background: #FFFFFF !important;
    background-color: #FFFFFF !important;
    color: #172033 !important;
    color-scheme: light !important;
}}
[data-baseweb="select"] span,
[data-baseweb="select"] input {{
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
}}

/* Selectbox popup rendered outside the main widget tree. */
[role="listbox"],
[role="option"],
div[data-baseweb="popover"] {{
    background: #FFFFFF !important;
    background-color: #FFFFFF !important;
    color: #172033 !important;
    color-scheme: light !important;
}}
[role="option"] * {{
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
}}
[role="option"][aria-selected="true"] {{
    background: #EEF2FF !important;
}}

/* File uploader's native Browse/Upload button. */
[data-testid="stFileUploaderDropzone"] button {{
    background: #FFFFFF !important;
    background-color: #FFFFFF !important;
    color: #172033 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 9px !important;
    box-shadow: none !important;
    color-scheme: light !important;
}}
[data-testid="stFileUploaderDropzone"] button:hover {{
    background: #F8FAFC !important;
    border-color: #A5B4FC !important;
    color: #3730A3 !important;
}}
[data-testid="stFileUploaderDropzone"] button * {{
    color: inherit !important;
    -webkit-text-fill-color: currentColor !important;
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


# ---------- Robust data helpers ----------
def esc(value):
    return html.escape(str(value if value is not None else ""))


def as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    if isinstance(value, dict):
        for key in ("items", "questions", "topics", "predictions", "data", "results"):
            if isinstance(value.get(key), (list, tuple)):
                return list(value[key])
        return [value]
    if isinstance(value, str):
        return [x.strip() for x in value.splitlines() if x.strip()]
    return [value]


def clean_question(value):
    if isinstance(value, dict):
        for key in ("question", "text", "prompt", "content", "query"):
            if key in value:
                return str(value[key]).strip()
        return json.dumps(value, ensure_ascii=False)
    text = str(value).strip()
    text = re.sub(r"^\s*(?:[-*•]|\d+[\).])\s*", "", text)
    return text


def normalize_questions(value):
    # Normalize model question output into {paper: [questions]} for UI/PDF.
    if value is None:
        return {}
    if isinstance(value, dict):
        if all(isinstance(v, (list, tuple)) for v in value.values()):
            normalized = {}
            for k, items in value.items():
                cleaned = []
                for item in items:
                    q = clean_question(item)
                    if q:
                        cleaned.append(q)
                normalized[str(k)] = cleaned
            return normalized
        for key in ("papers", "extracted_questions", "questions", "data"):
            if key in value:
                return normalize_questions(value[key])
        return {"Questions": [clean_question(value)]}
    if isinstance(value, (list, tuple)):
        cleaned = []
        for item in value:
            q = clean_question(item)
            if q:
                cleaned.append(q)
        return {"Extracted questions": cleaned}
    text = str(value).strip()
    if not text:
        return {}
    return {"Extracted questions": [clean_question(x) for x in text.splitlines() if clean_question(x)]}


def question_count(qmap):
    return sum(len(v) for v in qmap.values())


def questions_dataframe(qmap):
    rows=[]
    for paper, qs in qmap.items():
        for i,q in enumerate(qs,1):
            rows.append({"Paper":paper,"Question #":i,"Question":q})
    return pd.DataFrame(rows, columns=["Paper","Question #","Question"])


def question_text(qmap):
    out=[]
    for paper,qs in qmap.items():
        out.append(str(paper))
        out.extend(f"{i}. {q}" for i,q in enumerate(qs,1))
        out.append("")
    return "\n".join(out).strip()


def file_signature(files):
    h=hashlib.sha256()
    for f in files or []:
        h.update(f.name.encode("utf-8"))
        h.update(str(getattr(f,"size",0)).encode("utf-8"))
        try: h.update(f.getvalue())
        except Exception: pass
    return h.hexdigest()


def safe_int(value, default=0):
    try: return int(value)
    except Exception: return default


def fmt_num(value):
    try: return f"{int(value):,}"
    except Exception: return str(value)


def analysis_json(data):
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def prediction_text(data):
    p10=as_list(data.get("predicted_10mark",[])); p2=as_list(data.get("predicted_2mark",[]))
    lines=["## Predicted long-answer questions",""]
    lines += [f"{i}. {clean_question(q)}" for i,q in enumerate(p10,1)]
    lines += ["","## Predicted short-answer questions",""]
    lines += [f"{i}. {clean_question(q)}" for i,q in enumerate(p2,1)]
    if data.get("wildcard_question"):
        lines += ["","## Wildcard",str(data.get("wildcard_question")),f"Reason: {data.get('wildcard_reason','Pattern-based uncertainty.')}"]
    return "\n".join(lines)


def roadmap_text(roadmap):
    lines=["## 7-Day Roadmap",""]
    for i,day in enumerate(as_list(roadmap),1):
        if not isinstance(day,dict):
            lines += [f"Day {i}: {day}",""]
            continue
        lines += [f"Day {day.get('day',i)}: {day.get('topic','')}",f"Focus: {day.get('focus','')}"]
        lines += [f"- {x}" for x in as_list(day.get('tasks',[]))]
        lines += [f"Tip: {day.get('tip','')}",""]
    return "\n".join(lines)


def chart_layout(fig, title=None, height=420):
    fig.update_layout(title=title,height=height,paper_bgcolor=BG,plot_bgcolor=BG,font_color=TEXT,
                      margin=dict(l=20,r=20,t=55,b=30),hoverlabel=dict(bgcolor=CARD,font_color=TEXT))
    fig.update_xaxes(gridcolor=CHART_GRID,zerolinecolor=CHART_GRID)
    fig.update_yaxes(gridcolor=CHART_GRID,zerolinecolor=CHART_GRID)
    return fig


def init_state():
    defaults={
        "analysis":None,"mcqs":None,"mcq_topic_name":"","paper_meta":[],
        "analysis_subject":"","upload_signature":"","raw_text":"",
        "question_search":"","formula_search":"","analysis_runs":0,
    }
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v


init_state()

SUBJECTS=[
    "Engineering Mathematics","Engineering Physics","Engineering Chemistry",
    "AIML / Machine Learning","Deep Learning","NLP (Natural Language Processing)",
    "Computer Vision","Data Structures & Algorithms","DBMS (Database Management)",
    "Operating Systems","Artificial Intelligence","Computer Networks",
    "Software Engineering","Theory of Computation","Compiler Design",
    "Digital Electronics","Microprocessor & Microcontroller","Object Oriented Programming",
    "Web Technologies","Other",
]

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🎯 ExamLens AI")
    st.caption("Light interface • evidence-first exam analysis")
    st.divider()
    subject=st.selectbox("📚 Subject",SUBJECTS,key="subject_selector")
    st.divider()
    st.markdown("### ⚙️ Study settings")
    exam_date=st.date_input("🗓️ Exam date",value=date.today()+timedelta(days=7),min_value=date.today(),key="exam_date")
    daily_hours=st.slider("⏱️ Daily study hours",1,12,3,key="daily_hours")
    st.divider()
    st.markdown("### Pipeline")
    for item in ["Upload PDFs","Extract text","Analyze patterns","Predict questions","Build roadmap","Practice MCQs","Export PDFs"]:
        st.write("✓ "+item)
    st.divider()
    st.caption("🔐 PDFs are processed in the current session. This app does not save uploaded files to a database.")

if st.session_state.analysis_subject and st.session_state.analysis_subject != subject:
    st.session_state.analysis=None; st.session_state.paper_meta=[]; st.session_state.raw_text=""; st.session_state.mcqs=None; st.session_state.upload_signature=""
st.session_state.analysis_subject=subject

# ---------- Header ----------
st.markdown('''<div class="hero"><h1>🎯 ExamLens AI</h1><p>Turn previous-year papers into a focused, evidence-based study plan.</p><span class="pill">⚡ Groq + Llama</span><span class="pill">📄 Multi-PDF</span><span class="pill">📊 Topic Patterns</span><span class="pill">🎯 Predictions</span><span class="pill">🗺️ 7-Day Plan</span><span class="pill">📝 MCQs</span></div>''',unsafe_allow_html=True)

# ---------- Upload ----------
st.subheader("📄 Upload previous-year papers")
files=st.file_uploader("Upload selectable-text PDFs",type=["pdf"],accept_multiple_files=True,
                       help="Best results come from clear selectable-text PDFs from the same subject. Scanned PDFs may need OCR.")
if files:
    sig=file_signature(files)
    if sig != st.session_state.upload_signature:
        st.session_state.analysis=None; st.session_state.paper_meta=[]; st.session_state.raw_text=""; st.session_state.mcqs=None; st.session_state.upload_signature=sig
    st.success(f"{len(files)} paper(s) selected: "+", ".join(f.name for f in files))
    with st.expander("📁 Uploaded papers",expanded=False):
        for i,f in enumerate(files,1):
            st.write(f"**{i}. {f.name}** · {fmt_num(getattr(f,'size',0)/1024)} KB")

c1,c2,c3=st.columns([2,1,1])
with c1:
    analyze=st.button("🔍 Analyze papers",type="primary",disabled=not files,use_container_width=True)
with c2:
    if st.session_state.analysis and st.button("🧹 Clear analysis",use_container_width=True):
        st.session_state.analysis=None; st.session_state.paper_meta=[]; st.session_state.raw_text=""; st.session_state.mcqs=None; st.rerun()
with c3:
    if st.session_state.analysis:
        st.download_button("⬇️ JSON report",analysis_json(st.session_state.analysis),"examlens_analysis.json","application/json",use_container_width=True)

# ---------- Analysis ----------
if analyze:
    try:
        with st.status("Running ExamLens AI pipeline…",expanded=True) as status:
            st.write("1/2 • Extracting text from uploaded PDFs…")
            raw,meta=extract_text_from_multiple_pdfs(files)
            st.session_state.raw_text=raw or ""; st.session_state.paper_meta=meta or []
            readable=sum(1 for m in (meta or []) if isinstance(m,dict) and m.get("status")=="ok")
            st.write(f"Readable papers: {readable}/{len(meta or [])}")
            if not raw or not raw.strip() or readable==0:
                status.update(label="No readable PDF text found",state="error")
                st.error("No machine-readable text was found. Upload selectable-text PDFs or add OCR support for scanned papers.")
                st.stop()
            st.write(f"2/2 • Analyzing {subject} with the configured model…")
            data=analyze_all_in_one(raw,subject)
            if not isinstance(data,dict): raise ValueError("The AI analysis returned an invalid response format.")
            st.session_state.analysis=data; st.session_state.mcqs=None; st.session_state.analysis_runs+=1
            if data.get("analysis_status")=="success": status.update(label="Analysis complete",state="complete")
            else:
                status.update(label="Analysis returned an error",state="error")
                st.error(str(data.get("error","The model could not complete the analysis.")))
    except Exception as exc:
        st.session_state.analysis=None
        st.error(f"Analysis failed: {exc}")

# ---------- Results ----------
d=st.session_state.analysis
if d and d.get("analysis_status")=="success":
    tf=d.get("topic_frequency") or {}; hp=as_list(d.get("high_priority_topics",[])); mp=as_list(d.get("medium_priority_topics",[])); lp=as_list(d.get("low_priority_topics",[]))
    qmap=normalize_questions(d.get("extracted_questions")); roadmap=as_list(d.get("roadmap",[])); formulas=as_list(d.get("key_formulas",[]))
    p10=as_list(d.get("predicted_10mark",[])); p2=as_list(d.get("predicted_2mark",[])); diff=d.get("difficulty_distribution") or {}
    qdf=questions_dataframe(qmap)
    total_chars=sum(safe_int(m.get("characters",0)) for m in st.session_state.paper_meta if isinstance(m,dict))
    total_questions=safe_int(d.get("total_questions_analyzed",question_count(qmap)),question_count(qmap))

    st.markdown('<div class="notice">✅ <b>Evidence-first result:</b> topic frequency and priorities are derived from extracted paper text; predictions are forecasts, not guarantees.</div>',unsafe_allow_html=True)
    cols=st.columns(5)
    for col,(n,label) in zip(cols,[(len(files) if files else len(st.session_state.paper_meta),"Papers"),(total_questions,"Questions"),(len(tf),"Topics"),(len(hp),"High priority"),(total_chars,"Extracted chars")]):
        with col: st.markdown(f'<div class="card metric"><div class="n">{fmt_num(n)}</div><div class="l">{esc(label)}</div></div>',unsafe_allow_html=True)

    days_left=max((exam_date-date.today()).days,0)
    x,y,z=st.columns(3)
    with x: st.metric("🗓️ Days remaining",days_left)
    with y: st.metric("⏱️ Daily target",f"{daily_hours} h")
    with z: st.metric("🎯 High-priority topics",len(hp))
    st.progress(max(0,min(1,1-days_left/7)),text=f"Revision countdown: {days_left} day(s) remaining")

    st.markdown("### Results")
    tabs=st.tabs(["📊 Patterns","🎯 Predictions","🗺️ Roadmap","📐 Formulas","📝 MCQs","📋 Questions","📄 Paper Text","📥 Export"])

    with tabs[0]:
        if tf:
            freq_df=pd.DataFrame({"Topic":[str(k) for k in tf.keys()],"Frequency":[safe_int(v) for v in tf.values()]}).sort_values("Frequency",ascending=False)
            st.dataframe(freq_df,use_container_width=True,hide_index=True)
            fig=px.bar(freq_df.head(15),x="Topic",y="Frequency",text="Frequency",title=f"Top recurring topics — {subject}")
            chart_layout(fig,height=430); fig.update_xaxes(tickangle=-30); st.plotly_chart(fig,use_container_width=True)
            pareto=freq_df.copy(); total=max(pareto.Frequency.sum(),1); pareto["Cumulative %"]=pareto.Frequency.cumsum()/total*100
            figp=go.Figure(); figp.add_bar(x=pareto.Topic.head(12),y=pareto.Frequency.head(12),name="Frequency"); figp.add_scatter(x=pareto.Topic.head(12),y=pareto["Cumulative %"].head(12),name="Cumulative %",mode="lines+markers",yaxis="y2")
            figp.update_layout(yaxis=dict(title="Frequency",gridcolor=CHART_GRID),yaxis2=dict(title="Cumulative %",overlaying="y",side="right",range=[0,110],gridcolor=CHART_GRID)); chart_layout(figp,"Topic concentration",400); st.plotly_chart(figp,use_container_width=True)
            st.download_button("⬇️ Topic frequency CSV",freq_df.to_csv(index=False),"examlens_topic_frequency.csv","text/csv")
        else: st.info("No reliable topic-frequency data was returned.")
        a,b=st.columns(2)
        with a:
            st.markdown("#### 🔥 Priority map")
            for t in hp: st.markdown(f'<div class="priority">🔥 <b>High</b> · {esc(t)}</div>',unsafe_allow_html=True)
            for t in mp: st.markdown(f'<div class="priority">🟡 <b>Medium</b> · {esc(t)}</div>',unsafe_allow_html=True)
            for t in lp: st.markdown(f'<div class="priority">🟢 <b>Low</b> · {esc(t)}</div>',unsafe_allow_html=True)
        with b:
            if diff:
                diff_df=pd.DataFrame({"Difficulty":list(diff.keys()),"Count":[safe_int(v) for v in diff.values()]})
                fig2=px.bar(diff_df,x="Count",y="Difficulty",orientation="h",text="Count",title="Difficulty distribution"); chart_layout(fig2,height=320); st.plotly_chart(fig2,use_container_width=True)
            else: st.info("No difficulty distribution was returned.")
        with st.expander("📄 Paper extraction quality"):
            if st.session_state.paper_meta: st.dataframe(pd.DataFrame(st.session_state.paper_meta),use_container_width=True,hide_index=True)

    with tabs[1]:
        ptype=st.radio("Prediction type",["All","Long-answer","Short-answer"],horizontal=True,key="prediction_filter")
        if ptype in ("All","Long-answer"):
            st.markdown("#### 🎯 Longer-answer predictions")
            for i,q in enumerate(p10,1): st.markdown(f'<div class="pred"><b>{i}.</b> {esc(clean_question(q))}</div>',unsafe_allow_html=True)
        if ptype in ("All","Short-answer"):
            st.markdown("#### ⚡ Short-answer predictions")
            for i,q in enumerate(p2,1): st.markdown(f'<div class="pred"><b>{i}.</b> {esc(clean_question(q))}</div>',unsafe_allow_html=True)
        if d.get("wildcard_question"): st.warning(f"Wildcard: {d.get('wildcard_question')}\n\nReason: {d.get('wildcard_reason','Pattern-based uncertainty.')}")
        st.caption("Predictions are revision priorities, not guaranteed questions.")
        st.download_button("⬇️ Export predictions PDF",generate_predictions_pdf(prediction_text(d),subject),"examlens_predictions.pdf","application/pdf")

    with tabs[2]:
        if not roadmap: st.info("No roadmap was returned.")
        completed=0
        for idx,day in enumerate(roadmap,1):
            if not isinstance(day,dict): day={"day":idx,"topic":str(day),"tasks":[]}
            dayno=safe_int(day.get("day"),idx); done=st.checkbox(f"Day {dayno} complete",key=f"roadmap_done_{dayno}")
            if done: completed+=1
            st.markdown(f'<div class="day"><b>Day {dayno} • {esc(day.get("hours",daily_hours))} hours</b><br><strong>{esc(day.get("topic",""))}</strong><br><span style="color:{MUTED}">{esc(day.get("focus",""))}</span><br><br>{" • ".join(esc(x) for x in as_list(day.get("tasks",[])))}<br><small>💡 {esc(day.get("tip",""))}</small></div>',unsafe_allow_html=True)
        if roadmap: st.progress(completed/len(roadmap),text=f"Roadmap progress: {completed}/{len(roadmap)} days complete")
        tips=as_list(d.get("quick_tips",[]))
        if tips:
            st.markdown("#### 💡 Exam tips")
            for tip in tips: st.info(str(tip))
        st.download_button("⬇️ Export roadmap PDF",generate_roadmap_pdf(roadmap_text(roadmap),subject),"examlens_roadmap.pdf","application/pdf")

    with tabs[3]:
        if formulas:
            fs=st.text_input("🔎 Search formulas / definitions",key="formula_search",placeholder="Search a concept…")
            shown=[f for f in formulas if not fs or fs.lower() in str(f).lower()]
            st.caption(f"Showing {len(shown)} of {len(formulas)} items")
            for i,f in enumerate(shown,1): st.markdown(f'<div class="formula">📐 <b>{i}.</b> {esc(f)}</div>',unsafe_allow_html=True)
        else: st.info("No formulas or definitions were returned.")

    with tabs[4]:
        if not hp: st.info("Run an analysis with at least one detected topic first.")
        else:
            topic=st.selectbox("Topic",[str(x) for x in hp],key="mcq_topic_select")
            n=st.slider("Number of MCQs",3,15,5,key="mcq_count")
            c1,c2=st.columns(2)
            with c1:
                if st.button("🎲 Generate MCQs",key="generate_mcqs",type="primary"):
                    with st.spinner("Generating targeted MCQs…"):
                        try:
                            st.session_state.mcqs=generate_mcqs(subject,topic,n); st.session_state.mcq_topic_name=topic
                        except Exception as exc: st.error(f"MCQ generation failed: {exc}")
            with c2:
                if st.session_state.mcqs and st.button("🧹 Clear MCQs",key="clear_mcqs"): st.session_state.mcqs=None; st.rerun()
            if st.session_state.mcqs:
                st.markdown("#### Practice set"); st.markdown(str(st.session_state.mcqs))
                st.download_button("⬇️ Export MCQs PDF",generate_mcq_pdf(st.session_state.mcqs,st.session_state.get("mcq_topic_name",topic)),"examlens_mcqs.pdf","application/pdf")

    with tabs[5]:
        if not qmap: st.info("No questions were extracted.")
        else:
            st.markdown("#### 📋 Extracted questions")
            st.caption(f"{question_count(qmap)} questions across {len(qmap)} paper(s)")
            qsearch=st.text_input("🔎 Search extracted questions",key="question_search",placeholder="Search a keyword or concept…")
            paper_filter=st.selectbox("Filter by paper",["All papers"]+list(qmap.keys()),key="question_paper_filter")
            shown=qdf.copy()
            if qsearch: shown=shown[shown["Question"].str.contains(qsearch,case=False,regex=False,na=False)]
            if paper_filter!="All papers": shown=shown[shown["Paper"]==paper_filter]
            st.caption(f"Showing {len(shown)} question(s)")
            st.dataframe(shown,use_container_width=True,hide_index=True,height=430)
            st.download_button("⬇️ Questions CSV",qdf.to_csv(index=False),"examlens_questions.csv","text/csv")
            with st.expander("📖 Paper-wise readable view"):
                for paper,qs in qmap.items():
                    st.markdown(f"**{esc(paper)}**")
                    for i,q in enumerate(qs,1): st.markdown(f"{i}. {esc(q)}")
            st.download_button("⬇️ Extracted questions PDF",generate_extracted_questions_pdf(question_text(qmap),subject),"examlens_extracted_questions.pdf","application/pdf")

    with tabs[6]:
        raw=st.session_state.raw_text or ""
        if not raw: st.info("Raw extracted text is not available in this session.")
        else:
            st.markdown("#### 📄 Extracted source text")
            st.caption(f"{fmt_num(len(raw))} characters • Verify what the AI received before relying on predictions.")
            limit=st.slider("Preview length",2000,min(max(len(raw),2000),30000),min(max(len(raw),2000),10000),1000,key="raw_preview_limit")
            st.text_area("Source text preview",raw[:limit],height=480,key="raw_text_preview")
            st.download_button("⬇️ Download extracted text",raw,"examlens_extracted_text.txt","text/plain")

    with tabs[7]:
        st.markdown("#### 📥 Export center")
        e1,e2=st.columns(2)
        with e1:
            st.download_button("⬇️ Complete analysis JSON",analysis_json(d),"examlens_complete_analysis.json","application/json",use_container_width=True)
            st.download_button("⬇️ Predictions PDF",generate_predictions_pdf(prediction_text(d),subject),"examlens_predictions.pdf","application/pdf",use_container_width=True)
            st.download_button("⬇️ Roadmap PDF",generate_roadmap_pdf(roadmap_text(roadmap),subject),"examlens_roadmap.pdf","application/pdf",use_container_width=True)
        with e2:
            if st.session_state.mcqs:
                st.download_button("⬇️ MCQs PDF",generate_mcq_pdf(st.session_state.mcqs,st.session_state.get("mcq_topic_name","Practice")),"examlens_mcqs.pdf","application/pdf",use_container_width=True)
            if qmap:
                st.download_button("⬇️ Questions PDF",generate_extracted_questions_pdf(question_text(qmap),subject),"examlens_extracted_questions.pdf","application/pdf",use_container_width=True)
                st.download_button("⬇️ Questions CSV",qdf.to_csv(index=False),"examlens_questions.csv","text/csv",use_container_width=True)
            st.download_button("⬇️ Extracted text TXT",st.session_state.raw_text or "","examlens_extracted_text.txt","text/plain",use_container_width=True)
        st.divider()
        st.markdown("#### 📊 Analysis summary")
        st.json({"project":"ExamLens AI","subject":subject,"papers":len(files) if files else len(st.session_state.paper_meta),"questions":total_questions,"topics":len(tf),"high_priority_topics":hp,"medium_priority_topics":mp,"low_priority_topics":lp,"exam_date":str(exam_date),"days_remaining":days_left,"daily_study_hours":daily_hours,"analysis_runs":st.session_state.analysis_runs})

else:
    st.markdown("### How ExamLens AI works")
    cards=[("1 • Upload","Add previous-year papers for one subject."),("2 • Extract","Read paper text and validate extraction quality."),("3 • Analyze","Detect recurring concepts and difficulty patterns."),("4 • Predict","Generate evidence-based short and long questions."),("5 • Prepare","Build a roadmap, formulas and targeted MCQs."),("6 • Export","Download PDFs, CSV data and JSON analysis.")]
    cols=st.columns(3)
    for i,(title,body) in enumerate(cards):
        with cols[i%3]: st.markdown(f'<div class="card"><h4>{esc(title)}</h4><p style="color:{MUTED} !important">{esc(body)}</p></div>',unsafe_allow_html=True)
    st.info("💡 For the most reliable analysis, upload clear selectable-text PDFs from the same subject. Scanned/image-only papers may require OCR.")
