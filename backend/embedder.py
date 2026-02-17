from sentence_transformers import SentenceTransformer
import json
import faiss
import numpy as np
import os

print("Loading AI model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Loading sentences...")
with open("../data/sentences.json", "r", encoding="utf-8") as f:
    data = json.load(f)

sentences = [x["sentence"] for x in data]

print("Creating embeddings...")
embeddings = model.encode(sentences, show_progress_bar=True)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

os.makedirs("../embeddings/faiss_index", exist_ok=True)
faiss.write_index(index, "../embeddings/faiss_index/legal.index")

print("Embeddings saved. Total sentences:", len(sentences))

