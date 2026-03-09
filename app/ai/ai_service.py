import os
import time
from datetime import datetime

from app.extensions import db
from app.models.ai_log import AILog
from app.ai import ai_client
from app.ai import prompt_builder

# configuration constants
CACHE_TTL = int(os.getenv("AI_CACHE_TTL_SECONDS", 86400))  # 24 hours by default
MAX_PROMPT_LENGTH = int(os.getenv("AI_MAX_PROMPT_LENGTH", 4000))  # characters

# simple in‑memory cache: {(feature,prompt,model,lang): {"resp":...,"ts":...}}
_cache = {}


def _make_cache_key(feature, prompt, model, language):
    return f"{feature}|{model}|{language}|{prompt}"


def _get_cached(feature, prompt, model, language):
    key = _make_cache_key(feature, prompt, model, language)
    entry = _cache.get(key)
    if entry and time.time() - entry["ts"] < CACHE_TTL:
        return entry["resp"]
    return None


def _set_cache(feature, prompt, model, language, resp):
    key = _make_cache_key(feature, prompt, model, language)
    _cache[key] = {"resp": resp, "ts": time.time()}


def generate_ai_response(
    prompt, user_id=None, case_id=None, model_name=None, language="en", feature="generic"
):
    """Central method for OpenAI calls with caching, limits and logging."""
    if MAX_PROMPT_LENGTH and len(prompt) > MAX_PROMPT_LENGTH:
        raise ValueError("Prompt too long, please shorten the input.")

    model_name = model_name or os.getenv("AI_MODEL", "gpt-4")

    # return cached answer if available
    cached = _get_cached(feature, prompt, model_name, language)
    if cached is not None:
        return cached

    messages = [
        {"role": "system", "content": "You are a legal assistant AI."},
        {"role": "user", "content": prompt},
    ]

    resp = ai_client.call_openai_chat(
        messages,
        model=model_name,
        timeout=int(os.getenv("AI_TIMEOUT_SECONDS", 30)),
        max_tokens=int(os.getenv("AI_MAX_TOKENS", 2000)),
    )

    # parse output
    content = resp.choices[0].message.get("content") if hasattr(resp, "choices") else None
    usage = getattr(resp, "usage", None) or resp.get("usage") if isinstance(resp, dict) else None
    prompt_tokens = completion_tokens = total_tokens = None
    if usage:
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")

    result = {"content": content, "usage": usage, "model": model_name}

    # cache result
    _set_cache(feature, prompt, model_name, language, result)

    # persist log
    try:
        log = AILog(
            user_id=user_id,
            case_id=case_id,
            prompt=prompt,
            response=content,
            model=model_name,
            language=language,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            usage=usage,
            created_at=datetime.utcnow(),
            feature_used=feature,
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return result


# additional helper features

def predict_delay(case_data, user_id=None, case_id=None, language="en"):
    prompt = prompt_builder.delay_prediction_prompt(case_data, language)
    return generate_ai_response(
        prompt,
        user_id=user_id,
        case_id=case_id,
        language=language,
        feature="delay_prediction",
    )


def judicial_intelligence(case_data, user_id=None, case_id=None, language="en"):
    prompt = prompt_builder.judicial_intelligence_prompt(case_data, language)
    return generate_ai_response(
        prompt,
        user_id=user_id,
        case_id=case_id,
        language=language,
        feature="judicial_intelligence",
    )


def explain_court_order(text, user_id=None, case_id=None, language="en"):
    prompt = prompt_builder.explain_order_prompt(text, language)
    return generate_ai_response(
        prompt,
        user_id=user_id,
        case_id=case_id,
        language=language,
        feature="explain_order",
    )


def summarize_case(text, user_id=None, case_id=None, language="en"):
    prompt = prompt_builder.case_summary_prompt(text, language)
    return generate_ai_response(
        prompt,
        user_id=user_id,
        case_id=case_id,
        language=language,
        feature="case_summary",
    )


def draft_judgment_suggestion(text, user_id=None, case_id=None, language="en"):
    prompt = prompt_builder.draft_judgment_prompt(text, None, None, None, language)
    # the helper above expects multiple args so we just feed text through first parameter for compatibility
    return generate_ai_response(
        prompt,
        user_id=user_id,
        case_id=case_id,
        language=language,
        feature="draft_judgment",
    )
