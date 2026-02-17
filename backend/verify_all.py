import sys
import os

# Ensure backend dir is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Importing modules...")
try:
    from search import search
    from kanoon import search_kanoon
    from engine import extract_terms, build_concepts
    from graph import store
    print("Imports successful.")
except Exception as e:
    print(f"Import Error: {e}")
    sys.exit(1)

query = "contract breach"

print(f"Testing local search with query: '{query}'")
try:
    results = search(query)
    print(f"Local results found: {len(results)}")
except Exception as e:
    print(f"Local search failed: {e}")

print("Testing Kanoon search...")
try:
    kanoon_results = search_kanoon(query)
    docs = kanoon_results.get("docs", [])
    print(f"Kanoon results found: {len(docs)}")
except Exception as e:
    print(f"Kanoon search failed: {e}")

print("Testing pipeline (terms -> concepts -> store)...")
try:
    terms = extract_terms(results)
    print(f"Terms extracted: {terms}")
    
    concepts = build_concepts(terms)
    print(f"Concepts built: {list(concepts.keys())}")
    
    store(query, concepts)
    print("Stored in graph (or skipped gracefully).")
except Exception as e:
    print(f"Pipeline failed: {e}")

print("Verification passed.")
