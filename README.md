# Skill Gap Analyser

An ML-based prototype that compares a candidate's resume against a job description, identifies matching and missing skills, and gives an overall match score.

## What it does

- **Skill extraction** — pulls out relevant skills from both resume and job description text using keyword matching against a predefined skill taxonomy.
- **Match scoring** — computes an overall similarity score between the resume and job description using **TF-IDF + Cosine Similarity** (the ML component).
- **Skill gap report** — shows which required skills are already present, and which are missing, along with a learning recommendation.

## Files in this repo

| File | Description |
|---|---|
| `skill_gap_analyser.py` | Terminal/script version — prints the analysis for sample resumes and a job description. Uses scikit-learn's `TfidfVectorizer`. |
| `skill_gap_analyser_gui.py` | Desktop GUI version built with Tkinter (Python's built-in GUI library — no extra installs needed). Paste your own resume/job text and click Analyse. |
| `skill_gap_analyser.html` | Browser-based version — open directly in any browser, no Python required. Same logic reimplemented in JavaScript. |

## How to run

**Terminal script:**
python skill_gap_analyser.py
(requires scikit-learn: python -m pip install scikit-learn)

**GUI app:**
python skill_gap_analyser_gui.py
(no extra installs needed — Tkinter ships with Python)

**Browser version:**
Just double-click skill_gap_analyser.html, or open it in any browser.

## Tech used

- Python (scikit-learn, Tkinter)
- HTML/CSS/JavaScript
- TF-IDF vectorization + Cosine Similarity for match scoring
