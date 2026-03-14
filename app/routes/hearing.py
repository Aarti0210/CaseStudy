from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.jwt_utils import get_jwt_identity

from app.extensions import db
from app.middleware.rbac import role_required, roles_allowed
from app.models.audit import AuditLog
from app.models.case import Case
from app.models.hearing import Hearing
from app.utils.api_response import success_response, error_response

hearing_bp = Blueprint("hearing", __name__)


@hearing_bp.route("/schedule", methods=["POST"])
@jwt_required()
@role_required("judge")
def schedule():
    """Schedule a hearing for a case"""
    try:
        identity = get_jwt_identity()
        data = request.json or {}
        
        case_id = data.get("case_id")
        hearing_date_str = data.get("hearing_date")
        
        if not all([case_id, hearing_date_str]):
            return error_response(
                "case_id and hearing_date (ISO format) are required", 400
            )
        
        # Validate case exists
        case = Case.query.get(case_id)
        if not case:
            return error_response("Case not found", 404)
        
        # Parse date
        try:
            hearing_date = datetime.fromisoformat(hearing_date_str)
        except ValueError:
            return error_response(
                "Invalid hearing_date format. Use ISO format (YYYY-MM-DD HH:MM:SS)",
                400,
            )
        
        hearing = Hearing(
            case_id=case_id,
            hearing_date=hearing_date,
            judge_id=identity.get("id"),
            status="Scheduled",
            notes=data.get("notes", ""),
            created_by=identity.get("id")
        )
        db.session.add(hearing)
        db.session.flush()
        
        db.session.add(
            AuditLog(
                user_id=identity.get("id"),
                action="Scheduled Hearing",
                case_id=case_id,
                details={"hearing_id": hearing.id, "hearing_date": hearing_date_str}
            )
        )
        db.session.commit()
        
        return success_response(
            data={
                "hearing": {
                    "id": hearing.id,
                    "case_id": hearing.case_id,
                    "hearing_date": hearing.hearing_date.isoformat(),
                    "status": hearing.status,
                }
            },
            message="Hearing scheduled successfully",
            status_code=201,
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error scheduling hearing: {str(e)}", 500)


@hearing_bp.route("/<int:case_id>", methods=["GET"])
@jwt_required()
def get_case_hearings(case_id):
    """Get all hearings for a case"""
    try:
        Case.query.get_or_404(case_id)
        hearings = Hearing.query.filter_by(case_id=case_id).order_by(Hearing.hearing_date).all()
        
        return success_response(
            data={
                "case_id": case_id,
                "count": len(hearings),
                "hearings": [
                    {
                        "id": h.id,
                        "hearing_date": h.hearing_date.isoformat(),
                        "judge_id": h.judge_id,
                        "status": h.status,
                        "notes": h.notes,
                        "created_at": h.created_at.isoformat(),
                    }
                    for h in hearings
                ],
            }
        )
    except Exception as e:
        return error_response(f"Error fetching hearings: {str(e)}", 500)


# new route for suggesting optimal slots
@hearing_bp.route("/suggest", methods=["POST"])
@jwt_required()
def suggest_hearing():
    """Return suggested hearing slots for a case using smart scheduler"""
    data = request.json or {}
    case_id = data.get("case_id")
    if not case_id:
        return error_response("case_id required", 400)

    from app.services import smart_scheduler

    suggestions = smart_scheduler.suggest_optimal_hearing(case_id)
    return success_response(data={"suggestions": suggestions})


@hearing_bp.route("/<int:hearing_id>", methods=["PUT"])
@jwt_required()
@role_required("judge")
def update_hearing(hearing_id):
    """Update hearing details"""
    try:
        identity = get_jwt_identity()
        hearing = Hearing.query.get(hearing_id)
        
        if not hearing:
            return error_response("Hearing not found", 404)
        
        data = request.json or {}
        
        if "status" in data:
            valid_status = ["Scheduled", "Completed", "Cancelled", "Postponed"]
            if data["status"] in valid_status:
                hearing.status = data["status"]
        
        if "notes" in data:
            hearing.notes = data["notes"]
        
        db.session.add(
            AuditLog(
                user_id=identity.get("id"),
                action="Updated Hearing",
                case_id=hearing.case_id,
                details={"hearing_id": hearing_id}
            )
        )
        db.session.commit()
        
        return success_response(
            data={
                "hearing": {
                    "id": hearing.id,
                    "status": hearing.status,
                    "updated_at": datetime.utcnow().isoformat(),
                }
            },
            message="Hearing updated successfully",
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating hearing: {str(e)}", 500)


@hearing_bp.route("/<int:hearing_id>", methods=["DELETE"])
@jwt_required()
@role_required("judge")
def delete_hearing(hearing_id):
    """Delete a hearing"""
    try:
        identity = get_jwt_identity()
        hearing = Hearing.query.get(hearing_id)
        
        if not hearing:
            return error_response("Hearing not found", 404)
        
        case_id = hearing.case_id
        db.session.delete(hearing)
        db.session.add(
            AuditLog(
                user_id=identity.get("id"),
                action="Deleted Hearing",
                case_id=case_id,
                details={"hearing_id": hearing_id}
            )
        )
        db.session.commit()
        
        return success_response(
            data={"hearing_id": hearing_id}, message="Hearing deleted successfully"
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error deleting hearing: {str(e)}", 500)
