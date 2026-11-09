"""Wrapper around the Google Gemini API. Every agent calls chat()."""
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("MODEL_NAME", "gemini-3.5-flash")
_client = None


def get_client():
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY missing. Add it to the .env file.")
        _client = genai.Client(api_key=key)
    return _client


def chat(system: str, messages: list, max_tokens: int = 1500) -> str:
    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["content"])],
        )
        for m in messages
    ]
    resp = get_client().models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system),
    )
    return resp.text or ""