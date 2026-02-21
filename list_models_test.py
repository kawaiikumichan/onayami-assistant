import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY") # Or we can just configure if there's no API key... 
if not api_key:
    # Try getting it from the other conversation or assume the user's environment might not have it in this script. Wait, the error happened during app execution, which has the key.
    # Without API key, list_models requires one.
    pass

# We will just print the error if no key, but list models if we can.
genai.configure(api_key=api_key)
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(e)
