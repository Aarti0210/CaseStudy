from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.middleware.rbac import roles_allowed
from app.models.case import Case
from app.models.case_activity import CaseActivity

activity_bp = Blueprint("activity", __name__)


@activity_bp.route("/case/<int:case_id>", methods=["GET"])
@jwt_required()
def get_case_activity(case_id):
    """Get all activities for a case"""
    try:
        Case.query.get_or_404(case_id)
        
        activities = (
            CaseActivity.query.filter_by(case_id=case_id)
            .order_by(CaseActivity.created_at.desc())
            .all()
        )

        return jsonify({
            "success": True,
            "case_id": case_id,
            "count": len(activities),
            "activities": [
                {
                    "id": a.id,
                    "action": a.action,
                    "description": a.description,
                    "user_id": a.user_id,
                    "created_at": a.created_at.isoformat() if a.created_at else None
                }
                for a in activities
            ]
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching activity: {str(e)}", "success": False}), 500


@activity_bp.route("", methods=["POST"])
@jwt_required()
@roles_allowed("lawyer", "judge", "admin")
def log_activity():
    """Log a case activity"""
    try:
        identity = get_jwt_identity()
        data = request.json or {}
        
        case_id = data.get("case_id")
        action = data.get("action")
        description = data.get("description", "")
        
        if not all([case_id, action]):
            return jsonify({
                "message": "case_id and action are required",
                "success": False
            }), 400
        
        Case.query.get_or_404(case_id)
        
        activity = CaseActivity(
            case_id=case_id,
            user_id=identity.get("id"),
            action=action,
            description=description,
            created_at=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            "message": "Activity logged successfully",
            "success": True,
            "activity": {
                "id": activity.id,
                "case_id": activity.case_id,
                "action": activity.action,
                "created_at": activity.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error logging activity: {str(e)}", "success": False}), 500
