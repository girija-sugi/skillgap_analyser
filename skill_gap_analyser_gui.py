"""
Skill Gap Analyser - Tkinter GUI Prototype
--------------------------------------------
Colorful desktop version of the Skill Gap Analyser.
Paste a resume and a job description, click Analyse, and see:
  - An overall match score (drawn as a colored ring)
  - Skills you already have (green)
  - Skills you're missing (orange)
  - A one-line recommendation

Pure standard library - no pip install needed. Run:
    python skill_gap_analyser_gui.py
"""

import re
import math
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import font as tkfont

# ---------- Colors (matches the web version's palette) ----------
BG = "#F6F8FC"
SURFACE = "#FFFFFF"
INK = "#1B2559"
INK_SOFT = "#5B6B8C"
LINE = "#E3E8F2"
HAVE = "#15803D"
HAVE_BG = "#E7F6EC"
NEED = "#C2410C"
NEED_BG = "#FDECE1"
BRAND = "#6D28D9"
BRAND_2 = "#0EA5E9"

SKILL_TAXONOMY = [
    "python", "java", "c++", "sql", "html", "css", "javascript",
    "machine learning", "deep learning", "data analysis", "data visualization",
    "nlp", "computer vision", "flask", "django", "react", "tensorflow",
    "pytorch", "pandas", "numpy", "scikit-learn", "git", "docker",
    "aws", "cloud computing", "communication", "teamwork", "problem solving",
    "project management", "agile", "rest api", "power bi", "excel"
]

SAMPLE_RESUME = """B.Tech student in Computer Science with hands-on experience in Python,
SQL and data analysis using pandas and numpy. Completed a machine
learning course project using scikit-learn. Familiar with Git for
version control and built a basic REST API using Flask. Participated
in two hackathons, demonstrating strong communication and teamwork.
Basic knowledge of Excel and Power BI for reporting."""

SAMPLE_JOB = """Looking for a candidate skilled in Python, machine learning, deep
learning, NLP, TensorFlow or PyTorch, pandas, and data visualization.
Experience with Git, Docker and cloud computing (AWS) is a plus.
Good communication and agile teamwork required."""


def extract_skills(text):
    text = text.lower()
    found = set()
    for skill in SKILL_TAXONOMY:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text):
            found.add(skill)
    return found


def tokenize(text):
    words = re.findall(r"[a-z0-9+.]+", text.lower())
    return [w for w in words if len(w) > 2]


def cosine_similarity(text_a, text_b):
    wa, wb = tokenize(text_a), tokenize(text_b)
    vocab = set(wa) | set(wb)
    if not vocab:
        return 0.0
    vec_a = {w: wa.count(w) for w in vocab}
    vec_b = {w: wb.count(w) for w in vocab}
    dot = sum(vec_a[w] * vec_b[w] for w in vocab)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


class SkillGapApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Skill Gap Analyser")
        self.configure(bg=BG)
        self.geometry("880x760")
        self.minsize(760, 640)
        self._build_ui()

    def _build_ui(self):
        wrap = tk.Frame(self, bg=BG, padx=28, pady=28)
        wrap.pack(fill="both", expand=True)

        # Header
        tk.Label(wrap, text="SKILL GAP ANALYSER", bg=BG, fg=BRAND,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(wrap, text="See the gap between where you are and the role you want.",
                 bg=BG, fg=INK, font=("Georgia", 18, "bold"),
                 wraplength=780, justify="left").pack(anchor="w", pady=(4, 4))
        tk.Label(wrap, text="Paste a resume and a job description below, then analyse.",
                 bg=BG, fg=INK_SOFT, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 16))

        # Panels
        panels = tk.Frame(wrap, bg=BG)
        panels.pack(fill="x")
        panels.columnconfigure(0, weight=1)
        panels.columnconfigure(1, weight=1)

        self.resume_box = self._make_panel(panels, "Resume", 0, SAMPLE_RESUME, self.load_resume_sample)
        self.job_box = self._make_panel(panels, "Job description", 1, "", self.load_job_sample)

        # Analyse button
        btn = tk.Button(wrap, text="Analyse skill gap", command=self.analyse,
                         bg=BRAND, fg="white", activebackground=BRAND_2,
                         font=("Segoe UI", 11, "bold"), relief="flat",
                         padx=26, pady=10, cursor="hand2")
        btn.pack(pady=20)

        # Results area
        self.results_frame = tk.Frame(wrap, bg=BG)
        self.results_frame.pack(fill="both", expand=True)

        score_row = tk.Frame(self.results_frame, bg=SURFACE, highlightbackground=LINE,
                              highlightthickness=1, padx=20, pady=20)
        score_row.pack(fill="x", pady=(0, 16))

        self.canvas = tk.Canvas(score_row, width=110, height=110, bg=SURFACE, highlightthickness=0)
        self.canvas.pack(side="left", padx=(0, 20))

        score_text = tk.Frame(score_row, bg=SURFACE)
        score_text.pack(side="left", fill="x", expand=True)
        tk.Label(score_text, text="Match score", bg=SURFACE, fg=INK,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.score_sub = tk.Label(score_text, text="Click Analyse to see the result.",
                                   bg=SURFACE, fg=INK_SOFT, font=("Segoe UI", 9),
                                   wraplength=500, justify="left")
        self.score_sub.pack(anchor="w", pady=(4, 0))

        cols = tk.Frame(self.results_frame, bg=BG)
        cols.pack(fill="both", expand=True)
        cols.columnconfigure(0, weight=1)
        cols.columnconfigure(1, weight=1)

        self.have_panel = self._make_chip_panel(cols, "You already have", HAVE, 0)
        self.need_panel = self._make_chip_panel(cols, "Skills to build", NEED, 1)

        rec_frame = tk.Frame(self.results_frame, bg=SURFACE, highlightbackground=LINE,
                              highlightthickness=1, padx=18, pady=14)
        rec_frame.pack(fill="x", pady=(14, 0))
        tk.Label(rec_frame, text="Recommendation", bg=SURFACE, fg=INK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.rec_label = tk.Label(rec_frame, text="", bg=SURFACE, fg=INK_SOFT,
                                   font=("Segoe UI", 10), wraplength=780, justify="left")
        self.rec_label.pack(anchor="w", pady=(4, 0))

        self._draw_ring(0)

    def _make_panel(self, parent, label, col, prefill, sample_cmd):
        panel = tk.Frame(parent, bg=SURFACE, highlightbackground=LINE,
                          highlightthickness=1, padx=14, pady=12)
        panel.grid(row=0, column=col, sticky="nsew", padx=(0, 10) if col == 0 else (10, 0))

        head = tk.Frame(panel, bg=SURFACE)
        head.pack(fill="x")
        tk.Label(head, text=label, bg=SURFACE, fg=INK,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Button(head, text="Load sample", command=sample_cmd, bg=SURFACE, fg=BRAND,
                  font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                  cursor="hand2").pack(side="right")

        box = scrolledtext.ScrolledText(panel, height=9, wrap="word", font=("Segoe UI", 10),
                                         relief="solid", borderwidth=1)
        box.pack(fill="both", expand=True, pady=(8, 0))
        if prefill:
            box.insert("1.0", prefill)
        return box

    def _make_chip_panel(self, parent, title, color, col):
        frame = tk.Frame(parent, bg=SURFACE, highlightbackground=LINE,
                          highlightthickness=1, padx=16, pady=14)
        frame.grid(row=0, column=col, sticky="nsew", padx=(0, 8) if col == 0 else (8, 0))
        tk.Label(frame, text=title, bg=SURFACE, fg=color,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        count_lbl = tk.Label(frame, text="0 skills", bg=SURFACE, fg=INK_SOFT,
                              font=("Segoe UI", 9))
        count_lbl.pack(anchor="w", pady=(2, 8))
        chip_area = tk.Frame(frame, bg=SURFACE)
        chip_area.pack(fill="both", expand=True)
        frame.count_lbl = count_lbl
        frame.chip_area = chip_area
        return frame

    def load_resume_sample(self):
        self.resume_box.delete("1.0", "end")
        self.resume_box.insert("1.0", SAMPLE_RESUME)

    def load_job_sample(self):
        self.job_box.delete("1.0", "end")
        self.job_box.insert("1.0", SAMPLE_JOB)

    def _draw_ring(self, pct):
        self.canvas.delete("all")
        self.canvas.create_oval(5, 5, 105, 105, outline=LINE, width=10)
        if pct > 0:
            extent = -360 * (pct / 100)
            self.canvas.create_arc(5, 5, 105, 105, start=90, extent=extent,
                                    outline=BRAND, width=10, style="arc")
        self.canvas.create_text(55, 55, text=f"{pct}%", font=("Georgia", 16, "bold"), fill=INK)

    def _fill_chips(self, panel, skills, fg, bg, empty_text):
        for w in panel.chip_area.winfo_children():
            w.destroy()
        panel.count_lbl.config(text=f"{len(skills)} skill{'s' if len(skills) != 1 else ''}")
        if not skills:
            tk.Label(panel.chip_area, text=empty_text, bg=SURFACE, fg=INK_SOFT,
                      font=("Segoe UI", 9, "italic")).pack(anchor="w")
            return
        font = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        row = tk.Frame(panel.chip_area, bg=SURFACE)
        row.pack(anchor="w", fill="x")
        x_used = 0
        max_width = 340
        for skill in sorted(skills):
            w = font.measure(skill) + 20  # approximate chip width incl. padding
            if x_used + w > max_width and x_used > 0:
                row = tk.Frame(panel.chip_area, bg=SURFACE)
                row.pack(anchor="w", fill="x", pady=(4, 0))
                x_used = 0
            chip = tk.Label(row, text=skill, bg=bg, fg=fg, font=("Segoe UI", 9, "bold"),
                             padx=10, pady=4)
            chip.pack(side="left", padx=(0, 6), pady=(0, 6))
            x_used += w + 6

    def analyse(self):
        resume = self.resume_box.get("1.0", "end").strip()
        job = self.job_box.get("1.0", "end").strip()
        if not resume or not job:
            messagebox.showwarning("Missing text", "Please fill in both the resume and job description.")
            return

        resume_skills = extract_skills(resume)
        job_skills = extract_skills(job)
        have = job_skills & resume_skills
        need = job_skills - resume_skills
        score = round(cosine_similarity(resume, job) * 100)

        self._draw_ring(score)
        self.score_sub.config(
            text=f"Based on overall text similarity between resume and job description ({score}%)."
        )
        self._fill_chips(self.have_panel, have, HAVE, HAVE_BG, "No overlap found")
        self._fill_chips(self.need_panel, need, NEED, NEED_BG, "Nothing missing \u2014 full match!")

        if need:
            self.rec_label.config(text=f"Focus on learning: {', '.join(sorted(need))}.")
        else:
            self.rec_label.config(text="This resume already covers every skill the job description asks for.")


if __name__ == "__main__":
    app = SkillGapApp()
    app.mainloop()
