from flask import Blueprint, jsonify, request
from app.schemas import (
    ExplainOrderSchema,
    CaseSummarySchema,
    CaseDataSchema,
    BasicTextSchema,
    DraftNoticeSchema,
    EvidenceSummarySchema,
    StrategySuggestionSchema,
    PredictDelaySchema,
    validate_schema,
)
from flask_jwt_extended import jwt_required
from app.jwt_utils import get_jwt_identity

from app.ai import services as ai_services
from app.extensions import limiter
from app.middleware.rbac import roles_allowed

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/explain-order", methods=["POST"])
@jwt_required()
@limiter.limit("20 per hour")
@roles_allowed("citizen", "lawyer", "judge", "admin")
@validate_schema(ExplainOrderSchema)
def explain_order():
    data = request.get_json() or {}
    text = data.get("text")
    language = data.get("language", "en")
    identity = get_jwt_identity()
    res = ai_services.explain_order(
        text, user_id=identity.get("id"), role=identity.get("role"), language=language
    )
    return jsonify(res), 200


@ai_bp.route("/case-summary", methods=["POST"])
@jwt_required()
@limiter.limit("30 per hour")
@roles_allowed("citizen", "lawyer", "admin")
@validate_schema(CaseSummarySchema)
def case_summary():
    data = request.get_json() or {}
    case_data = data.get("case_data")
    language = data.get("language", "en")
    identity = get_jwt_identity()
    res = ai_services.case_summary(
        case_data,
        user_id=identity.get("id"),
        role=identity.get("role"),
        language=language,
    )
    return jsonify(res), 200


@ai_bp.route("/voice-search", methods=["POST"])
@jwt_required()
@limiter.limit("60 per hour")
@roles_allowed("citizen", "lawyer")
@validate_schema(BasicTextSchema)
def voice_search():
    data = request.get_json() or {}
    transcript = data.get("text")
    identity = get_jwt_identity()
    res = ai_services.voice_search(
        transcript, user_id=identity.get("id"), role=identity.get("role")
    )
    return jsonify(res), 200


@ai_bp.route("/draft-notice", methods=["POST"])
@jwt_required()
@limiter.limit("30 per hour")
@roles_allowed("lawyer")
@validate_schema(DraftNoticeSchema)
def draft_notice():
    data = request.get_json() or {}
    client_name = data.get("client_name")
    case_type = data.get("case_type")
    facts = data.get("facts")
    identity = get_jwt_identity()
    res = ai_services.draft_notice(
        client_name,
        case_type,
        facts,
        user_id=identity.get("id"),
        role=identity.get("role"),
    )
    return jsonify(res), 200


@ai_bp.route("/evidence-summary", methods=["POST"])
@jwt_required()
@limiter.limit("40 per hour")
@roles_allowed("lawyer")
@validate_schema(EvidenceSummarySchema)
def evidence_summary():
    data = request.get_json() or {}
    text = data.get("text")
    identity = get_jwt_identity()
    res = ai_services.evidence_summary(
        text, user_id=identity.get("id"), role=identity.get("role")
    )
    return jsonify(res), 200


@ai_bp.route("/strategy-suggestion", methods=["POST"])
@jwt_required()
@limiter.limit("20 per hour")
@roles_allowed("lawyer")
@validate_schema(StrategySuggestionSchema)
def strategy_suggestion():
    data = request.get_json() or {}
    case_summary_text = data.get("case_summary")
    opponent_claims = data.get("opponent_claims")
    identity = get_jwt_identity()
    res = ai_services.strategy_suggestion(
        case_summary_text,
        opponent_claims,
        user_id=identity.get("id"),
        role=identity.get("role"),
    )
    return jsonify(res), 200


@ai_bp.route("/draft-judgment", methods=["POST"])
@jwt_required()
@limiter.limit("10 per hour")
@roles_allowed("judge")
@validate_schema(ExplainOrderSchema)
def draft_judgment():
    data = request.get_json() or {}
    cs = data.get("case_summary")
    p_args = data.get("plaintiff_args")
    d_args = data.get("defendant_args")
    evidence = data.get("evidence_summary")
    identity = get_jwt_identity()
    res = ai_services.draft_judgment(
        cs,
        p_args,
        d_args,
        evidence,
        user_id=identity.get("id"),
        role=identity.get("role"),
    )
    return jsonify(res), 200


@ai_bp.route("/detect-contradictions", methods=["POST"])
@jwt_required()
@limiter.limit("30 per hour")
@roles_allowed("judge")
@validate_schema(StrategySuggestionSchema)
def detect_contradictions():
    data = request.get_json() or {}
    plaintiff = data.get("plaintiff")
    defendant = data.get("defendant")
    identity = get_jwt_identity()
    res = ai_services.detect_contradictions(
        plaintiff, defendant, user_id=identity.get("id"), role=identity.get("role")
    )
    return jsonify(res), 200


@ai_bp.route("/generate-timeline", methods=["POST"])
@jwt_required()
@limiter.limit("60 per hour")
@roles_allowed("judge", "lawyer")
@validate_schema(BasicTextSchema)
def generate_timeline():
    data = request.get_json() or {}
    events = data.get("events")
    identity = get_jwt_identity()
    res = ai_services.generate_timeline(
        events, user_id=identity.get("id"), role=identity.get("role")
    )
    return jsonify(res), 200


@ai_bp.route("/system-summary", methods=["POST"])
@jwt_required()
@limiter.limit("10 per hour")
@roles_allowed("admin")
@validate_schema(BasicTextSchema)
def system_summary():
    data = request.get_json() or {}
    stats = data.get("stats")
    identity = get_jwt_identity()
    res = ai_services.system_summary(
        stats, user_id=identity.get("id"), role=identity.get("role")
    )
    return jsonify(res), 200


# new endpoints
@ai_bp.route("/predict-delay", methods=["POST"])
@jwt_required()
# apply stricter per-user rate limit: 10 per minute per user
@limiter.limit("10 per minute", key_func=lambda: (get_jwt_identity() or {}).get("id") or request.remote_addr)
@roles_allowed("lawyer", "judge", "admin")
@validate_schema(PredictDelaySchema)
def predict_delay():
    # validation decorator ensures payload valid
    data = request.get_json() or {}
    case_data = data.get("case_data")
    identity = get_jwt_identity()
    res = ai_services.predict_delay(
        case_data, user_id=identity.get("id"), role=identity.get("role")
    )
    return jsonify(res), 200


@ai_bp.route("/judicial-intelligence", methods=["POST"])
@jwt_required()
@limiter.limit("10 per hour")
@roles_allowed("lawyer", "judge", "admin")
def judicial_intelligence():
    data = request.get_json() or {}
    case_data = data.get("case_data")
    if not case_data:
        return (
            jsonify(ai_services.error_response("judicial-intelligence", "case_data required")),
            400,
        )
    identity = get_jwt_identity()
    res = ai_services.judicial_intelligence(
        case_data, user_id=identity.get("id"), role=identity.get("role")
    )
    return jsonify(res), 200


@ai_bp.route("/model-info", methods=["GET"])
@jwt_required()
@roles_allowed("admin")
def model_info():
    # only admins can see model metadata
    res = ai_services.model_info()
    return jsonify(res), 200


@ai_bp.route("/health", methods=["GET"])
def health():
    from app.extensions import db
    from app.ml import predictor
    status = {"db": False, "model": False}
    try:
        db.session.execute("SELECT 1")
        status["db"] = True
    except Exception:
        status["db"] = False
    status["model"] = bool(getattr(predictor, "model", None))
    overall = "ok" if all(status.values()) else "degraded"
    return jsonify({"status": overall, "checks": status}), 200 if overall == "ok" else 503
