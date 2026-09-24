import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("Resume/Resume.csv")
df = df.dropna(subset=["Resume_str"]).reset_index(drop=True)

jobs = {
    "INFORMATION-TECHNOLOGY": "Python, Java, SQL, networking, software development, web development, database management, troubleshooting, Linux, cloud computing, technical support.",
    "HR": "Human resources, recruitment, employee relations, onboarding, payroll, benefits administration, performance management, HRIS, talent acquisition.",
    "SALES": "Sales, customer acquisition, lead generation, negotiation, account management, revenue targets, CRM, cold calling, client relationships.",
    "TEACHER": "Teaching, classroom management, lesson planning, curriculum development, student assessment, education, parent communication.",
    "ACCOUNTANT": "Accounting, bookkeeping, accounts payable, accounts receivable, financial statements, reconciliation, tax preparation, QuickBooks, auditing.",
    "CHEF": "Chef, cooking, kitchen management, menu planning, food preparation, food safety, culinary, restaurant, catering.",
}

vectorizer = TfidfVectorizer(stop_words="english")
resume_vectors = vectorizer.fit_transform(df["Resume_str"])

results = []
for category, text in jobs.items():
    scores = cosine_similarity(vectorizer.transform([text]), resume_vectors)[0]
    top = df.assign(score=scores).sort_values("score", ascending=False).head(10)
    p = (top["Category"] == category).mean()
    results.append(p)
    print(f"{category:25s} precision@10 = {p:.1f}")
    print("   top 10 came from:", dict(top["Category"].value_counts()))

print()
print("Average precision@10:", round(sum(results) / len(results), 2))