import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_terms(sentences):
    terms = []
    for s in sentences:
        doc = nlp(s)
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 3:
                terms.append(token.text.lower())
    return list(set(terms))

def build_concepts(terms):
    if len(terms) == 0:
        return {}

    embeddings = model.encode(terms)
    kmeans = KMeans(n_clusters=min(5, len(terms)))
    kmeans.fit(embeddings)

    concepts = {}
    for term, label in zip(terms, kmeans.labels_):
        concepts.setdefault(str(label), []).append(term)

    return concepts
