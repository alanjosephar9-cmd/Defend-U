## Quick Start (Windows)

Simply double-click the **`run.bat`** file in the project root. This will:
1. Start the FastAPI backend server in a new window.
2. Automatically open the frontend in your default browser.

---

## Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download Spacy Model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Configure Environment**
   - Copy `.env.example` to `.env`.
   - Update `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` with your Neo4j credentials.

4. **Run Backend**
   ```bash
   cd backend
   python -m uvicorn api:app --reload
   ```

5. **Run Frontend**
   - Open `frontend/index.html` in your browser.

## Data Processing (Optional)

If you have new PDFs in `data/raw_pdfs`, run:
1. `python backend/pdf_to_text.py`
2. `python backend/sentence_split.py`
3. `python backend/embedder.py` (Creates FAISS index)
