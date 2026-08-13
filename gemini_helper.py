"""LLM services for ExamLens AI v2.

The module keeps all model interaction in one place, validates the returned
JSON, and never silently substitutes another subject.
"""
import json
import os
from typing import Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError(
                "GROQ_API_KEY is missing. Add it to your .env file or Streamlit secrets."
            )
        _client = Groq(api_key=key)
    return _client


def _ask(prompt: str, json_mode: bool = False, max_tokens: int = 6000) -> str:
    kwargs = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are ExamLens AI, a rigorous university exam-paper analyst. "
                    "You analyze only the subject explicitly supplied by the user. "
                    "Never replace, broaden, or substitute the subject. "
                    "Separate evidence found in the uploaded papers from predictions. "
                    "If evidence is insufficient, say so instead of inventing paper-specific facts."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.15,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = _get_client().chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""


def _empty_result(subject: str, error: str = "") -> dict[str, Any]:
    return {
        "extracted_questions": "",
        "subject_detected": subject,
        "total_questions_analyzed": 0,
        "topic_frequency": {},
        "high_priority_topics": [],
        "medium_priority_topics": [],
        "low_priority_topics": [],
        "difficulty_distribution": {},
        "predicted_10mark": [],
        "predicted_2mark": [],
        "wildcard_question": "",
        "wildcard_reason": "",
        "roadmap": [],
        "quick_tips": [],
        "key_formulas": [],
        "analysis_status": "error",
        "analysis_error": error,
    }


def _normalise(data: dict, subject: str) -> dict:
    """Make the model response safe for the UI without inventing content."""
    list_keys = [
        "high_priority_topics", "medium_priority_topics", "low_priority_topics",
        "predicted_10mark", "predicted_2mark", "quick_tips", "key_formulas", "roadmap"
    ]
    for key in list_keys:
        if not isinstance(data.get(key), list):
            data[key] = []
    if not isinstance(data.get("topic_frequency"), dict):
        data["topic_frequency"] = {}
    if not isinstance(data.get("difficulty_distribution"), dict):
        data["difficulty_distribution"] = {}
    data["subject_detected"] = subject
    data["analysis_status"] = "success"
    return data


def analyze_all_in_one(raw_text: str, subject: str) -> dict:
    # Keep a generous context while preventing accidental runaway requests.
    source = raw_text[:30000]
    prompt = f"""
SUBJECT (immutable): {subject}

TASK
Analyze the uploaded previous-year exam papers for {subject}. Use the paper text
as the primary evidence. Do not invent a claim that a topic appeared a certain
number of times unless it is reasonably supported by the supplied text.

Return ONLY valid JSON with exactly these top-level keys:
{{
  "extracted_questions": "clean numbered questions grouped by paper/unit",
  "subject_detected": "{subject}",
  "total_questions_analyzed": 0,
  "topic_frequency": {{"topic": 0}},
  "high_priority_topics": [],
  "medium_priority_topics": [],
  "low_priority_topics": [],
  "difficulty_distribution": {{"Easy": 0, "Medium": 0, "Hard": 0}},
  "predicted_10mark": [],
  "predicted_2mark": [],
  "wildcard_question": "",
  "wildcard_reason": "",
  "roadmap": [],
  "quick_tips": [],
  "key_formulas": []
}}

QUALITY RULES
1. Every topic/question/formula must belong to {subject}.
2. "topic_frequency" counts repeated concepts visible in the supplied papers.
3. Priority lists must be derived from topic_frequency.
4. Predictions are forecasts, not guarantees. Prefer recurring concepts and clearly
   label the prediction basis in the wording when useful.
5. Do not claim exact marks unless the paper text supports the marks.
6. If the PDFs are incomplete or text extraction is poor, keep the evidence-based
   fields conservative.
7. Roadmap must contain exactly 7 days. Each day has:
   day, topic, focus, tasks (3 short strings), tip, hours.
8. Provide 5 predicted_10mark questions and 8 predicted_2mark questions when
   sufficient evidence exists; otherwise provide fewer rather than hallucinating.
9. Provide 5 key formulas/definitions only if genuinely relevant to {subject}.
10. Do not output markdown fences.

UPLOADED PAPER TEXT:
{source}
"""
    try:
        data = json.loads(_ask(prompt, json_mode=True))
        return _normalise(data, subject)
    except Exception as exc:
        return _empty_result(subject, str(exc))


def generate_mcqs(subject: str, topic: str, num: int = 5) -> str:
    prompt = f"""
Create {num} university-level MCQs for:
SUBJECT: {subject}
TOPIC: {topic}

Stay strictly inside this subject/topic. Do not mix in another subject.
Format:
Q1. question
A) option
B) option
C) option
D) option
Answer: B) correct option
Tip: one concise explanation or memory aid
---
"""
    return _ask(prompt, json_mode=False, max_tokens=3500)
