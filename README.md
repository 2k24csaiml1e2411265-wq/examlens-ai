---
title: ExamLens AI
emoji: 🎯
colorFrom: purple
colorTo: blue
sdk: streamlit
sdk_version: "1.35.0"
python_version: "3.10"
app_file: app.py
pinned: false
---

# 🎯 ExamLens AI — Exam Paper Analyzer & Question Predictor

> Upload previous year B.Tech papers → AI detects patterns → Study smarter, not harder.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 What It Does

| Feature | Description |
|---|---|
| 📊 Topic Heatmap | Visual chart of which topics repeat most |
| 🎯 Predicted Questions | AI-predicted 10-mark & 2-mark questions |
| 🗺️ Study Roadmap | Personalized 7-day revision plan with daily tasks |
| 📐 Key Formulas | Most important formulas to memorize |
| 📝 MCQ Practice | AI-generated MCQs with answers |
| 📄 PDF Export | Download all outputs as PDF |

## ⚡ Why Groq?
- **14,400 free requests/day** — 10x more than Gemini
- **Responses in under 3 seconds** — fastest AI API available
- **Llama 3.3 70B** — highly capable open source model
- Get free key at: [console.groq.com](https://console.groq.com)

## 🛠 Tech Stack
- **AI:** Groq Llama 3.3 70B
- **Frontend:** Streamlit
- **PDF Parsing:** pdfplumber
- **Charts:** Plotly
- **PDF Export:** reportlab

## ▶️ Run Locally
```bash
git clone https://github.com/YOUR_USERNAME/examlens-ai
cd examlens-ai
pip install -r requirements.txt
# Add to .env: GROQ_API_KEY=gsk_...
streamlit run app.py
```

## 🔑 Get Free Groq API Key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up free with Google/GitHub
3. Click **API Keys** → **Create API key**
4. Key starts with `gsk_...`

## 👨‍💻 Built By
Yash Kushwaha — B.Tech AIML, PSIT

## 📄 License
MIT License
