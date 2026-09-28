# AI Legal Document Assistant — Project Update

Hey team, here is a quick, easy-to-read summary of exactly what we have built so far for the **30-40% milestone**. We successfully created a functional, end-to-end legal analysis pipeline **without** relying on Large Language Models (LLMs).

---

## 🛠️ The Tech Stack
*   **Backend:** FastAPI & Python
*   **PDF Parsing:** PyMuPDF
*   **NLP & Cleaning:** spaCy
*   **Machine Learning:** scikit-learn (Naive Bayes)
*   **Risk Assessment:** scikit-fuzzy (Fuzzy Logic)
*   **Frontend UI:** Vanilla HTML, CSS, JavaScript (Dark Mode)

---

## ✅ What is Working Right Now?
1.  **Beautiful Frontend:** A sleek dark-mode UI with a login screen, drag-and-drop PDF upload, and interactive risk gauges.
2.  **PDF Extraction:** The system can successfully read uploaded PDFs and extract text while handling errors (like empty or scanned files).
3.  **Clause Segmentation:** It intelligently breaks down a solid wall of legal text into individual, manageable "clauses".
4.  **AI Classification (Naive Bayes):** It predicts what category each clause belongs to: *Payment, Confidentiality, Termination, Liability, or General*.
5.  **Fuzzy Risk Scoring:** It mathematically calculates a risk score (0-100) for every single clause by looking at how important the clause is, how ambiguous the wording is, and if there are aggressive keywords (like "penalty" or "indemnify").
6.  **Document Risk:** It gives the entire document an overall risk score (LOW, MEDIUM, HIGH) based on the clauses inside it.

---

## ⚙️ How the Pipeline Works (5 Steps)
When a user uploads a PDF, the backend does this instantly:
1.  **Extract:** PyMuPDF grabs the raw text.
2.  **Preprocess:** spaCy cleans the text (removes stop words, punctuation, etc.) and chops it into clauses.
3.  **Classify:** scikit-learn runs TF-IDF vectorization and uses Naive Bayes to classify the clause category.
4.  **Score Risk:** scikit-fuzzy runs the clause through 6 "IF/THEN" rules and outputs a continuous risk score.
5.  **Return:** FastAPI sends the results to the UI to be displayed in beautiful graphs and accordions.

---

## 🚀 How to Test the Demo
I've generated 3 perfect sample PDFs to use for the presentation. They are located in the `backend/sample_pdfs` folder:
*   `Standard_Consulting_Agreement.pdf` (Low Risk)
*   `Simple_NDA.pdf` (Focuses on Confidentiality)
*   `High_Risk_Vendor_Contract.pdf` (High Risk - Watch the gauges turn red!)

**To run the app:** Start the backend server (`uvicorn src.main:app --port 8000`) and open `http://localhost:8000` in your browser!

---

## ⏭️ Next Steps (For Future Phases)
*   Add a real Database (PostgreSQL/MySQL) to save history.
*   Feed the ML model hundreds of real clauses to improve accuracy.
*   Add the TF-IDF Question & Answering chatbot feature.
