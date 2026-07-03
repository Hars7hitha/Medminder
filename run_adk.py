import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from adk_agents.medminder_adk import medminder_agent

session_service = InMemorySessionService()
runner = Runner(
    agent=medminder_agent,
    app_name="medminder",
    session_service=session_service
)

async def chat():
    print("=== MedMinder ADK Agent ===\n")
    session = await session_service.create_session(
        app_name="medminder",
        user_id="user_001"
    )

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["quit", "exit"]:
            break
        if not user_input:
            continue

        response_text = ""
        async for event in runner.run_async(
            user_id="user_001",
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=user_input)]
            )
        ):
            if event.is_final_response():
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        response_text += part.text

        print(f"MedMinder: {response_text}\n")

if __name__ == "__main__":
    asyncio.run(chat())