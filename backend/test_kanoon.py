from kanoon import search_kanoon, get_document
import os
from dotenv import load_dotenv

load_dotenv()

print(f"Token present: {bool(os.getenv('KANOON_API_TOKEN'))}")

print("Testing Search...")
search_res = search_kanoon("contract law", pagenum=0)
if "error" in search_res:
    print("Search Error:", search_res["error"])
else:
    print("Search Success. Found docs:", len(search_res.get("docs", [])))
    if search_res.get("docs"):
        first_doc_id = search_res["docs"][0]["tid"]
        print(f"Testing Doc Fetch (ID: {first_doc_id})...")
        doc_res = get_document(first_doc_id)
        if "error" in doc_res:
             print("Doc Fetch Error:", doc_res["error"])
        else:
             print("Doc Fetch Success. Title:", doc_res.get("title", "Unknown"))
