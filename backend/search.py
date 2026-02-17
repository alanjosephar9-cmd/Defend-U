import faiss
import json
import numpy as np
import os
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/sentences.json")
INDEX_PATH = os.path.join(BASE_DIR, "../embeddings/faiss_index/legal.index")

model = SentenceTransformer("all-MiniLM-L6-v2")

try:
    index = faiss.read_index(INDEX_PATH)
except Exception as e:
    print(f"Warning: Could not load index from {INDEX_PATH}: {e}")
    index = None

data = []
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    print(f"Warning: Data file not found at {DATA_PATH}")

def search(query, top_k=5):
    if index is None or not data:
        return []

    q_vec = model.encode([query])
    D, I = index.search(np.array(q_vec), top_k)

    results = []
    for idx in I[0]:
        results.append(data[idx]["sentence"])
    return results
