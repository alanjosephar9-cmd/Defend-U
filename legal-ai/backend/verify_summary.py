import requests

url = "http://127.0.0.1:8000/ask"

def test_summary():
    print("\n[Testing Topic Summary]")
    payload = {"query": "murder"} 
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Success!")
            data = response.json()
            print("Summary:", data.get('summary'))
            if not data.get('summary'):
                 print("WARNING: No summary returned (might be lack of data/matches).")
            else:
                 print("Found summary length:", len(data.get('summary')))
        else:
            print("Failed:", response.status_code, response.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_summary()
