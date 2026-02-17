import os
import sys

print("Checking environment...")

# Check imports
try:
    import faiss
    print("MATCH: faiss imported")
except ImportError as e:
    print(f"ERROR: faiss import failed: {e}")

try:
    import sentence_transformers
    print("MATCH: sentence_transformers imported")
except ImportError as e:
    print(f"ERROR: sentence_transformers import failed: {e}")

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    print("MATCH: spacy model loaded")
except OSError:
    print("ERROR: spacy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
except ImportError as e:
    print(f"ERROR: spacy import failed: {e}")

# Check files
index_path = "../embeddings/faiss_index/legal.index"
data_path = "../data/sentences.json"

if os.path.exists(index_path):
    print(f"MATCH: Found index at {index_path}")
else:
    print(f"ERROR: Missing index at {index_path}")

if os.path.exists(data_path):
    print(f"MATCH: Found data at {data_path}")
else:
    print(f"ERROR: Missing data at {data_path}")

print("Diagnostic complete.")
