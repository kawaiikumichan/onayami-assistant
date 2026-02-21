import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

genai.configure(api_key=api_key)
try:
    model = genai.GenerativeModel("gemini-3-flash-preview")
    response = model.generate_content("Hello")
    print("Response text:", response.text)
    print("Full response object:", dir(response))
    if hasattr(response, 'candidates'):
        print("Candidates:", response.candidates)
except Exception as e:
    print("Error:", e)
