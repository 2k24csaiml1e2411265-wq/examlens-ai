# 🎯 ExamLens AI

> **AI-powered university exam paper analyzer, question predictor, and personalized study assistant.**

ExamLens AI is a Streamlit-based application that uses **Groq and Llama** to analyze previous-year university examination papers.

The application extracts questions from uploaded PDFs, identifies recurring topics and patterns, generates evidence-based question predictions, creates a personalized 7-day study roadmap, provides MCQ practice, and exports study material as PDFs.

---
## 🚀 Live Demo

[Open ExamLens AI](https://examlens-ai-5abyyua2y9dmmgmltqkyce.streamlit.app/)

---
## ✨ Features

### 📄 Exam Paper Analysis

- Upload multiple previous-year examination papers.
- Extract text from selectable-text PDFs.
- Analyze papers for recurring concepts and question patterns.
- Identify frequently appearing topics.
- Prioritize important topics based on extracted evidence.
- Display extraction statistics and analysis results.

### 🔮 Question Prediction

ExamLens AI uses historical paper patterns to generate:

- High-priority topics
- Likely question areas
- Repeated concepts
- Evidence-based predictions

> Predictions are forecasts based on historical data and should not be treated as guaranteed exam questions.

### 📚 7-Day Study Roadmap

Generate a focused revision plan based on the analyzed topics.

The roadmap helps students:

- Prioritize important concepts
- Organize revision time
- Focus on frequently repeated topics
- Prepare efficiently before examinations

### 📝 MCQ Practice

Generate AI-powered MCQs based on:

- Selected subject
- Selected topic
- Analyzed exam-paper context

This enables targeted practice rather than generic questions.

### 📑 PDF Export

Export generated content as PDFs, including:

- Analysis results
- Study roadmap
- Predicted questions
- Formulas
- MCQs
- Extracted questions

The PDF generation layer also uses HTML escaping to reduce formatting issues.

### 📋 Structured Extracted Questions

Extracted questions are displayed in a clean paper-wise format:

```text
Paper 1

1. Question one
2. Question two
3. Question three

Paper 2

1. Question one
2. Question two
3. Question three
