import spacy
import numpy as np
import re
import wikipedia
import json
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import KMeans

nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Optimizations ---
SUMMARY_CACHE = {}

def clean_text(text):
    """Strips HTML tags, normalizes whitespace, and removes legal artifacts"""
    if not text: return ""
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove excessive punctuation/artifacts common in legal scans
    text = re.sub(r'\[\d+\]', '', text) # Remove citations like [1]
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


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
    k = min(5, len(terms))
    kmeans = KMeans(n_clusters=k, n_init="auto")
    kmeans.fit(embeddings)

    concepts = {}
    for term, label in zip(terms, kmeans.labels_):
        concepts.setdefault(str(label), []).append(term)

    return concepts

def analyze_case(text):
    doc = nlp(text)
    
    # Extract Entities
    entities = {}
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "DATE", "MONEY"]:
            entities.setdefault(ent.label_, []).append(ent.text)
    
    # Deduplicate lists
    for k in entities:
        entities[k] = list(set(entities[k]))

    # Analyze Legal Context (Basic Keyword Matching for Advice)
    advice = []
    preparation = []
    rights = []
    roadmap = []
    text_lower = text.lower()

    # Match predefined scenarios
    scenario_name, scenario_data = discover_scenario(text)
    if scenario_data:
        rights = scenario_data.get("rights", [])
        roadmap = scenario_data.get("roadmap", [])
        advice.append(f"Detected {scenario_name.upper()} context. Follow the provided checklist and roadmap.")

    # Additional ad-hoc checks
    if "contract" in text_lower or "agreement" in text_lower:
        advice.append("Review the termination clause and breach of contract terms.")
        preparation.append("Original signed agreement")
        preparation.append("Communication records (emails/letters) regarding the dispute")

    if "property" in text_lower or "land" in text_lower:
        advice.append("Verify property title deeds and encumbrance certificates.")
        preparation.append("sale deed / lease agreement")
        preparation.append("Property tax receipts")

    if "divorce" in text_lower or "custody" in text_lower:
        advice.append("Consult a family lawyer regarding custody rights and alimony.")
        preparation.append("Marriage certificate")
        preparation.append("Financial statements of both parties")
    
    if "criminal" in text_lower or "police" in text_lower or "fir" in text_lower:
        advice.append("IMMEDIATE: Apply for anticipatory bail if arrest is feared.")
        advice.append("Do not make statements to police without a lawyer present.")
        preparation.append("Copy of FIR (if available)")
        preparation.append("Character certificates")

    # Default if no specific keywords found
    if not advice:
        advice.append("Consult a general practitioner to understand the specific liabilities.")
        preparation.append("Timeline of events")
        preparation.append("List of witnesses")

    return {
        "entities": entities,
        "advice_steps": list(set(advice)),
        "documents_to_arrange": list(set(preparation)),
        "rights": rights,
        "roadmap": roadmap,
        "priority_actions": scenario_data.get("priority_actions", []) if scenario_data else [],
        "evidence_checklist": scenario_data.get("evidence_checklist", []) if scenario_data else [],
        "emergency_tips": scenario_data.get("emergency_tips", []) if scenario_data else [],
        "legal_aid_url": scenario_data.get("legal_aid_url", "") if scenario_data else "",
        "recommended_template": scenario_data.get("recommended_template", "") if scenario_data else "",
        "helplines": KNOW_YOUR_RIGHTS.get("helplines", []) if scenario_data else []
    }

import json
import os
import wikipedia

# Load Legal Definitions Dictionary
# Assuming data/legal_definitions.json exists relative to this file
DEFINITIONS_FILE = os.path.join(os.path.dirname(__file__), "data", "legal_definitions.json")
LEGAL_DEFINITIONS = {}

if os.path.exists(DEFINITIONS_FILE):
    try:
        with open(DEFINITIONS_FILE, "r", encoding="utf-8") as f:
            LEGAL_DEFINITIONS = json.load(f)
    except Exception as e:
        print(f"Error loading definitions: {e}")

# Load Rights & Roadmaps
RIGHTS_FILE = os.path.join(os.path.dirname(__file__), "data", "know_your_rights.json")
KNOW_YOUR_RIGHTS = {}

if os.path.exists(RIGHTS_FILE):
    try:
        with open(RIGHTS_FILE, "r", encoding="utf-8") as f:
            KNOW_YOUR_RIGHTS = json.load(f)
    except Exception as e:
        print(f"Error loading rights database: {e}")

def discover_scenario(text):
    """Identifies if a text matches any scenario in KNOW_YOUR_RIGHTS"""
    text_lower = text.lower()
    for name, data in KNOW_YOUR_RIGHTS.get("scenarios", {}).items():
        if any(keyword in text_lower for keyword in data.get("keywords", [])):
            return name, data
    return None, None

def generate_summary(query, texts):
    """
    Generates a high-quality topic overview using:
    0. Internal Cache (Speed)
    1. Rights & Roadmap Database (Priority)
    2. Local Dictionary (Precision)
    3. Wikipedia (Broad Knowledge)
    4. Semantic Extractive Summarization (Fallback)
    """
    query_clean = query.strip()
    query_lower = query_clean.lower()

    # 1. Check Performance Cache
    if query_lower in SUMMARY_CACHE:
        return SUMMARY_CACHE[query_lower]

    # 2. Check Rights Database
    scenario_name, scenario_data = discover_scenario(query_lower)
    if scenario_data:
        rights_summary = f"Detected {scenario_name.upper()} context. "
        if scenario_data.get("rights"):
             rights_summary += f"Key Rights: {scenario_data['rights'][0]} "
        res = {
            "text": rights_summary,
            "rights": scenario_data.get("rights", []),
            "roadmap": scenario_data.get("roadmap", []),
            "priority_actions": scenario_data.get("priority_actions", []),
            "evidence_checklist": scenario_data.get("evidence_checklist", []),
            "emergency_tips": scenario_data.get("emergency_tips", []),
            "legal_aid_url": scenario_data.get("legal_aid_url", ""),
            "recommended_template": scenario_data.get("recommended_template", ""),
            "helplines": KNOW_YOUR_RIGHTS.get("helplines", [])
        }
        SUMMARY_CACHE[query_lower] = res
        return res
    
    res_text = None
    
    # 3. Check Local Dictionary (Hand-crafted)
    if query_lower in LEGAL_DEFINITIONS:
        res_text = LEGAL_DEFINITIONS[query_lower]
    else:
        for key, val in LEGAL_DEFINITIONS.items():
            if key in query_lower or query_lower in key:
                if len(key) > 4: 
                    res_text = val
                    break

    # 4. Check Wikipedia
    if not res_text:
        try:
            wiki_summary = wikipedia.summary(query_clean, sentences=2)
            if wiki_summary:
                res_text = clean_text(wiki_summary)
        except Exception:
            pass

    # 5. Semantic Extractive Summarization (Fallback)
    if not res_text and texts:
        # Pre-process texts (cleaning HTML)
        cleaned_texts = [clean_text(t) for t in texts if len(t) > 40]
        if len(cleaned_texts) > 20:
            cleaned_texts = cleaned_texts[:20]

        if cleaned_texts:
            # Semantic Ranking
            query_embedding = model.encode(query_lower, convert_to_tensor=True)
            
            sentences = []
            for t in cleaned_texts:
                doc = nlp(t)
                # Filter out too specific case sentences ("The petitioner...", "The court finds...")
                for sent in doc.sents:
                    s_text = sent.text.strip()
                    if 40 < len(s_text) < 350:
                        l_text = s_text.lower()
                        if not any(stop in l_text for stop in ["petitioner", "respondent", "affidavit", "i.a. no", "dated"]):
                            sentences.append(s_text)
            
            if sentences:
                # Remove duplicates
                sentences = list(dict.fromkeys(sentences))
                
                sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
                cosine_scores = util.cos_sim(query_embedding, sentence_embeddings)[0]
                
                # Boost sentences that look like definitions or explanations
                final_scores = []
                for idx, score in enumerate(cosine_scores):
                    s_text = sentences[idx]
                    boost = 0
                    if any(term in s_text.lower() for term in ["is defined", "means", "refers to", "provides that", "stipulates"]):
                        boost += 0.15
                    if any(term in s_text.lower() for term in ["article", "section", "clause"]):
                        boost += 0.1
                    final_scores.append(score + boost)
                
                final_scores = np.array(final_scores)
                
                # Get top 2 unique high-scoring sentences
                top_results = np.argpartition(-final_scores, range(min(3, len(sentences))))[:3]
                
                summary_sents = []
                for idx in top_results:
                    if final_scores[idx] > 0.35:
                        summary_sents.append(sentences[idx])
                
                if summary_sents:
                    res_text = " ".join(summary_sents[:2])

    if res_text:
        # Final Polish
        res_text = clean_text(res_text)
        # Ensure it ends with a period
        if not res_text.endswith("."):
            res_text += "."
            
        res = {"text": res_text}
        SUMMARY_CACHE[query_lower] = res
        return res
        
    return None
