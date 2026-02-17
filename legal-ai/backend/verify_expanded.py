import requests

url = "http://127.0.0.1:8000/analyze"

def test_text_input():
    print("\n[Testing Text Input]")
    payload = {"text_input": "I have a dispute regarding a breach of contract with my supplier who failed to deliver goods on time."}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Success!")
            data = response.json()
            print("Advice:", data['analysis'].get('advice_steps')[:1])
        else:
            print("Failed:", response.status_code, response.text)
    except Exception as e:
        print("Error:", e)

def test_url_input():
    print("\n[Testing URL Input]")
    # Using a reliable government URL or similar (using example.com for safety, scraper might return limited text but should work)
    payload = {"url": "https://example.com"} 
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Success!")
            data = response.json()
            print("Entities:", data['analysis'].get('entities'))
        else:
            print("Failed:", response.status_code, response.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_text_input()
    test_url_input()
