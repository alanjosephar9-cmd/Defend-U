import os
import requests
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

API_TOKEN = os.getenv("KANOON_API_TOKEN")
BASE_URL = "https://api.indiankanoon.org"

def get_headers():
    if not API_TOKEN:
        return {}
    return {"Authorization": f"Token {API_TOKEN}"}

@lru_cache(maxsize=100)
def search_kanoon(query, pagenum=0):
    url = f"{BASE_URL}/search/"
    params = {
        "formInput": query,
        "pagenum": pagenum
    }
    
    try:
        response = requests.post(url, data=params, headers=get_headers(), timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching Kanoon: {e}")
        return {"error": str(e)}

def get_document(docid):
    url = f"{BASE_URL}/doc/{docid}/"
    
    try:
        response = requests.post(url, headers=get_headers(), timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching document {docid}: {e}")
        return {"error": str(e)}
