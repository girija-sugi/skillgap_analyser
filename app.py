import os
import re
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skills_data import SKILLS, SKILL_CATEGORIES

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resume", "Resume.csv")

@st.cache_resource
def load_vectorizer():
    """Fit the matching engine once on real IT resumes from the dataset."""
    try:
        df = pd.read_csv(CSV_PATH)
        df = df[df["Category"] == "INFORMATION-TECHNOLOGY"].dropna(subset=["Resume_str"])
        vec = TfidfVectorizer(stop_words="english")
        vec.fit(df["Resume_str"])
        return vec, len(df)
    except Exception:
        return None, 0

vectorizer, corpus_size = load_vectorizer()

def read_resume(file):
    name = file.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(file)
        return " ".join(page.extract_text() or "" for page in reader.pages)
    elif name.endswith(".docx"):
        doc = Document(file)
        return " ".join(p.text for p in doc.paragraphs)
    return ""

def match_score(resume_text, job_text):
    if vectorizer is not None:
        vectors = vectorizer.transform([resume_text, job_text])
    else:
        vectors = TfidfVectorizer(stop_words="english").fit_transform([resume_text, job_text])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(score * 100, 1)

def extract_skills(text):
    text = text.lower()
    found = set()
    for skill in SKILLS:
        pattern = r"(?<![\w+])" + re.escape(skill) + r"(?![\w+])"
        if re.search(pattern, text):
            found.add(skill)
    return found

def initials(name):
    """Two-letter initials for the candidate avatar chip."""
    parts = re.split(r"[\s_\-.]+", os.path.splitext(name)[0].strip())
    parts = [p for p in parts if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()


def skill_radar(resume_skills, job_skills):
    """Per-category coverage: of the skills the JD asks for in each
    category, what fraction does this resume already have."""
    labels, values = [], []
    for category, members in SKILL_CATEGORIES.items():
        asked = job_skills & set(members)
        if not asked:
            continue
        have = asked & resume_skills
        labels.append(category)
        values.append(round(len(have) / len(asked) * 100))

    if not labels:
        return None

    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]

    fig = go.Figure(data=[go.Scatterpolar(
        r=values_closed, theta=labels_closed, fill="toself",
        fillcolor="rgba(139, 92, 246, 0.28)",
        line=dict(color="#A78BFA", width=2),
        marker=dict(color="#38BDF8", size=6),
    )])
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False,
                             gridcolor="#2A3A63", linecolor="#2A3A63"),
            angularaxis=dict(gridcolor="#2A3A63", linecolor="#2A3A63",
                              tickfont=dict(color="#C9D3EE", size=11)),
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=20, b=20),
        height=280,
    )
    return fig


def skill_donut(skill_score):
    """Donut chart: skill match % vs remaining, styled for the dark theme."""
    fig = go.Figure(data=[go.Pie(
        values=[skill_score, 100 - skill_score],
        hole=0.72,
        marker=dict(colors=["#8B5CF6", "#2D3A66"], line=dict(color="#131D3D", width=3)),
        textinfo="none",
        sort=False,
        direction="clockwise",
    )])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        annotations=[dict(
            text=f"<b>{skill_score}%</b>", x=0.5, y=0.5,
            font=dict(size=28, color="#FFFFFF", family="Georgia"),
            showarrow=False
        )]
    )
    return fig

st.set_page_config(page_title="Skill Gap Analyser", page_icon="🎯", layout="wide")

st.markdown("""
<style>
@keyframes gradientDrift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.stApp {
    background: linear-gradient(120deg, #0B1120 0%, #111A33 45%, #171238 75%, #0B1120 100%) !important;
    background-size: 300% 300% !important;
    animation: gradientDrift 22s ease infinite;
}
.block-container {
    max-width: 880px !important;
    margin: 0 auto !important;
    padding-top: 2rem !important;
}
#MainMenu, footer, header {visibility: hidden;}

p, label, .stMarkdown, span {
    color: #C9D3EE;
}
.stTextArea textarea {
    background-color: #16213E !important;
    color: #EAF0FF !important;
    border: 1px solid #2A3A63 !important;
    border-radius: 10px !important;
}
.stTextArea label p {
    color: #EAF0FF !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}
.stFileUploader label p {
    color: #EAF0FF !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}
.stFileUploader section {
    background-color: #16213E !important;
    border: 1px dashed #3B4C82 !important;
    border-radius: 12px !important;
}
.stFileUploader section div small,
[data-testid="stFileUploaderDropzoneInstructions"] div,
[data-testid="stFileUploaderDropzoneInstructions"] span {
    color: #AEB9E0 !important;
    opacity: 1 !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    justify-content: center;
}
.stTabs [data-baseweb="tab"] {
    color: #C9D3EE !important;
    font-weight: 800 !important;
    font-size: 20px !important;
    padding: 14px 28px !important;
    background-color: #131D3D !important;
    border-radius: 14px !important;
    border: 1px solid #2A3A63 !important;
}
.stTabs [aria-selected="true"] {
    color: #FFFFFF !important;
    background: linear-gradient(145deg, #6D28D9, #A78BFA) !important;
    border: none !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    display: none;
}
.stTabs [data-baseweb="tab-border"] {
    display: none;
}

.hero {
    text-align: center;
    padding: 10px 0 30px 0;
}
.hero-eyebrow {
    color: #FFFFFF;
    font-family: 'Georgia', serif;
    font-size: 34px;
    font-weight: 800;
    letter-spacing: 0.5px;
}
.hero-title {
    color: #A78BFA;
    font-size: 16px;
    font-weight: 600;
    margin: 10px 0 10px 0;
    line-height: 1.4;
}
.hero-sub {
    color: #8E9CC7;
    font-size: 14px;
    font-weight: 400;
    max-width: 520px;
    margin: 0 auto;
}
.trust-bar {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin: 4px auto 28px auto;
}
.trust-pill {
    background: rgba(139, 92, 246, 0.12);
    border: 1px solid rgba(167, 139, 250, 0.35);
    color: #C9B8FF;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.2px;
    padding: 7px 14px;
    border-radius: 999px;
}

.stat-row {
    display: flex;
    gap: 18px;
}
.stat-card {
    background: linear-gradient(145deg, #1B2A55, #131D3D);
    border: 1px solid #2E4080;
    border-radius: 18px;
    padding: 26px;
    box-shadow: 0 8px 24px rgba(109, 40, 217, 0.25);
    text-align: center;
    height: 100%;
    flex: 1;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
.stat-card:hover {
    transform: translateY(-3px);
    border-color: #7C4DFF;
    box-shadow: 0 12px 32px rgba(124, 77, 255, 0.35);
}
.stat-value {
    font-family: 'Georgia', serif;
    font-size: 40px;
    font-weight: 800;
    background: linear-gradient(90deg, #A78BFA, #38BDF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.stat-label {
    font-size: 12px;
    color: #AEB9E0;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 6px;
    font-weight: 700;
}
.chart-label {
    font-size: 12px;
    color: #AEB9E0;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 700;
    text-align: center;
    margin-top: -6px;
}

.section-card {
    background: rgba(19, 29, 61, 0.75);
    backdrop-filter: blur(6px);
    border: 1px solid #2A3A63;
    border-radius: 16px;
    padding: 22px 26px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.25);
    margin-bottom: 18px;
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
.section-card:hover {
    border-color: #4C3B99;
    box-shadow: 0 8px 26px rgba(109, 40, 217, 0.18);
}
.section-title {
    color: #EAF0FF;
    font-weight: 800;
    font-size: 16px;
    margin-bottom: 12px;
}
.section-body {
    color: #C9D3EE;
    font-size: 14px;
}

.skill-chip {
    display: inline-block !important;
    padding: 7px 16px !important;
    border-radius: 999px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    margin: 4px 6px 4px 0 !important;
    border: none !important;
}
.chip-have {
    background-color: #0F3D2A !important;
    color: #4ADE80 !important;
}
.chip-need {
    background-color: #4A2113 !important;
    color: #FB923C !important;
}
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: #A78BFA !important;
    border-color: #A78BFA !important;
}
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] {
    color: #8E9CC7 !important;
}
.rank-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 480px;
    overflow-y: auto;
}
.rank-row {
    display: flex;
    align-items: center;
    gap: 16px;
    background: #16213E;
    border: 1px solid #2A3A63;
    border-radius: 12px;
    padding: 14px 18px;
}
.rank-num {
    font-family: 'Georgia', serif;
    font-weight: 800;
    font-size: 15px;
    color: #A78BFA;
    min-width: 34px;
}
.rank-main {
    flex: 1;
    min-width: 0;
}
.rank-name {
    color: #EAF0FF;
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 3px;
    word-break: break-word;
}
.rank-meta {
    color: #8E9CC7;
    font-size: 12px;
    line-height: 1.5;
}
.rank-meta-label {
    color: #AEB9E0;
    font-weight: 700;
}
.rank-score {
    font-family: 'Georgia', serif;
    font-weight: 800;
    font-size: 16px;
    padding: 8px 14px;
    border-radius: 10px;
    white-space: nowrap;
    min-width: 64px;
    text-align: center;
}
.rank-row {
    transition: transform 0.15s ease, border-color 0.15s ease;
}
.rank-row:hover {
    transform: translateX(3px);
    border-color: #6D28D9;
}
.rank-avatar {
    width: 38px;
    height: 38px;
    min-width: 38px;
    border-radius: 12px;
    background: linear-gradient(145deg, #6D28D9, #38BDF8);
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Georgia', serif;
    font-weight: 800;
    font-size: 13px;
}
.mini-bar-track {
    background: #0F1730;
    border-radius: 999px;
    height: 6px;
    width: 100%;
    margin-top: 6px;
    overflow: hidden;
}
.mini-bar-fill {
    height: 100%;
    border-radius: 999px;
}
.stTextInput input {
    background-color: #16213E !important;
    color: #EAF0FF !important;
    border: 1px solid #2A3A63 !important;
    border-radius: 10px !important;
}
.stTextInput label p {
    color: #EAF0FF !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Skill Gap Analyser</div>
    <div class="hero-title">Know exactly what stands between you and the role</div>
    <div class="hero-sub">Upload a resume, paste a job description, and see your match score, skill gaps, and what to learn next.</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="trust-bar">
    <span class="trust-pill">🧠 TF-IDF matching engine</span>
    <span class="trust-pill">📄 Trained on {corpus_size or '—'} real IT resumes</span>
    <span class="trust-pill">🎯 {len(SKILLS)} tracked skills</span>
</div>
""", unsafe_allow_html=True)

tab_single, tab_bulk = st.tabs(["For Students", "For Placement Team"])

with tab_single:
    resume = st.file_uploader("Upload your resume", type=["pdf", "docx"], key="single")
    job_desc = st.text_area("Paste the job description", height=200, key="single_job")

    resume_text = ""
    if resume is not None:
        st.success(f"Uploaded: {resume.name}")
        resume_text = read_resume(resume)

    if resume_text and job_desc:
        text_score = match_score(resume_text, job_desc)

        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_desc)
        have = sorted(job_skills & resume_skills)
        need = sorted(job_skills - resume_skills)

        skill_score = round(len(have) / len(job_skills) * 100, 1) if job_skills else 0

        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.plotly_chart(skill_donut(skill_score), use_container_width=True, config={"displayModeBar": False})
            st.markdown('<div class="chart-label">Skill Match</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{text_score}%</div>
                <div class="stat-label">Overall Match</div>
            </div>
            """, unsafe_allow_html=True)

        radar_fig = skill_radar(resume_skills, job_skills)
        if radar_fig is not None:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🕸️ Coverage by category</div>', unsafe_allow_html=True)
            st.plotly_chart(radar_fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            chips = "".join(f'<span class="skill-chip chip-have">{s}</span>' for s in have) if have else '<span class="section-body">No overlap found</span>'
            st.markdown(f"""
            <div class="section-card">
                <div class="section-title">✅ You already have</div>
                {chips}
            </div>
            """, unsafe_allow_html=True)
        with col2:
            chips = "".join(f'<span class="skill-chip chip-need">{s}</span>' for s in need) if need else '<span class="section-body">Nothing missing!</span>'
            st.markdown(f"""
            <div class="section-card">
                <div class="section-title">🎯 Skills to build</div>
                {chips}
            </div>
            """, unsafe_allow_html=True)

        rec = f"Focus on learning: {', '.join(need)}." if need else "Your resume covers every skill the job description asks for."
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">💡 Recommendation</div>
            <div class="section-body">{rec}</div>
        </div>
        """, unsafe_allow_html=True)

with tab_bulk:
    bulk_job = st.text_area("Paste the job description", height=200, key="bulk_job")
    bulk_files = st.file_uploader(
        "Upload candidate resumes", type=["pdf", "docx"],
        accept_multiple_files=True, key="bulk"
    )

    if bulk_files and bulk_job:
        job_skills = extract_skills(bulk_job)
        rows = []
        progress = st.progress(0, text=f"Processing 0 of {len(bulk_files)} resumes...")
        for i, f in enumerate(bulk_files):
            text = read_resume(f)
            found = extract_skills(text)
            have = job_skills & found
            skill_score = round(len(have) / len(job_skills) * 100, 1) if job_skills else 0
            rows.append({
                "Resume": f.name,
                "Skill match %": skill_score,
                "Overall match %": match_score(text, bulk_job),
                "Skills matched": ", ".join(sorted(have)),
                "Skills missing": ", ".join(sorted(job_skills - found)),
            })
            progress.progress((i + 1) / len(bulk_files), text=f"Processing {i + 1} of {len(bulk_files)} resumes...")
        progress.empty()

        rows.sort(key=lambda r: (r["Skill match %"], r["Overall match %"]), reverse=True)

        st.markdown(f"""
        <div class="stat-row" style="margin-top: 20px;">
            <div class="stat-card">
                <div class="stat-value">{len(rows)}</div>
                <div class="stat-label">Resumes Analysed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{rows[0]['Skill match %']}%</div>
                <div class="stat-label">Top Score</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎚️ Shortlist threshold</div>', unsafe_allow_html=True)
        threshold = st.slider(
            "Only show candidates with skill match at or above:",
            min_value=0, max_value=100, value=0, step=5, key="threshold"
        )
        search_term = st.text_input(
            "Filter by resume file name", value="", key="candidate_search",
            placeholder="Type a name to filter…"
        )
        shortlisted = [r for r in rows if r["Skill match %"] >= threshold]
        if search_term.strip():
            needle = search_term.strip().lower()
            shortlisted = [r for r in shortlisted if needle in r["Resume"].lower()]
        st.markdown(
            f'<div class="section-body">{len(shortlisted)} of {len(rows)} candidates meet this threshold.</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Ranking</div>', unsafe_allow_html=True)

        rank_rows_parts = []
        for i, r in enumerate(shortlisted, start=1):
            score = r["Skill match %"]
            if score >= 70:
                score_color, score_bg = "#4ADE80", "#0F3D2A"
            elif score >= 40:
                score_color, score_bg = "#FB923C", "#4A2113"
            else:
                score_color, score_bg = "#F87171", "#4A1313"

            matched = r["Skills matched"] or "—"
            missing = r["Skills missing"] or "—"

            row_html = (
                '<div class="rank-row">'
                f'<div class="rank-num">#{i}</div>'
                f'<div class="rank-avatar">{initials(r["Resume"])}</div>'
                '<div class="rank-main">'
                f'<div class="rank-name">{r["Resume"]}</div>'
                '<div class="rank-meta">'
                f'<span class="rank-meta-label">Have:</span> {matched}<br>'
                f'<span class="rank-meta-label">Missing:</span> {missing}'
                '</div>'
                '<div class="mini-bar-track">'
                f'<div class="mini-bar-fill" style="width:{score}%; background-color:{score_color};"></div>'
                '</div>'
                '</div>'
                f'<div class="rank-score" style="color:{score_color}; background-color:{score_bg};">{score}%</div>'
                '</div>'
            )
            rank_rows_parts.append(row_html)

        if not rank_rows_parts:
            st.markdown('<div class="section-body">No candidates match this threshold/search.</div>', unsafe_allow_html=True)
        else:
            rank_rows_html = '<div class="rank-list">' + "".join(rank_rows_parts) + '</div>'
            st.markdown(rank_rows_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        csv_data = pd.DataFrame(shortlisted).to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download shortlisted candidates (CSV)",
            data=csv_data,
            file_name="shortlisted_candidates.csv",
            mime="text/csv",
        )

        # ---- Batch analytics ----
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Batch analytics</div>', unsafe_allow_html=True)

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            buckets = ["0-20", "21-40", "41-60", "61-80", "81-100"]
            bucket_counts = [0, 0, 0, 0, 0]
            for r in rows:
                s = r["Skill match %"]
                idx = min(int(s // 20), 4)
                bucket_counts[idx] += 1

            fig_hist = go.Figure(data=[go.Bar(
                x=buckets, y=bucket_counts,
                marker=dict(color="#8B5CF6"),
            )])
            fig_hist.update_layout(
                title=dict(text="Score distribution", font=dict(color="#EAF0FF", size=14)),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#C9D3EE"),
                margin=dict(l=10, r=10, t=40, b=10),
                height=280,
                xaxis=dict(title="Skill match %", gridcolor="#2A3A63"),
                yaxis=dict(title="Candidates", gridcolor="#2A3A63"),
            )
            st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

        with chart_col2:
            missing_counts = {}
            for r in rows:
                missing = r["Skills missing"]
                if missing:
                    for s in missing.split(", "):
                        missing_counts[s] = missing_counts.get(s, 0) + 1

            if missing_counts:
                top_missing = sorted(missing_counts.items(), key=lambda x: x[1], reverse=True)[:8]
                labels = [s for s, _ in top_missing]
                counts = [c for _, c in top_missing]

                fig_missing = go.Figure(data=[go.Bar(
                    x=counts, y=labels, orientation="h",
                    marker=dict(color="#FB923C"),
                )])
                fig_missing.update_layout(
                    title=dict(text="Most common missing skills", font=dict(color="#EAF0FF", size=14)),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#C9D3EE"),
                    margin=dict(l=10, r=10, t=40, b=10),
                    height=280,
                    xaxis=dict(title="Candidates missing", gridcolor="#2A3A63"),
                    yaxis=dict(autorange="reversed"),
                )
                st.plotly_chart(fig_missing, use_container_width=True, config={"displayModeBar": False})
            else:
                st.markdown('<div class="section-body">No missing skills across this batch.</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)