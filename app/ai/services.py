import hashlib
import os
import time
from datetime import datetime

from flask import current_app, request

from app.ai import ai_client
from app.ai.prompt_builder import *
from app.ai.response_formatter import error_response, standard_response
from app.extensions import db, limiter
from app.models.ai_log import AILog
from app.ml import predictor as ml_predictor
# for model metadata path
from app.ml.predict import META_FILE
import json

# simple in-memory cache with TTL
_CACHE = {}
_CACHE_TTL = int(current_app.config.get("AI_CACHE_TTL", 300)) if current_app else 300


def _cache_key(feature, payload):
    h = hashlib.sha256()
    h.update(feature.encode("utf-8"))
    h.update(repr(payload).encode("utf-8"))
    return h.hexdigest()


def _get_cached(key):
    entry = _CACHE.get(key)
    if not entry:
        return None
    ts, value = entry
    if time.time() - ts > _CACHE_TTL:
        del _CACHE[key]
        return None
    return value


def _set_cache(key, value):
    _CACHE[key] = (time.time(), value)


def _mask(data):
    """Return a redacted version of input for logging.
    Shallow mask for dicts and simple types.
    """
    if isinstance(data, dict):
        return {k: "***" for k in data.keys()}
    if isinstance(data, list):
        return ["***" for _ in data]
    # strings and others
    return "***"


def _log_ai(feature, user_id, role, prompt, response_text, usage, model, ip):
    try:
        # Do not store raw prompt or full response. Store masked placeholders only.
        log = AILog(
            user_id=user_id,
            role=role,
            feature_used=feature,
            prompt=_mask(prompt) if prompt is not None else None,
            response=_mask(response_text) if response_text is not None else None,
            model=model,
            language="en",
            prompt_tokens=usage.get("prompt_tokens") if usage else None,
            completion_tokens=usage.get("completion_tokens") if usage else None,
            total_tokens=usage.get("total_tokens") if usage else None,
            usage=None,
            token_usage=None,
            ip_address=(ip[:64] if ip else None),
            created_at=datetime.utcnow(),
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()


def _call_and_format(messages, feature, user_id=None, role=None, model=None):
    ip = request.remote_addr if request else None
    key = _cache_key(feature, messages)
    cached = _get_cached(key)
    if cached:
        return standard_response(feature, {"result": cached, "cached": True})

    start = time.time()
    try:
        resp = ai_client.call_openai_chat(messages, model=model)
        # extract content and usage
        try:
            content = resp.choices[0].message.content
        except (AttributeError, IndexError, TypeError):
            content = str(resp)
        
        usage = None
        try:
            usage = getattr(resp, "usage", None)
            if usage:
                usage = {
                    "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(usage, "completion_tokens", 0),
                    "total_tokens": getattr(usage, "total_tokens", 0),
                }
        except Exception:
            usage = None

        # store masked record only
        _log_ai(
            feature,
            user_id,
            role,
            _mask(messages),
            _mask(content),
            None,
            model or os.getenv("AI_MODEL", "gpt-4-turbo"),
            ip,
        )

        _set_cache(key, content)

        # structured minimal logging (no prompt/response)
        try:
            duration_ms = int((time.time() - start) * 1000)
            rid = request.headers.get("X-Request-ID") if request else None
            current_app.logger.info(
                {
                    "request_id": rid,
                    "endpoint": request.path if request else feature,
                    "user_id": user_id,
                    "feature": feature,
                    "duration_ms": duration_ms,
                    "status_code": 200,
                }
            )
        except Exception:
            pass

        return standard_response(
            feature,
            {
                "result": content,
                "usage": usage,
                "model": model or os.getenv("AI_MODEL", "gpt-4-turbo"),
            },
        )
    except RuntimeError as e:
        return error_response(feature, str(e), 500)
    except Exception as e:
        return error_response(feature, f"AI processing error: {str(e)}", 500)


# Feature wrappers
def explain_order(text, user_id=None, role=None, language="en"):
    prompt = explain_order_prompt(text, language=language)
    messages = [
        {
            "role": "system",
            "content": "You are a legal assistant. Simplify language for citizens.",
        },
        {"role": "user", "content": prompt},
    ]
    return _call_and_format(messages, "explain-order", user_id=user_id, role=role)


def case_summary(case_data, user_id=None, role=None, language="en"):
    prompt = case_summary_prompt(case_data, language=language)
    messages = [
        {"role": "system", "content": "You are a legal assistant."},
        {"role": "user", "content": prompt},
    ]
    return _call_and_format(messages, "case-summary", user_id=user_id, role=role)


def voice_search(transcript, user_id=None, role=None):
    prompt = voice_search_prompt(transcript)
    messages = [
        {"role": "system", "content": "Convert spoken input to search queries."},
        {"role": "user", "content": prompt},
    ]
    return _call_and_format(messages, "voice-search", user_id=user_id, role=role)


def draft_notice(client_name, case_type, facts, user_id=None, role=None, language="en"):
    prompt = draft_notice_prompt(client_name, case_type, facts, language=language)
    messages = [
        {"role": "system", "content": "Help draft legal notices."},
        {"role": "user", "content": prompt},
    ]
    return _call_and_format(messages, "draft-notice", user_id=user_id, role=role)


def evidence_summary(text, user_id=None, role=None, language="en"):
    prompt = evidence_summary_prompt(text, language=language)
    messages = [
        {"role": "system", "content": "Summarize evidence."},
        {"role": "user", "content": prompt},
    ]
    return _call_and_format(messages, "evidence-summary", user_id=user_id, role=role)


def strategy_suggestion(
    case_summary_text, opponent_claims, user_id=None, role=None, language="en"
):
    prompt = strategy_suggestion_prompt(
        case_summary_text, opponent_claims, language=language
    )
    messages = [
        {"role": "system", "content": "Provide advisory strategy suggestions."},
        {"role": "user", "content": prompt},
    ]
    return _call_and_format(messages, "strategy-suggestion", user_id=user_id, role=role)


def draft_judgment(
    case_summary_text,
    plaintiff_args,
    defendant_args,
    evidence_summary_text,
    user_id=None,
    role=None,
    language="en",
):
    prompt = draft_judgment_prompt(
        case_summary_text,
        plaintiff_args,
        defendant_args,
        evidence_summary_text,
        language=language,
    )
    messages = [
        {"role": "system", "content": "Assist judge with structuring judgments."},
        {"role": "user", "content": prompt},
    ]
    return _call_and_format(messages, "draft-judgment", user_id=user_id, role=role)


# new features defined after initial MVP

def predict_delay(case_data, user_id=None, role=None, language="en"):
    # deterministic ML predictor; if unavailable, return service error
    if not ml_predictor or not hasattr(ml_predictor, "predict") or ml_predictor.model is None:
        return error_response("predict-delay", "model unavailable", 503)

    # caching for ML results using same in-memory store as AI features
    key = _cache_key("predict-delay", case_data)
    cached = _get_cached(key)
    if cached is not None:
        return standard_response("predict-delay", {"result": cached, "cached": True})

    try:
        pred = ml_predictor.predict(case_data)
    except Exception as e:
        # model error
        return error_response("predict-delay", "prediction error", 503)

    # store in cache
    try:
        _set_cache(key, pred)
    except Exception:
        pass

    # log prediction (mask sensitive data)
    try:
        _log_ai(
            "predict-delay",
            user_id,
            role,
            _mask(case_data),
            _mask(pred),
            usage=None,
            model=pred.get("model_version") if isinstance(pred, dict) else None,
            ip=request.remote_addr if request else None,
        )
    except Exception:
        pass

    return standard_response("predict-delay", {"result": pred, "cached": False})


def judicial_intelligence(case_data, user_id=None, role=None, language="en"):
    prompt = judicial_intelligence_prompt(case_data, language=language)
    messages = [
        {"role": "system", "content": "You are a smart judicial intelligence assistant."},
        {"role": "user", "content": prompt},
    ]
    return _call_and_format(messages, "judicial-intelligence", user_id=user_id, role=role)


def detect_contradictions(plaintiff, defendant, user_id=None, role=None, language="en"):
    prompt = contradictions_prompt(plaintiff, defendant, language=language)
    messages = [
        {"role": "system", "content": "Detect contradictions."},
        {"role": "user", "content": prompt},
    ]
    return _call_and_format(
        messages, "detect-contradictions", user_id=user_id, role=role
    )


def model_info():
    """Return summary of the current ML model."""
    try:
        # prefer metadata already loaded by predictor if available
        meta = ml_predictor.meta
        if not meta:
            with open(META_FILE, "r", encoding="utf-8") as fh:
                meta = json.load(fh)
    except Exception as e:
        return error_response("model-info", "metadata unavailable", 500)

    metrics = meta.get("metrics", {})
    info = {
        "model_version": meta.get("model_version"),
        "algorithm": "RandomForestRegressor",
        "rmse": round(metrics.get("rmse", 0), 2),
        "mae": round(metrics.get("mae", 0), 2),
        "r2_score": round(metrics.get("r2", 0), 3),
        "training_samples": meta.get("dataset_size"),
        "features_used": meta.get("feature_list", []),
    }
    return standard_response("model-info", info)


def generate_timeline(events, user_id=None, role=None, language="en"):
    prompt = timeline_prompt(events, language=language)
    messages = [
        {"role": "system", "content": "Generate chronological timeline."},
        {"role": "user", "content": prompt},
    ]
    return _call_and_format(messages, "generate-timeline", user_id=user_id, role=role)


def system_summary(stats, user_id=None, role=None, language="en"):
    prompt = system_summary_prompt(stats, language=language)
    messages = [
        {"role": "system", "content": "Provide system analytics summary."},
        {"role": "user", "content": prompt},
    ]
    return _call_and_format(messages, "system-summary", user_id=user_id, role=role)
