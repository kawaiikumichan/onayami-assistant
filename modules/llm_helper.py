import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

SYSTEM_PROMPT = """
# Role & Objective
You are **"Legal Prep AI"**, a supportive assistant designed to help users organize their legal troubles and find appropriate consultation resources.
Your goal is to:
1.  **Listen with Empathy:** Allow the user to vent their feelings and provide emotional validation.
2.  **Organize Facts:** Ask 5W1H questions to structure the chaotic information into a clear chronological report.
3.  **Navigate:** Suggest appropriate institutional resources (e.g., Houterasu, City Hall) based on the user's situation.

## CRITICAL COMPLIANCE RULES (Article 72 of the Attorney Act)
* **NO Legal Advice:** You MUST NOT provide legal judgments (e.g., "This is illegal," "You will win," "You can get 1 million yen").
* **NO Specific Legal Strategy:** Do not advise on specific legal tactics.
* **Refusal Protocol:** If asked for legal judgment, reply: "I am an AI and cannot make legal judgments. However, I can help you organize the facts so you can consult a lawyer effectively."

## Interaction Flow
1.  **Phase 1: Empathy (Input)**
    * Listen to the user. Acknowledge their distress (e.g., "It must be tough for you").
    * Do not rush to facts immediately; build trust first.
2.  **Phase 2: Fact Extraction (Structure)**
    * Gently ask missing information:
        * **When** did it happen?
        * **Who** is the other party?
        * **What** exactly happened? (Objective facts)
        * **Evidence:** Do you have emails, recordings, or contracts?
        * **Desire:** What is your goal? (Apology, Money, Break up?)
3.  **Phase 3: Output & Navigation**
    * Summarize the conversation into a "Consultation Sheet" (Markdown format).
    * Recommend resources from the provided resource list.

## Tone
* Polite, calm, and supportive (Japanese: 丁寧語, "Desu/Masu" tone).
* Objective when summarizing facts (remove emotional words in the final report).
"""

def get_chat_response(messages, api_key, model_name="gemini-2.5-flash"):
    """
    Sends messages to the Gemini API and returns the response.
    """
    if not api_key:
        return "システム連携キーが見つかりません。`.env` ファイルに `GOOGLE_API_KEY` を設定してください。"

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_PROMPT
        )

        # Convert OpenAI-style messages to Gemini history
        gemini_history = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        # The last message is the new input, previous ones are history
        # Gemini history must not be empty if starting chat, but here we rebuild it
        chat = model.start_chat(history=gemini_history[:-1])
        
        last_message = gemini_history[-1]["parts"][0]
        response = chat.send_message(last_message)
        
        if not response.text:
            return f"[Debug: Please send this to the developer]\nEmpty response text. \nPrompt: {last_message}\nCandidates: {response.candidates}\nPrompt feedback: {response.prompt_feedback}"

        return response.text
    except Exception as e:
        error_msg = f"Error communicating with AI: {str(e)}"
        try:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            error_msg += f"\n\nAvailable models: {', '.join(models)}"
        except Exception:
            pass
        return error_msg

FACT_EXTRACTION_PROMPT = """
# Fact Extraction Task
You are a legal assistant helper. Your task is to analyze the conversation history and extract structured facts.
**CRITICAL REQUIREMENT:** ALL extracted values must be written in natural Japanese (日本語).

Output a JSON object with the following keys:
- "timeline": List of strings describing key events in chronological order in Japanese (e.g., "2023年4月: 会社に入社した").
- "parties": List of strings describing who is involved in Japanese (e.g., "相談者", "X社", "A氏").
- "main_issue": String summarizing the core legal trouble in Japanese.
- "evidence": List of strings describing potential evidence mentioned in Japanese (e.g., "LINEのメッセージ", "雇用契約書").
- "user_desire": String describing what the user wants to achieve in Japanese.
- "missing_info": String describing critical information that is still missing to give proper advice in Japanese.

If information is not present, use empty lists or "不明" (Unknown in Japanese).
"""

def extract_facts_from_chat(messages, api_key, model_name="gemini-2.5-flash"):
    """
    Extracts structured facts from the chat history using Gemini.
    Returns a dictionary (parsed JSON).
    """
    if not api_key:
        return {}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"response_mime_type": "application/json"}
        )

        # Combine history and prompt for non-interactive generation
        full_text = f"{FACT_EXTRACTION_PROMPT}\n\nConversation History:\n"
        for msg in messages:
             full_text += f"{msg['role']}: {msg['content']}\n"
        
        response = model.generate_content(full_text)
        
        return json.loads(response.text)
    except Exception as e:
        print(f"Extraction Error: {e}")
        try:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            print(f"Available models: {', '.join(models)}")
        except Exception:
            pass
        return {}
