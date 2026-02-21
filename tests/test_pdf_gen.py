import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules import document_generator

messages = [
    {"role": "user", "content": "I was fired."},
    {"role": "assistant", "content": "That is terrible. When did it happen?"},
    {"role": "user", "content": "Yesterday."}
]

facts = {
    "timeline": ["2024/02/19: Fired"],
    "parties": ["User", "Company"],
    "main_issue": "Unfair dismissal",
    "evidence": ["None"],
    "user_desire": "Money",
    "missing_info": "Reason for dismissal"
}

try:
    output_path = document_generator.create_pdf_report(messages, facts)
    if output_path and os.path.exists(output_path):
        print(f"SUCCESS: PDF generated at: {output_path}")
    else:
        print("FAILURE: PDF path returned but file not found or None returned.")
except Exception as e:
    print(f"FAILURE: Exception occurred: {e}")
