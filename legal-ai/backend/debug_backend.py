import requests
import sys

URL = "http://127.0.0.1:8000"

def check_backend():
    print(f"Checking backend at {URL}...")
    try:
        # Check Root
        resp = requests.get(f"{URL}/", timeout=2)
        print(f"Root / status: {resp.status_code}")
        print(f"Root response: {resp.json()}")
        
        # Check Ask Endpoint with a simple query
        print("\nChecking /ask endpoint...")
        payload = {"query": "test", "lang": "en"}
        resp = requests.post(f"{URL}/ask", json=payload, timeout=5)
        print(f"/ask status: {resp.status_code}")
        if resp.status_code == 200:
            print("/ask functional.")
        else:
            print(f"/ask failed: {resp.text}")

    except requests.exceptions.ConnectionError:
        print("CRITICAL: Connection refused. processing is likely not running.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_backend()
