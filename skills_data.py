# skills_data.py
"""Shared skill taxonomy for the Skill Gap Analyser."""

SKILLS = [
    "python", "java", "c++", "sql", "html", "css", "javascript",
    "machine learning", "deep learning", "data analysis", "data visualization",
    "nlp", "computer vision", "flask", "django", "react", "tensorflow",
    "pytorch", "pandas", "numpy", "scikit-learn", "git", "docker",
    "aws", "cloud computing", "communication", "teamwork", "problem solving",
    "project management", "agile", "rest api", "power bi", "excel"
]

# Groups SKILLS into categories so the UI can show a per-category
# coverage breakdown (radar chart) instead of one flat list.
SKILL_CATEGORIES = {
    "Languages": ["python", "java", "c++", "sql", "html", "css", "javascript"],
    "AI / ML": ["machine learning", "deep learning", "nlp", "computer vision",
                "tensorflow", "pytorch", "scikit-learn"],
    "Data & Reporting": ["data analysis", "data visualization", "pandas",
                         "numpy", "power bi", "excel"],
    "Dev & Cloud": ["flask", "django", "react", "git", "docker", "aws",
                     "cloud computing", "rest api"],
    "Collaboration": ["communication", "teamwork", "problem solving",
                       "project management", "agile"],
}