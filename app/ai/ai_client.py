import os

from flask import current_app
from requests.exceptions import Timeout

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

DEFAULT_MODEL = os.getenv("AI_MODEL", "gpt-4-turbo")
DEFAULT_TIMEOUT = int(os.getenv("AI_TIMEOUT_SECONDS", 30))
MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", 2000))


def call_openai_chat(
    messages, model=None, timeout=DEFAULT_TIMEOUT, max_tokens=MAX_TOKENS
):
    """Call OpenAI Chat API with modern client"""
    if not HAS_OPENAI:
        raise RuntimeError("OpenAI package not installed. Install with: pip install openai")
    
    model = model or DEFAULT_MODEL
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise RuntimeError("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
    
    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        return resp
    except Timeout as e:
        raise RuntimeError(f"OpenAI API timeout after {timeout}s: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")
