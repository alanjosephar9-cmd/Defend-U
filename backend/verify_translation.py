import requests
import json

url = "http://127.0.0.1:8000/ask"

def test_translation():
    print("\n[Testing Translation to Hindi]")
    payload = {"query": "murder", "lang": "hi"} 
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Success!")
            data = response.json()
            summary = data.get('summary')
            print(f"Summary (Hindi): {summary}")
            
            # Simple check if translation happened (heuristic: check for devanagari chars)
            if summary and any('\u0900' <= char <= '\u097F' for char in summary):
                print("Verified: Contains Hindi characters.")
            else:
                print("Warning: Does not seem to contain Hindi characters.")
                
        else:
            print("Failed:", response.status_code, response.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_translation()
