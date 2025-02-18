import fitz  # PyMuPDF for PDF parsing
import spacy
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load NLP model (spaCy's pre-trained model)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess

    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Predefined skill set for extraction
SKILL_SET = {"Python", "Java", "HTML", "CSS", "Machine Learning", "Data Science", "SQL", "NLP", "Django", "Flask"}


# Database setup
def init_db():
    conn = sqlite3.connect("resume_analysis.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        skills TEXT,
                        similarity_score REAL)''')
    conn.commit()
    conn.close()


def save_to_db(skills, similarity):
    conn = sqlite3.connect("resume_analysis.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO results (skills, similarity_score) VALUES (?, ?)", (", ".join(skills), similarity))
    conn.commit()
    conn.close()


def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = " ".join([page.get_text("text") for page in doc])
    return text


def extract_skills(text):
    """Extract skills from the given text using NLP."""
    doc = nlp(text)
    words = {token.text for token in doc if token.is_alpha}
    extracted_skills = words & SKILL_SET
    return extracted_skills


def calculate_similarity(resume_text, job_description):
    """Calculates similarity score between resume and job description."""
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, job_description])
    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(similarity * 100, 2)


def analyze_resume():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not file_path:
        return
    job_description = job_desc_entry.get("1.0", tk.END).strip()
    if not job_description:
        messagebox.showerror("Error", "Please enter a job description.")
        return

    resume_text = extract_text_from_pdf(file_path)
    extracted_skills = extract_skills(resume_text)
    similarity_score = calculate_similarity(resume_text, job_description)

    save_to_db(extracted_skills, similarity_score)

    result_text.set(f"Extracted Skills: {', '.join(extracted_skills)}\nMatch Score: {similarity_score}%")


# Initialize database
init_db()

# GUI Setup
root = tk.Tk()
root.title("Resume Analyzer")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

tk.Label(frame, text="Job Description:").pack(anchor="w")
job_desc_entry = tk.Text(frame, height=5, width=50)
job_desc_entry.pack()

tk.Button(frame, text="Select Resume PDF", command=analyze_resume).pack(pady=5)

result_text = tk.StringVar()
result_label = tk.Label(frame, textvariable=result_text, justify="left")
result_label.pack()

root.mainloop()