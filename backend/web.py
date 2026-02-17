from flask import Flask, request, jsonify
from search import search
from engine import extract_terms, build_concepts
from graph import store

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    query = data["query"]

    results = search(query)
    terms = extract_terms(results)
    concepts = build_concepts(terms)

    store(query, concepts)

    return jsonify({
        "query": query,
        "results": results,
        "concepts": concepts
    })

app.run(debug=True)
