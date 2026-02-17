import requests

url = "http://127.0.0.1:8000/analyze"

# Create a dummy case file
dummy_content = """
AGREEMENT FOR SALE
This Agreement for Sale is made on this 10th day of January, 2023 between Mr. John Doe (Vendor) and Mr. Smith (Purchaser).
Whereas the Vendor is the owner of the property located at 123 Legal Lane.
And whereas a dispute has arisen regarding the breach of contract and non-payment of the token amount.
The parties hereby agree to settle the matter in court.
"""

with open("test_case.txt", "w") as f:
    f.write(dummy_content)

files = {'file': ('test_case.txt', open('test_case.txt', 'rb'), 'text/plain')}

try:
    print("Testing /analyze endpoint...")
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        print("Success!")
        data = response.json()
        print("Advice:", data['analysis'].get('advice_steps'))
        print("Entities:", data['analysis'].get('entities'))
        print("Kanoon Precedents Found:", len(data.get('kanoon_precedents', [])))
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
