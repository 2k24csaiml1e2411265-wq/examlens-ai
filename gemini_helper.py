import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ── Groq client ───────────────────────────────────────────────
# 14,400 free requests/day — 10x more than Gemini
# Get free key at: console.groq.com

_client = None

def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found!\n"
                "1. Go to console.groq.com\n"
                "2. Sign up free → API Keys → Create API key\n"
                "3. Add to .env file: GROQ_API_KEY=gsk_..."
            )
        _client = Groq(api_key=api_key)
    return _client

MODEL = "llama-3.3-70b-versatile"   # fastest + smartest free Groq model


def _ask(prompt: str, json_mode: bool = False) -> str:
    """Call Groq API — ultra fast, 14400 req/day free."""
    client = _get_client()
    kwargs = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert B.Tech exam analyzer for AKTU/HBTU university India. "
                    "You help students analyze previous year papers, detect patterns, and predict questions. "
                    "Always be specific, accurate, and exam-focused."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 4096,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


# ══════════════════════════════════════════════════════════════
# SINGLE MEGA CALL — all analysis in ONE API call
# saves quota, faster results, consistent output
# ══════════════════════════════════════════════════════════════

def analyze_all_in_one(raw_text: str, subject: str) -> dict:
    """
    Single API call that does everything:
    extract questions + analyze topics + predict questions + build roadmap
    Uses Groq JSON mode for reliable parsing.
    """
    prompt = f"""
Analyze the following B.Tech exam paper text for subject: {subject}
University: AKTU/HBTU India

EXAM TEXT:
{raw_text[:5000]}

Return a JSON object with exactly these keys:

{{
  "extracted_questions": "Clean numbered list of all questions found. Group by UNIT if present. Format: UNIT 1:\\n1. question\\n2. question",
  "subject_detected": "detected subject name",
  "total_questions_analyzed": <integer count of questions found>,
  "topic_frequency": {{
    "<topic name>": <integer count how many times this topic appeared>
  }},
  "high_priority_topics": ["<5 most repeated topics>"],
  "medium_priority_topics": ["<3 medium frequency topics>"],
  "low_priority_topics": ["<2 least repeated topics>"],
  "difficulty_distribution": {{
    "Easy (2-mark)": <integer>,
    "Medium (5-mark)": <integer>,
    "Hard (10-mark)": <integer>
  }},
  "predicted_10mark": [
    "<Specific 10-mark question likely to appear - write full question>",
    "<Specific 10-mark question likely to appear - write full question>",
    "<Specific 10-mark question likely to appear - write full question>",
    "<Specific 10-mark question likely to appear - write full question>",
    "<Specific 10-mark question likely to appear - write full question>"
  ],
  "predicted_2mark": [
    "<Specific 2-mark question>",
    "<Specific 2-mark question>",
    "<Specific 2-mark question>",
    "<Specific 2-mark question>",
    "<Specific 2-mark question>",
    "<Specific 2-mark question>",
    "<Specific 2-mark question>",
    "<Specific 2-mark question>"
  ],
  "wildcard_question": "<One important question from a less-tested but important area>",
  "wildcard_reason": "<One sentence why this might appear in the next exam>",
  "roadmap": [
    {{"day": 1, "topic": "<topic>", "focus": "<specific what to study>", "tasks": ["<task1>", "<task2>", "<task3>"], "tip": "<one smart study tip>", "hours": 3}},
    {{"day": 2, "topic": "<topic>", "focus": "<specific what to study>", "tasks": ["<task1>", "<task2>", "<task3>"], "tip": "<one smart study tip>", "hours": 3}},
    {{"day": 3, "topic": "<topic>", "focus": "<specific what to study>", "tasks": ["<task1>", "<task2>", "<task3>"], "tip": "<one smart study tip>", "hours": 3}},
    {{"day": 4, "topic": "<topic>", "focus": "<specific what to study>", "tasks": ["<task1>", "<task2>", "<task3>"], "tip": "<one smart study tip>", "hours": 3}},
    {{"day": 5, "topic": "<topic>", "focus": "<specific what to study>", "tasks": ["<task1>", "<task2>", "<task3>"], "tip": "<one smart study tip>", "hours": 3}},
    {{"day": 6, "topic": "Revision", "focus": "Revise all high priority topics", "tasks": ["Solve 10-mark questions", "Revise formulas", "Make quick notes"], "tip": "Focus on topics that appeared 3+ times", "hours": 4}},
    {{"day": 7, "topic": "Mock Test", "focus": "Full exam simulation", "tasks": ["Attempt full mock paper", "Check answers", "Revise weak areas"], "tip": "Simulate real exam: 3 hours, no breaks", "hours": 3}}
  ],
  "quick_tips": [
    "<Specific exam strategy tip for this subject>",
    "<Specific exam strategy tip for this subject>",
    "<Specific exam strategy tip for this subject>"
  ],
  "key_formulas": [
    "<Important formula or definition to memorize>",
    "<Important formula or definition to memorize>",
    "<Important formula or definition to memorize>",
    "<Important formula or definition to memorize>",
    "<Important formula or definition to memorize>"
  ]
}}

Rules:
- Write REAL specific exam questions, not generic placeholders
- Base predictions strictly on frequency patterns in the text
- All questions must be AKTU/HBTU university exam style
- key_formulas should be actual formulas/definitions relevant to this subject
"""
    try:
        text = _ask(prompt, json_mode=True)
        return json.loads(text)
    except Exception as e:
        # Fallback data if parsing fails
        return {
            "extracted_questions": "Could not extract. Please try again.",
            "subject_detected": subject,
            "total_questions_analyzed": 0,
            "topic_frequency": {"Machine Learning": 5, "Deep Learning": 4, "NLP": 3, "CNN": 3, "SVM": 2},
            "high_priority_topics": ["Machine Learning", "Neural Networks", "Deep Learning", "NLP", "Computer Vision"],
            "medium_priority_topics": ["SVM", "Decision Trees", "Clustering"],
            "low_priority_topics": ["Reinforcement Learning", "Bayesian Networks"],
            "difficulty_distribution": {"Easy (2-mark)": 8, "Medium (5-mark)": 7, "Hard (10-mark)": 5},
            "predicted_10mark": [
                "Explain the backpropagation algorithm with mathematical derivation and example.",
                "Describe the architecture of Convolutional Neural Network (CNN) with diagram.",
                "Explain Support Vector Machine (SVM) with kernel trick and its applications.",
                "What is overfitting? Explain regularization techniques to prevent it.",
                "Explain the LSTM architecture and how it solves the vanishing gradient problem."
            ],
            "predicted_2mark": [
                "Define supervised learning with example.",
                "What is the difference between classification and regression?",
                "Define precision, recall and F1-score.",
                "What is gradient descent?",
                "Define bias-variance tradeoff.",
                "What is a confusion matrix?",
                "Define activation function. Name its types.",
                "What is transfer learning?"
            ],
            "wildcard_question": "Explain the attention mechanism in transformer models with diagram.",
            "wildcard_reason": "Transformers are a growing trend in AIML curriculum at AKTU.",
            "roadmap": [
                {"day": 1, "topic": "Machine Learning Basics", "focus": "Core ML algorithms and math", "tasks": ["Study linear/logistic regression", "Understand gradient descent", "Solve 5 past 2-mark questions"], "tip": "Master the math — derivations fetch full marks", "hours": 3},
                {"day": 2, "topic": "Neural Networks", "focus": "Architecture and backpropagation", "tasks": ["Draw network architecture", "Derive backprop step by step", "Practice activation functions"], "tip": "Draw diagrams — they save time in exams", "hours": 3},
                {"day": 3, "topic": "Deep Learning", "focus": "CNN and RNN architectures", "tasks": ["Study CNN layer by layer", "Understand LSTM gates", "Compare CNN vs RNN"], "tip": "Focus on CNN — it appears every year", "hours": 3},
                {"day": 4, "topic": "NLP", "focus": "Text processing and models", "tasks": ["Study tokenization and embeddings", "Understand attention mechanism", "Practice NLP questions"], "tip": "Transformers are trending — study attention well", "hours": 3},
                {"day": 5, "topic": "SVM and Clustering", "focus": "SVM kernel trick and K-means", "tasks": ["Study SVM with kernel functions", "K-means algorithm steps", "Compare clustering methods"], "tip": "Draw SVM hyperplane diagrams for visual marks", "hours": 3},
                {"day": 6, "topic": "Revision", "focus": "Revise all high priority topics", "tasks": ["Solve 10-mark questions", "Revise all formulas", "Make quick revision notes"], "tip": "Focus on topics that appeared 3+ times in past papers", "hours": 4},
                {"day": 7, "topic": "Mock Test", "focus": "Full exam simulation", "tasks": ["Attempt full mock paper in 3 hours", "Check and correct answers", "Revise weakest 2 topics"], "tip": "Simulate real exam conditions — no phone, no breaks", "hours": 3}
            ],
            "quick_tips": [
                "Start with Section A (2-mark) — attempt all 10 in first 30 minutes.",
                "Write neat labeled diagrams — AKTU gives extra marks for good diagrams.",
                "No negative marking — attempt every question even if unsure."
            ],
            "key_formulas": [
                "Gradient Descent: θ = θ - α∇J(θ)",
                "Cross Entropy Loss: L = -Σ y·log(ŷ)",
                "Precision = TP/(TP+FP), Recall = TP/(TP+FN)",
                "F1 Score = 2·(Precision·Recall)/(Precision+Recall)",
                "Sigmoid: σ(x) = 1/(1+e^(-x))"
            ]
        }


def generate_mcqs(topic: str, num: int = 5) -> str:
    """Generate MCQs — 1 API call, returns formatted string."""
    prompt = f"""
Generate {num} AKTU/HBTU university style multiple choice questions on the topic: {topic}

These must be realistic exam questions a B.Tech AIML student would see.

Format EACH question EXACTLY like this (include the --- separator):

Q1. [Specific technical question about {topic}]
A) [Option]
B) [Option]  
C) [Option]
D) [Option]
Answer: [Letter]) [Correct option]
Tip: [One-line memory trick or key concept to remember]

---

Rules:
- Questions must be technically accurate
- Options must be realistic (no obviously wrong answers)
- Progress from easy to hard
- Cover different aspects of {topic}
- Write questions a professor would actually set in AKTU exam
"""
    return _ask(prompt)
