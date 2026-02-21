import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock
sys.modules["streamlit"] = MagicMock()

from modules import legal_logic, document_generator

def test_recommendations():
    print("Testing recommendations...")
    # Test case 1: Financial aid
    req = "お金がない"
    recs = legal_logic.get_recommendations(req)
    found = any("法テラス" in r["name"] for r in recs)
    if found:
        print("PASS: Recommended Houterasu for financial issues.")
    else:
        print("FAIL: Did not recommend Houterasu.")

    # Test case 2: Labor issue
    req = "残業代が支払われない"
    recs = legal_logic.get_recommendations(req)
    found = any("労働基準監督署" in r["name"] for r in recs)
    if found:
        print("PASS: Recommended Labor Standards Office.")
    else:
        print("FAIL: Did not recommend Labor Standards Office.")

def test_pdf_generation():
    print("\nTesting PDF generation...")
    messages = [
        {"role": "user", "content": "私は詐欺に遭いました。"},
        {"role": "assistant", "content": "それは大変でしたね。詳しい状況を教えていただけますか？"},
        {"role": "user", "content": "2024年1月にX社と契約しました。"},
    ]
    
    path = document_generator.create_pdf_report(messages)
    if path and os.path.exists(path):
        print(f"PASS: PDF created at {path}")
    else:
        print("FAIL: PDF generation failed.")

if __name__ == "__main__":
    test_recommendations()
    test_pdf_generation()
