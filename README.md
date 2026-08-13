# 🎯 ExamLens AI v2

An AI-powered university exam-paper analyzer built with Streamlit, Groq and Llama.

## What changed in v2

- Fixed the startup typo in the original `app.py` (`mport` → `import`).
- Stronger subject-locking: the model is explicitly prevented from substituting another subject.
- Larger paper context window than the original 5,000-character slice.
- Evidence-first analysis: frequencies and priorities are requested from the uploaded papers.
- No fake subject-specific fallback predictions when the API fails.
- MCQs now receive both the selected subject and topic as context.
- Cleaner PDF generation with HTML escaping to prevent malformed exports.
- Better extraction metadata so users can see whether a PDF contains readable text.
- Analysis results are stored in Streamlit session state, so switching tabs does not repeat the main API call.
- Configurable model through `GROQ_MODEL`.
- More accurate UI copy: avoids hard-coding a specific daily quota.
- Added a clearer error state instead of silently showing unrelated demo data.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
# Put your Groq key in .env
streamlit run app.py
```

`.env`:
```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

## Deployment

For Streamlit Community Cloud, add `GROQ_API_KEY` under App → Settings → Secrets.

## Important limitation

`pdfplumber` extracts selectable PDF text. Scanned/image-only PDFs may produce little or no text. OCR should be added as a future enhancement if scanned papers are a requirement.

## Suggested resume line

**ExamLens AI — Exam Paper Analyzer & Question Predictor:** Built a Streamlit application that extracts university exam-paper text, uses an LLM to identify recurring topics and generate evidence-based predictions, creates a 7-day study roadmap and MCQ practice, and exports personalized PDFs.
