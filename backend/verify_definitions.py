import sys
import os

# Ensure backend path is in sys.path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from nlp import generate_summary

def test_definitions():
    print("\n[Testing Enhanced Definitions]")
    
    # Test 1: Dictionary Term
    term1 = "quo warranto"
    print(f"\nQuery: {term1}")
    summary1 = generate_summary(term1, [])
    print(f"Result (Should be from Dict): {summary1}")
    if "writ used to challenge" in summary1:
        print("PASS: Retrieved from Dictionary.")
    else:
        print("FAIL: Dictionary lookup failed.")

    # Test 2: Wikipedia Term (Not in Dictionary)
    term2 = "Tesla Inc" # Non-legal term to test wiki, or use "Contracts"
    print(f"\nQuery: {term2}")
    try:
        summary2 = generate_summary(term2, [])
        print(f"Result (Should be from Wiki): {summary2[:100]}...")
        if summary2:
            print("PASS: Retrieved from Wikipedia.")
    except Exception as e:
        print(f"FAIL: Wikipedia lookup error: {e}")

if __name__ == "__main__":
    test_definitions()
