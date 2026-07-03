from google import genai
from google.genai import types
import json
import os
from dotenv import load_dotenv
from orchestrator import handle_intent

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

SYSTEM_PROMPT = """
You are MedMinder, an AI medication coordination agent.

Your job is to understand what the user wants and return ONLY a JSON object with this structure:
{
  "intent": one of [view_schedule, add_med, remove_med, caregiver_summary, safety_check],
  "params": {
    "drug": "drug name if mentioned",
    "dose": "dosage if mentioned",
    "times": ["HH:MM"] list of times if mentioned, else ["08:00"]
  }
}

Rules:
- Return ONLY valid JSON. No explanation, no markdown, no backticks.
- If user says "morning" → "08:00", "afternoon" → "13:00", "night" or "evening" → "20:00"
- If no dose mentioned, use null
- If intent is view_schedule or caregiver_summary, params can be empty {}

Examples:
User: "add warfarin 5mg at night"
→ {"intent": "add_med", "params": {"drug": "Warfarin", "dose": "5mg", "times": ["20:00"]}}

User: "what's my schedule today"
→ {"intent": "view_schedule", "params": {}}

User: "remove aspirin"
→ {"intent": "remove_med", "params": {"drug": "Aspirin"}}

User: "is ibuprofen safe for me"
→ {"intent": "safety_check", "params": {"drug": "Ibuprofen"}}

User: "show caregiver report"
→ {"intent": "caregiver_summary", "params": {}}
"""

def parse_intent(user_message: str) -> dict:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1
        )
    )
    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def chat():
    print("=== MedMinder Agent ===")
    print("Type your message (or 'quit' to exit)\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["quit", "exit"]:
            break
        if not user_input:
            continue

        try:
            parsed = parse_intent(user_input)
            intent = parsed.get("intent")
            params = parsed.get("params", {})
            result = handle_intent(intent, params)
            print(f"MedMinder: {result}\n")

        except json.JSONDecodeError:
            print("MedMinder: Sorry, I didn't understand that. Try again.\n")
        except Exception as e:
            print(f"MedMinder: Error — {e}\n")


if __name__ == "__main__":
    chat()