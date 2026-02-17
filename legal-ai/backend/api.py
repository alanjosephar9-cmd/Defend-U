from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import shutil
import os
from pdf_to_text import extract_text
from ocr import extract_from_image
from scraper import scrape_url
from translator import translate_text, translate_list

load_dotenv()

from search import search
from engine import extract_terms, build_concepts
from graph import store
from kanoon import search_kanoon, get_document
from nlp import generate_summary

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all frontends
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str
    lang: str = "en"

@app.get("/")
def home():
    return {"status": "Defend U backend running"}

@app.post("/ask")
def ask(q: Query):
    results = search(q.query)
    kanoon_results = search_kanoon(q.query)
    terms = extract_terms(results)
    concepts = build_concepts(terms)

    # Generate Topic Overview
    summary_pool = results + [doc.get("headline", "") for doc in kanoon_results.get("docs", [])]
    summary_data = generate_summary(q.query, summary_pool)
    
    summary = summary_data.get("text", "")
    rights = summary_data.get("rights", [])
    roadmap = summary_data.get("roadmap", [])
    emergency_tips = summary_data.get("emergency_tips", [])
    helplines = summary_data.get("helplines", [])

    # Translate if needed
    if q.lang and q.lang != 'en':
        summary = translate_text(summary, q.lang)
        results = translate_list(results, q.lang)
        rights = translate_list(rights, q.lang)
        roadmap = translate_list(roadmap, q.lang)
        emergency_tips = translate_list(emergency_tips, q.lang)
        
        # kanoon results translation
        for doc in kanoon_results.get("docs", []):
            if "headline" in doc:
                doc["headline"] = translate_text(doc["headline"], q.lang)
            if "title" in doc:
                doc["title"] = translate_text(doc["title"], q.lang)

    store(q.query, concepts)

    return {
        "query": q.query,
        "summary": summary,
        "rights": rights,
        "roadmap": roadmap,
        "priority_actions": summary_data.get("priority_actions", []),
        "evidence_checklist": summary_data.get("evidence_checklist", []),
        "emergency_tips": emergency_tips,
        "legal_aid_url": summary_data.get("legal_aid_url", ""),
        "recommended_template": summary_data.get("recommended_template", ""),
        "helplines": helplines,
        "local_results": results,
        "kanoon_results": kanoon_results.get("docs", []),
        "concepts": concepts
    }

@app.get("/templates")
def get_templates():
    """Returns available document templates"""
    return {
        "templates": [
            {"id": "police_complaint", "name": "Police Complaint Form"},
            {"id": "legal_notice", "name": "Legal Notice to Seller"},
            {"id": "rti_app", "name": "RTI Application Format"},
            {"id": "divorce_mutual", "name": "Mutual Consent Divorce Petition"}
        ]
    }

@app.get("/draft/{template_id}")
def draft_document(template_id: str, name: str = "NAME", details: str = "DETAILS"):
    """Generates a text-based document from a template"""
    templates = {
        "police_complaint": f"To,\nThe Station House Officer,\nPolice Station: [STATION]\n\nSubject: Formal Complaint regarding [SUBJECT]\n\nRespected Sir/Madam,\nI, {name}, resident of [ADDRESS], would like to lodge a formal complaint regarding {details}...\n\nSincerely,\n{name}",
        "legal_notice": f"LEGAL NOTICE\n\nTo,\n[OPPOSITE PARTY NAME]\n[ADDRESS]\n\nUnder instructions from my client, {name}, I hereby serve you with this legal notice regarding {details}...\n\nPlease resolve this within 15 days.",
        "rti_app": f"FORMAT OF RTI APPLICATION\n\nTo,\nThe Public Information Officer,\n[OFFICE NAME]\n\n1. Name of Applicant: {name}\n2. Information Required: {details}\n3. Period to which information relates: [PERIOD]\n4. Fee: ₹10 (enclosed)",
        "divorce_mutual": f"IN THE COURT OF THE PRINCIPAL JUDGE, FAMILY COURT\n\nPetition for dissolution of marriage by mutual consent under Section 13B of the Hindu Marriage Act.\n\nPetitioner 1: {name}\nPetitioner 2: [SPOUSE NAME]\n\nStatment of Facts: {details}..."
    }
    return {"content": templates.get(template_id, "Template not found.")}

@app.post("/analyze")
async def analyze_file(
    file: UploadFile = File(None),
    url: str = Form(None),
    text_input: str = Form(None),
    lang: str = Form('en')
):
    text = ""
    temp_file = None

    try:
        # Priority 1: Text Input
        if text_input:
             text = text_input
        
        # Priority 2: URL
        elif url:
             text = scrape_url(url)
        
        # Priority 3: File Upload
        elif file:
            temp_file = f"temp_{file.filename}"
            with open(temp_file, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            if temp_file.lower().endswith(".pdf"):
                text = extract_text(temp_file)
            elif temp_file.lower().endswith((".png", ".jpg", ".jpeg")):
                text = extract_from_image(temp_file)
            else:
                # Text file fallback
                with open(temp_file, "r", encoding="utf-8") as f:
                    text = f.read()

        if not text or len(text) < 10:
            return {"error": "No valid text could be extracted from the input."}

        # Run Analysis
        analysis = analyze_case(text)
        
        # Find Similar Precedents
        similar_texts = search(text[:500])
        kanoon_similar = search_kanoon(text[:200])
        
        # Translate Outputs
        if lang and lang != 'en':
            analysis['advice_steps'] = translate_list(analysis['advice_steps'], lang)
            analysis['documents_to_arrange'] = translate_list(analysis['documents_to_arrange'], lang)
            analysis['rights'] = translate_list(analysis.get('rights', []), lang)
            analysis['roadmap'] = translate_list(analysis.get('roadmap', []), lang)
            analysis['emergency_tips'] = translate_list(analysis.get('emergency_tips', []), lang)
            similar_texts = translate_list(similar_texts, lang)
            # Kanoon headlines
            for doc in kanoon_similar.get("docs", []):
                if "headline" in doc:
                    doc["headline"] = translate_text(doc["headline"], lang)
                if "title" in doc:
                    doc["title"] = translate_text(doc["title"], lang)

        return {
            "analysis": analysis,
            "similar_precedents": similar_texts,
            "kanoon_precedents": kanoon_similar.get("docs", [])[:3]
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        # Cleanup
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
