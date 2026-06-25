import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pdf_utils import extract_text_from_multiple_pdfs
from gemini_helper import analyze_all_in_one, generate_mcqs
from pdf_generator import (
    generate_predictions_pdf, generate_roadmap_pdf,
    generate_mcq_pdf, generate_extracted_questions_pdf,
)

st.set_page_config(page_title="ExamLens AI", page_icon="🎯",
                   layout="wide", initial_sidebar_state="expanded")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
dm = st.session_state.dark_mode

if dm:
    BG="#0e0e1a";BG2="#16162a";BG3="#1e1e36";CARD="#1a1a30";BORDER="#2d2d55"
    TEXT="#e8e8f8";TEXT2="#9898bb";ACCENT="#7c6ff7";ACCENT2="#5a4fcf"
    SUCCESS="#10b981";INFO="#3b82f6";WARN="#f59e0b"
    PH_BG="#1e0a3a";PM_BG="#0a1830";PL_BG="#0a1e18"
    PH_TX="#ccc5ff";PM_TX="#b8d4ff";PL_TX="#a7f3d0"
    TIP_BG="#0a1a0a";TIP_BD="#14401a";TIP_TX="#86efac"
    FORM_BG="#0f1a2e";FORM_BD="#1a3050";FORM_TX="#90c8f8"
    PBG=BG;PPA=BG;PFC="#c0c0e0";PGC="#1e1e3a"
    HBG="linear-gradient(135deg,#0f0c29,#302b63,#24243e)"
    HSUB="#a0a8c0";MOON="☀️";MLBL="Switch to Light Mode"
    DAY_C=["#7c6ff7","#6b5ed6","#5a4fcf","#4a3fb8","#3a30a0","#2d2480","#1e1860"]
else:
    BG="#f5f5ff";BG2="#ffffff";BG3="#ededfa";CARD="#ffffff";BORDER="#d0d0e8"
    TEXT="#1a1a3a";TEXT2="#5a5a88";ACCENT="#5a4fcf";ACCENT2="#4338ca"
    SUCCESS="#059669";INFO="#2563eb";WARN="#d97706"
    PH_BG="#f0eeff";PM_BG="#eff6ff";PL_BG="#f0fdf4"
    PH_TX="#4c3db8";PM_TX="#1d4ed8";PL_TX="#065f46"
    TIP_BG="#f0fdf4";TIP_BD="#bbf7d0";TIP_TX="#065f46"
    FORM_BG="#eff6ff";FORM_BD="#bfdbfe";FORM_TX="#1d4ed8"
    PBG="#ffffff";PPA="#f5f5ff";PFC="#1a1a3a";PGC="#e0e0f0"
    HBG="linear-gradient(135deg,#4338ca,#6d28d9,#7c3aed)"
    HSUB="#ddd8ff";MOON="🌙";MLBL="Switch to Dark Mode"
    DAY_C=["#5a4fcf","#6b5ed6","#7c6ff7","#8b7ef8","#9b8ef9","#a89cff","#b8acff"]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"],.stApp{{font-family:'Inter',sans-serif!important;background-color:{BG}!important;color:{TEXT}!important;}}
section[data-testid="stSidebar"]>div{{background-color:{BG2}!important;border-right:1px solid {BORDER}!important;}}
section[data-testid="stSidebar"] *{{color:{TEXT}!important;}}
.block-container{{padding-top:1.5rem!important;background-color:{BG}!important;}}
.main-header{{background:{HBG};border-radius:20px;padding:2.5rem 2rem;margin-bottom:2rem;text-align:center;box-shadow:0 8px 32px rgba(124,111,247,0.18);}}
.main-header h1{{color:#fff;font-size:2.8rem;font-weight:700;margin:0 0 0.4rem;letter-spacing:-1px;}}
.main-header p{{color:{HSUB};font-size:1rem;margin:0;}}
.accent{{color:#a89cff;}}
.badge-row{{display:flex;justify-content:center;gap:8px;margin-top:1rem;flex-wrap:wrap;}}
.hbadge{{background:rgba(255,255,255,0.12);color:#fff;border:1px solid rgba(255,255,255,0.2);border-radius:20px;padding:4px 12px;font-size:0.78rem;font-weight:500;}}
.metric-card{{background:{CARD};border:1px solid {BORDER};border-radius:16px;padding:1.3rem 1rem;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.08);transition:transform .2s;}}
.metric-card:hover{{transform:translateY(-2px);}}
.metric-card .val{{font-size:2.2rem;font-weight:700;color:{ACCENT};line-height:1;margin-bottom:4px;}}
.metric-card .lbl{{font-size:0.75rem;color:{TEXT2};text-transform:uppercase;letter-spacing:0.08em;}}
.section-header{{font-size:1.1rem;font-weight:600;color:{TEXT};margin:1.6rem 0 0.9rem;padding-bottom:0.5rem;border-bottom:2px solid {ACCENT};display:inline-block;}}
.priority-high{{background:{PH_BG};border-left:4px solid {ACCENT};border-radius:0 10px 10px 0;padding:0.75rem 1rem;margin-bottom:8px;font-size:0.88rem;color:{PH_TX};font-weight:500;transition:transform .15s;}}
.priority-high:hover{{transform:translateX(4px);}}
.priority-medium{{background:{PM_BG};border-left:4px solid {INFO};border-radius:0 10px 10px 0;padding:0.75rem 1rem;margin-bottom:8px;font-size:0.88rem;color:{PM_TX};font-weight:500;}}
.priority-low{{background:{PL_BG};border-left:4px solid {SUCCESS};border-radius:0 10px 10px 0;padding:0.75rem 1rem;margin-bottom:8px;font-size:0.88rem;color:{PL_TX};font-weight:500;}}
.tip-box{{background:{TIP_BG};border:1px solid {TIP_BD};border-radius:12px;padding:1rem 1.2rem;color:{TIP_TX};font-size:0.88rem;margin-top:1rem;line-height:1.6;}}
.formula-card{{background:{FORM_BG};border:1px solid {FORM_BD};border-radius:10px;padding:0.8rem 1rem;margin-bottom:8px;font-family:monospace;font-size:0.92rem;color:{FORM_TX};}}
.upload-hint{{background:{BG3};border:2px dashed {BORDER};border-radius:16px;padding:0.8rem 1.2rem;color:{TEXT2};font-size:0.88rem;margin-bottom:0.6rem;text-align:center;}}
.step-card{{background:{CARD};border:1px solid {BORDER};border-radius:16px;padding:1.4rem 1.2rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);}}
.step-num{{width:40px;height:40px;background:{ACCENT};color:#fff;border-radius:50%;font-size:1.1rem;font-weight:700;display:flex;align-items:center;justify-content:center;margin:0 auto 0.8rem;}}
.step-title{{font-size:0.95rem;font-weight:600;color:{TEXT};margin-bottom:6px;}}
.step-sub{{font-size:0.82rem;color:{TEXT2};line-height:1.5;}}
.day-card{{background:{CARD};border:1px solid {BORDER};border-radius:14px;padding:1rem 1.1rem;margin-bottom:10px;border-left:4px solid {ACCENT};transition:transform .15s;}}
.day-card:hover{{transform:translateX(3px);}}
.day-label{{font-size:0.72rem;font-weight:700;color:{ACCENT};text-transform:uppercase;letter-spacing:0.1em;margin-bottom:3px;}}
.day-topic{{font-size:1rem;font-weight:600;color:{TEXT};margin-bottom:3px;}}
.day-focus{{font-size:0.84rem;color:{TEXT2};margin-bottom:6px;}}
.day-tasks{{font-size:0.8rem;color:{TEXT2};margin-bottom:6px;padding-left:4px;}}
.day-tip{{font-size:0.78rem;color:{TIP_TX};background:{TIP_BG};border-radius:6px;padding:3px 8px;display:inline-block;}}
.pred-card{{background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:0.9rem 1.1rem;margin-bottom:8px;display:flex;align-items:flex-start;gap:10px;}}
.pred-num{{min-width:26px;height:26px;background:{ACCENT};color:#fff;border-radius:50%;font-size:0.75rem;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;}}
.pred-text{{font-size:0.9rem;color:{TEXT};line-height:1.5;}}
.marks-badge{{display:inline-block;font-size:0.7rem;padding:2px 8px;border-radius:20px;font-weight:600;margin-bottom:6px;}}
.badge-10{{background:{PH_BG};color:{PH_TX};}}
.badge-2{{background:{PM_BG};color:{PM_TX};}}
.quota-box{{background:{BG3};border:1px solid {BORDER};border-radius:10px;padding:0.7rem 1rem;font-size:0.82rem;color:{TEXT2};margin-top:0.5rem;}}
.stButton>button{{background:linear-gradient(135deg,{ACCENT},{ACCENT2})!important;color:#fff!important;border:none!important;border-radius:12px!important;padding:0.65rem 1.5rem!important;font-weight:600!important;font-size:0.95rem!important;width:100%!important;box-shadow:0 4px 14px rgba(124,111,247,0.35)!important;transition:opacity .2s,transform .15s!important;}}
.stButton>button:hover{{opacity:0.9!important;transform:translateY(-1px)!important;}}
.mode-btn>button{{background:transparent!important;border:1.5px solid {BORDER}!important;color:{TEXT}!important;box-shadow:none!important;border-radius:10px!important;font-size:0.88rem!important;padding:0.45rem 1rem!important;}}
.mode-btn>button:hover{{background:{BG3}!important;border-color:{ACCENT}!important;transform:none!important;box-shadow:none!important;}}
.stTabs [data-baseweb="tab-list"]{{background:{BG2}!important;border-radius:12px!important;padding:4px!important;border:1px solid {BORDER}!important;}}
.stTabs [data-baseweb="tab"]{{border-radius:10px!important;font-weight:500!important;color:{TEXT2}!important;padding:0.4rem 0.9rem!important;}}
.stTabs [aria-selected="true"]{{background:{ACCENT}!important;color:#fff!important;}}
div[data-testid="stExpander"]{{background:{CARD}!important;border:1px solid {BORDER}!important;border-radius:12px!important;margin-bottom:8px!important;}}
.stSelectbox>div>div,.stTextArea>div>div>textarea{{background:{BG2}!important;border-color:{BORDER}!important;color:{TEXT}!important;border-radius:10px!important;}}
.stFileUploader>div{{background:{BG2}!important;border:2px dashed {BORDER}!important;border-radius:16px!important;}}
hr{{border-color:{BORDER}!important;}}
.sidebar-footer{{font-size:0.76rem;color:{TEXT2};text-align:center;padding-top:0.5rem;border-top:1px solid {BORDER};margin-top:0.5rem;line-height:1.6;}}
.tech-pill{{display:inline-flex;align-items:center;gap:5px;background:{BG3};border:1px solid {BORDER};border-radius:20px;padding:4px 10px;font-size:0.78rem;color:{TEXT2};margin:2px 3px 2px 0;}}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.2rem;">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,{ACCENT},{ACCENT2});border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.2rem;">🎯</div>
        <div>
            <div style="font-size:1.1rem;font-weight:700;color:{TEXT};">ExamLens AI</div>
            <div style="font-size:0.75rem;color:{TEXT2};">Powered by Groq Llama 3.3</div>
        </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f"**{MOON} Display Mode**")
    st.markdown('<div class="mode-btn">', unsafe_allow_html=True)
    if st.button(f"{MOON}  {MLBL}", key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**📚 Select Subject**")
    subject = st.selectbox("Subject", [
        # Engineering Core
        "Engineering Mathematics",
        "Engineering Physics",
        "Engineering Chemistry",
        # CSE / AIML
        "AIML / Machine Learning",
        "Deep Learning",
        "NLP (Natural Language Processing)",
        "Computer Vision",
        "Data Structures & Algorithms",
        "DBMS (Database Management)",
        "Operating Systems",
        "Artificial Intelligence",
        "Computer Networks",
        "Software Engineering",
        "Theory of Computation",
        "Compiler Design",
        "Digital Electronics",
        "Microprocessor & Microcontroller",
        "Object Oriented Programming",
        "Web Technologies",
        # Other
        "Other",
    ], label_visibility="collapsed")
    st.markdown("---")

    st.markdown("**⚡ How it works**")
    for num, text in [
        ("1","Upload previous year PDFs"),
        ("2","1 AI call analyzes everything"),
        ("3","Topic heatmap + priorities"),
        ("4","Predicted exam questions"),
        ("5","7-day study roadmap"),
        ("6","Key formulas to memorize"),
        ("7","MCQ practice by topic"),
    ]:
        st.markdown(f"""<div style="display:flex;align-items:center;gap:8px;padding:4px 0;font-size:0.82rem;color:{TEXT2};">
            <div style="width:20px;height:20px;min-width:20px;background:{BG3};border:1.5px solid {ACCENT};border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.68rem;font-weight:700;color:{ACCENT};">{num}</div>
            <span>{text}</span></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""<div class="quota-box">
    ⚡ <b>Groq Free Tier:</b> 14,400 requests/day<br>
    Only <b>1 API call</b> per full analysis<br>
    MCQs = 1 call per topic<br>
    Get key free: <b>console.groq.com</b>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""<div class="sidebar-footer">
        Built with ❤️ by Yash Kushwaha — AIML PSIT<br>
        No data stored · Real-time AI processing
    </div>""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <h1>🎯 Exam<span class="accent">Lens</span> AI</h1>
    <p>Upload previous year papers → AI detects patterns → Study smarter, not harder</p>
    <div class="badge-row">
        <span class="hbadge">⚡ Groq Llama 3.3 — Ultra Fast</span>
        <span class="hbadge">🆓 14,400 Free Calls/Day</span>
        <span class="hbadge">📄 PDF Upload</span>
        <span class="hbadge">🎯 Question Prediction</span>
        <span class="hbadge">🗺️ Study Roadmap</span>
        <span class="hbadge">📐 Key Formulas</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Upload ────────────────────────────────────────────────────
st.markdown("### 📄 Upload Your Exam Papers")
st.markdown('<div class="upload-hint">💡 Upload 2–5 previous year PDFs — everything analyzed in a single AI call</div>',
            unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Drop PDFs here", type=["pdf"],
    accept_multiple_files=True, label_visibility="collapsed"
)
if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} paper(s) ready — {', '.join([f.name for f in uploaded_files])}")

col_btn, _ = st.columns([2, 3])
with col_btn:
    analyze_btn = st.button("🔍  Analyze Papers", disabled=not uploaded_files)

for key, val in [("done",False),("data",{}),("sn",subject),("last_subject","")]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── Clear stale results when subject changes ──────────────────
if st.session_state.last_subject != subject:
    st.session_state.done = False
    st.session_state.data = {}
    st.session_state.sn = subject
    st.session_state.last_subject = subject
    # clear MCQ cache too
    for k in ["mcqs", "mcq_topic"]:
        if k in st.session_state:
            del st.session_state[k]

# ── Analysis ──────────────────────────────────────────────────
if analyze_btn and uploaded_files:
    try:
        prog = st.progress(0, text=f"📄 Reading your {subject} exam papers...")
        raw_text = extract_text_from_multiple_pdfs(uploaded_files)
        if not raw_text.strip():
            st.error("❌ Could not read text from PDFs. Make sure they are not scanned images.")
            st.stop()
        prog.progress(25, text=f"⚡ Analyzing {subject} patterns with Groq AI...")
        data = analyze_all_in_one(raw_text, subject)
        st.session_state.data = data
        st.session_state.sn = subject   # always use selected subject, not AI guess
        st.session_state.last_subject = subject
        st.session_state.done = True
        prog.progress(100, text="✅ Done! 1 API call used.")
        st.success(f"🎉 {subject} analysis complete! Just 1 API call used out of your 14,400 daily limit.")
        st.balloons()
    except Exception as e:
        st.error(f"❌ {str(e)}")

# ── Results ───────────────────────────────────────────────────
if st.session_state.done:
    d  = st.session_state.data
    sn = st.session_state.sn
    tf = d.get("topic_frequency", {})
    hp = d.get("high_priority_topics", [])
    mp = d.get("medium_priority_topics", [])
    lp = d.get("low_priority_topics", [])
    qt = d.get("extracted_questions", "")
    rm = d.get("roadmap", [])
    kf = d.get("key_formulas", [])

    c1,c2,c3,c4 = st.columns(4)
    for col,val,lbl in [
        (c1, str(len(uploaded_files)), "Papers Analyzed"),
        (c2, str(d.get("total_questions_analyzed","?")), "Questions Found"),
        (c3, str(len(tf)), "Unique Topics"),
        (c4, str(len(hp)), "🔥 Hot Topics"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>',
                        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
        "📊 Heatmap","🎯 Predictions",
        "🗺️ Roadmap","📐 Formulas",
        "📝 MCQs","📋 Questions"
    ])

    # ── TAB 1: Heatmap ───────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-header">📊 Topic Frequency Heatmap</div>', unsafe_allow_html=True)
        st.caption("Taller bar = more repeated = study this first!")
        if tf:
            df = pd.DataFrame(list(tf.items()),columns=["Topic","Frequency"]).sort_values("Frequency",ascending=False)
            bc = ["#1a1a4e","#3a2d9e","#5a4fcf","#7c6ff7","#a89cff"] if dm else ["#c7d2fe","#a5b4fc","#818cf8","#6366f1","#4f46e5"]
            fig = px.bar(df,x="Topic",y="Frequency",color="Frequency",
                         color_continuous_scale=bc,title=f"Topic Frequency — {sn}",text="Frequency")
            fig.update_traces(textposition="outside",marker_line_width=0)
            fig.update_layout(plot_bgcolor=PBG,paper_bgcolor=PPA,font_color=PFC,
                              xaxis=dict(tickangle=-30,gridcolor=PGC,title=""),
                              yaxis=dict(gridcolor=PGC,title="Times Asked"),
                              coloraxis_showscale=False,margin=dict(t=55,b=90,l=50,r=20),height=380)
            st.plotly_chart(fig,use_container_width=True)

        col1,col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header">🔥 Priority Breakdown</div>', unsafe_allow_html=True)
            st.markdown(f"<small style='color:{TEXT2}'>🔴 High — study first</small>", unsafe_allow_html=True)
            for t in hp:
                st.markdown(f'<div class="priority-high">🎯 &nbsp;{t}</div>', unsafe_allow_html=True)
            st.markdown(f"<small style='color:{TEXT2}'>🟡 Medium</small>", unsafe_allow_html=True)
            for t in mp:
                st.markdown(f'<div class="priority-medium">📌 &nbsp;{t}</div>', unsafe_allow_html=True)
            st.markdown(f"<small style='color:{TEXT2}'>🟢 Low</small>", unsafe_allow_html=True)
            for t in lp:
                st.markdown(f'<div class="priority-low">📎 &nbsp;{t}</div>', unsafe_allow_html=True)

        with col2:
            diff = d.get("difficulty_distribution",{})
            if diff:
                st.markdown('<div class="section-header">📏 Question Distribution</div>', unsafe_allow_html=True)
                df2 = pd.DataFrame(list(diff.items()),columns=["Type","Count"])
                fig3 = go.Figure(go.Bar(x=df2["Count"],y=df2["Type"],orientation="h",
                                        marker_color=[SUCCESS,INFO,ACCENT],
                                        text=df2["Count"],textposition="outside"))
                fig3.update_layout(plot_bgcolor=PBG,paper_bgcolor=PPA,font_color=PFC,height=220,
                                   margin=dict(t=10,b=10,l=10,r=40),
                                   xaxis=dict(gridcolor=PGC),yaxis=dict(gridcolor=PGC))
                st.plotly_chart(fig3,use_container_width=True)

    # ── TAB 2: Predictions ───────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">🎯 AI-Predicted Questions</div>', unsafe_allow_html=True)
        st.caption("Based on pattern detection — included in your 1 API call, no extra quota used!")

        p10 = d.get("predicted_10mark",[])
        p2  = d.get("predicted_2mark",[])
        wq  = d.get("wildcard_question","")
        wr  = d.get("wildcard_reason","")

        if p10:
            st.markdown(f'<span class="marks-badge badge-10">10-MARK QUESTIONS — 15 marks each</span>', unsafe_allow_html=True)
            for i,q in enumerate(p10):
                st.markdown(f'<div class="pred-card"><div class="pred-num">{i+1}</div><div class="pred-text">{q}</div></div>',
                            unsafe_allow_html=True)

        if p2:
            st.markdown(f"<br>", unsafe_allow_html=True)
            st.markdown(f'<span class="marks-badge badge-2">2-MARK QUESTIONS — 2 marks each</span>', unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            for i,q in enumerate(p2):
                with (c1 if i%2==0 else c2):
                    st.markdown(f'<div class="pred-card"><div class="pred-num">{i+1}</div><div class="pred-text">{q}</div></div>',
                                unsafe_allow_html=True)

        if wq:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<span class="marks-badge" style="background:{FORM_BG};color:{FORM_TX};">⚠️ WILDCARD QUESTION</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="pred-card" style="border-left:4px solid {WARN};">'
                        f'<div class="pred-text">🎲 {wq}<br><small style="color:{TEXT2};">Why: {wr}</small></div></div>',
                        unsafe_allow_html=True)

        pred_text = "## Top 10-Mark Questions\n"
        for i,q in enumerate(p10): pred_text += f"{i+1}. {q}\n"
        pred_text += "\n## Top 2-Mark Questions\n"
        for i,q in enumerate(p2): pred_text += f"{i+1}. {q}\n"
        if wq: pred_text += f"\n## Wildcard Question\n- {wq}\n- Why: {wr}\n"

        st.markdown("<br>", unsafe_allow_html=True)
        pdf_bytes = generate_predictions_pdf(pred_text, sn)
        st.download_button("⬇️ Download Predictions PDF", pdf_bytes,
                           file_name="predicted_questions.pdf", mime="application/pdf")
        st.markdown(f'<div class="tip-box">⚡ <b>Strategy:</b> 10-mark questions = 50% of your marks. Prepare 3 detailed answers for each predicted question. Even bullet points with diagrams score well in AKTU.</div>',
                    unsafe_allow_html=True)

    # ── TAB 3: Roadmap ───────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">🗺️ 7-Day Study Roadmap</div>', unsafe_allow_html=True)
        st.caption("Personalized to your paper patterns — included in the 1 API call!")
        if rm:
            for i,day in enumerate(rm):
                color = DAY_C[i % len(DAY_C)]
                tasks_html = "".join(f"<span style='margin-right:12px;'>✓ {t}</span>" for t in day.get("tasks",[]))
                st.markdown(f"""<div class="day-card" style="border-left-color:{color};">
                    <div class="day-label">📅 Day {day.get('day',i+1)} · {day.get('hours',3)} hours</div>
                    <div class="day-topic">{day.get('topic','')}</div>
                    <div class="day-focus">📖 {day.get('focus','')}</div>
                    <div class="day-tasks">{tasks_html}</div>
                    <span class="day-tip">💡 {day.get('tip','')}</span>
                </div>""", unsafe_allow_html=True)

            tips = d.get("quick_tips",[])
            if tips:
                st.markdown(f'<div class="tip-box"><b>⚡ Exam Day Tips</b><br>{"<br>".join(f"• {t}" for t in tips)}</div>',
                            unsafe_allow_html=True)

            rm_text = "## 7-Day Exam Revision Roadmap\n\n"
            for day in rm:
                rm_text += f"**Day {day.get('day','')}: {day.get('topic','')}**\n"
                rm_text += f"Focus: {day.get('focus','')}\n"
                for t in day.get("tasks",[]): rm_text += f"- {t}\n"
                rm_text += f"Tip: {day.get('tip','')}\n\n"
            if tips: rm_text += "## Quick Tips\n" + "\n".join(f"- {t}" for t in tips)

            pdf_bytes = generate_roadmap_pdf(rm_text, sn)
            st.download_button("⬇️ Download Roadmap PDF", pdf_bytes,
                               file_name="study_roadmap.pdf", mime="application/pdf")

    # ── TAB 4: Formulas ──────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-header">📐 Key Formulas & Definitions</div>', unsafe_allow_html=True)
        st.caption("Most important formulas to memorize — generated from your paper patterns!")
        if kf:
            for i,f in enumerate(kf):
                st.markdown(f'<div class="formula-card">📐 {i+1}. &nbsp; {f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="tip-box">💡 <b>Tip:</b> Write these on a sticky note and paste it on your desk. Reading them daily for 7 days = guaranteed recall in the exam hall.</div>',
                        unsafe_allow_html=True)
        else:
            st.info("Run the analysis first to get key formulas for your subject.")

    # ── TAB 5: MCQs ──────────────────────────────────────────
    with tab5:
        st.markdown('<div class="section-header">📝 MCQ Practice</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="tip-box">⚡ Each MCQ set = 1 API call from your 14,400 daily limit. Generate as many as you want!</div>',
                    unsafe_allow_html=True)
        col_t,col_n,col_g = st.columns([2,1,1])
        with col_t:
            sel = st.selectbox("Topic", hp if hp else ["Machine Learning"], label_visibility="visible")
        with col_n:
            num_q = st.slider("Questions", 3, 10, 5)
        with col_g:
            st.markdown("<br>", unsafe_allow_html=True)
            gen = st.button("🎲 Generate MCQs", key="mcq_btn")

        if gen:
            with st.spinner(f"Generating {num_q} MCQs on {sel}..."):
                try:
                    mcqs = generate_mcqs(sel, num_q)
                    st.session_state.mcqs = mcqs
                    st.session_state.mcq_topic = sel
                except Exception as e:
                    st.error(f"❌ {str(e)}")

        if "mcqs" in st.session_state:
            qs = st.session_state.mcqs.strip().split("---")
            for i,q in enumerate(qs):
                if q.strip():
                    with st.expander(f"Question {i+1}", expanded=(i==0)):
                        st.markdown(q.strip())
            pdf_bytes = generate_mcq_pdf(st.session_state.mcqs, st.session_state.get("mcq_topic",sel))
            st.download_button("⬇️ Download MCQs PDF", pdf_bytes,
                               file_name="mcq_practice.pdf", mime="application/pdf")

    # ── TAB 6: All Questions ─────────────────────────────────
    with tab6:
        st.markdown('<div class="section-header">📋 All Extracted Questions</div>', unsafe_allow_html=True)
        st.caption("Every question AI found across your uploaded papers.")
        st.text_area("Questions", qt, height=400, label_visibility="collapsed")
        pdf_bytes = generate_extracted_questions_pdf(qt, sn)
        st.download_button("⬇️ Download Questions PDF", pdf_bytes,
                           file_name="extracted_questions.pdf", mime="application/pdf")

# ── Empty state ───────────────────────────────────────────────
else:
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(3)
    for col,num,title,sub in zip(cols,["1","2","3"],
        ["📄 Upload Papers","⚡ Instant AI Analysis","🎯 Get Everything"],
        ["Upload 2–5 previous year B.Tech exam PDFs from AKTU/HBTU.",
         "Groq Llama 3.3 analyzes everything in under 5 seconds.",
         "Heatmap · Predictions · Roadmap · Formulas · MCQs — all at once."]):
        with col:
            st.markdown(f"""<div class="step-card">
                <div class="step-num">{num}</div>
                <div class="step-title">{title}</div>
                <div class="step-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""<div class="tip-box">
    ⚡ <b>Why Groq?</b> Groq runs Llama 3.3 on custom hardware — responses in under 3 seconds vs 15+ seconds with other APIs.<br>
    🆓 <b>14,400 free requests/day</b> — 10x more than Gemini. Get your free key at <b>console.groq.com</b><br>
    🔒 <b>Privacy:</b> Your PDFs are never stored. All processing happens in real time and is cleared after your session.
    </div>""", unsafe_allow_html=True)
