import os
import json
import fitz
import spacy
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load AI Components
print("Loading NLP and AI Models...")
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.join(BASE_DIR, "../data/references")
SENTENCES_FILE = os.path.join(BASE_DIR, "../data/sentences.json")
INDEX_PATH = os.path.join(BASE_DIR, "../embeddings/faiss_index/legal.index")

def extract_text_from_pdf(pdf_path):
    """Extracts text from PDF pages"""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def ingest():
    """Main ingestion pipeline"""
    os.makedirs(REF_DIR, exist_ok=True)
    
    # 1. Load existing data
    existing_sentences = []
    if os.path.exists(SENTENCES_FILE):
        with open(SENTENCES_FILE, "r", encoding="utf-8") as f:
            existing_sentences = json.load(f)
    
    # Track existing filenames to avoid duplicates
    processed_files = {s["case"] for s in existing_sentences}
    new_data_count = 0

    print(f"\nScanning for new documents in {REF_DIR}...")
    
    # 2. Process PDFs in references folder
    files = [f for f in os.listdir(REF_DIR) if f.endswith(".pdf")]
    
    if not files:
        print("No new PDF files found in data/references.")
        return

    for filename in files:
        if filename in processed_files:
            print(f"Skipping {filename} (already indexed).")
            continue
            
        print(f"Ingesting: {filename}...")
        pdf_path = os.path.join(REF_DIR, filename)
        text = extract_text_from_pdf(pdf_path)
        
        if not text:
            continue
            
        doc = nlp(text)
        for sent in doc.sents:
            s_text = sent.text.strip()
            if 30 < len(s_text) < 500: # Quality filter
                existing_sentences.append({
                    "case": filename,
                    "sentence": s_text
                })
                new_data_count += 1
    
    if new_data_count == 0:
        print("No new sentences to index.")
        return

    # 3. Save updated sentences
    print(f"Saving {len(existing_sentences)} sentences to {SENTENCES_FILE}...")
    with open(SENTENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_sentences, f, indent=2)

    # 4. Rebuild Neural Index
    print("Rebuilding Neural FAISS Index (this may take a while for large docs)...")
    all_sentences = [x["sentence"] for x in existing_sentences]
    embeddings = model.encode(all_sentences, show_progress_bar=True)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    
    print(f"\nSUCCESS: Ingested {new_data_count} new sentences.")
    print(f"Total Knowledge Base Size: {len(existing_sentences)} sentences.")

if __name__ == "__main__":
    ingest()
