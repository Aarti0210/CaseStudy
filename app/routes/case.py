from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.jwt_utils import get_jwt_identity

from app.extensions import db
from app.middleware.rbac import roles_allowed
from app.models.audit import AuditLog
from app.models.case import Case

case_bp = Blueprint("case", __name__)


@case_bp.route("/create", methods=["POST"])
@jwt_required()
@roles_allowed("lawyer", "citizen", "admin")
def create_case():
    """Create a new case"""
    try:
        identity = get_jwt_identity()
        data = request.json or {}
        title = data.get("title")
        
        if not title:
            return jsonify({"message": "title is required", "success": False}), 400
        
        if len(title) > 200:
            return jsonify({"message": "title too long (max 200 chars)", "success": False}), 400

        description = data.get("description", "")
        case = Case(
            title=title,
            description=description,
            created_by=identity.get("id"),
            status="Pending"
        )
        db.session.add(case)
        db.session.flush()
        
        db.session.add(
            AuditLog(
                user_id=identity.get("id"),
                action="Created Case",
                case_id=case.id,
                details={"title": title}
            )
        )
        db.session.commit()
        
        return jsonify({
            "message": "Case created successfully",
            "success": True,
            "case": {
                "id": case.id,
                "title": case.title,
                "status": case.status,
                "created_at": case.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error creating case: {str(e)}", "success": False}), 500


@case_bp.route("", methods=["GET"])
@case_bp.route("/list", methods=["GET"])
@jwt_required()
def get_all_cases():
    """Get all cases"""
    try:
        identity = get_jwt_identity()
        user_id = identity.get("id")
        user_role = identity.get("role")
        
        # Admin sees all cases, others see their own
        if user_role == "admin":
            cases = Case.query.all()
        else:
            cases = Case.query.filter(
                (Case.created_by == user_id) | (Case.assigned_judge_id == user_id)
            ).all()
        
        return jsonify({
            "success": True,
            "count": len(cases),
            "cases": [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "status": c.status,
                    "created_at": c.created_at.isoformat(),
                    "created_by": c.created_by,
                    "assigned_judge_id": c.assigned_judge_id,
                }
                for c in cases
            ]
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching cases: {str(e)}", "success": False}), 500


@case_bp.route("/<int:case_id>", methods=["GET"])
@jwt_required()
def get_case(case_id):
    """Get a specific case"""
    try:
        identity = get_jwt_identity()
        case = Case.query.get(case_id)
        
        if not case:
            return jsonify({"message": "Case not found", "success": False}), 404
        
        # Check authorization
        user_id = identity.get("id")
        user_role = identity.get("role")
        if user_role != "admin" and case.created_by != user_id and case.assigned_judge_id != user_id:
            return jsonify({"message": "Access denied", "success": False}), 403
        
        return jsonify({
            "success": True,
            "case": {
                "id": case.id,
                "title": case.title,
                "description": case.description,
                "status": case.status,
                "created_at": case.created_at.isoformat(),
                "created_by": case.created_by,
                "assigned_judge_id": case.assigned_judge_id,
                "documents_count": len(case.documents.all()),
                "hearings_count": len(case.hearings.all()),
            }
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching case: {str(e)}", "success": False}), 500


@case_bp.route("/<int:case_id>", methods=["PUT"])
@jwt_required()
@roles_allowed("lawyer", "judge", "admin")
def update_case(case_id):
    """Update a case"""
    try:
        identity = get_jwt_identity()
        case = Case.query.get(case_id)
        
        if not case:
            return jsonify({"message": "Case not found", "success": False}), 404
        
        # Authorization check
        user_id = identity.get("id")
        user_role = identity.get("role")
        if user_role != "admin" and case.created_by != user_id:
            return jsonify({"message": "Access denied", "success": False}), 403
        
        data = request.json or {}
        
        if "title" in data:
            data["title"] = data["title"][:200]
            case.title = data["title"]
        if "description" in data:
            case.description = data["description"]
        if "status" in data:
            valid_status = ["Pending", "Active", "Closed", "On Hold"]
            if data["status"] in valid_status:
                case.status = data["status"]
        if "assigned_judge_id" in data:
            case.assigned_judge_id = data["assigned_judge_id"]
        
        db.session.add(
            AuditLog(
                user_id=user_id,
                action="Updated Case",
                case_id=case.id,
                details={"updated_fields": list(data.keys())}
            )
        )
        db.session.commit()
        
        return jsonify({
            "message": "Case updated successfully",
            "success": True,
            "case": {
                "id": case.id,
                "title": case.title,
                "status": case.status,
                "updated_at": datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating case: {str(e)}", "success": False}), 500


@case_bp.route("/<int:case_id>", methods=["DELETE"])
@jwt_required()
@roles_allowed("admin", "lawyer")
def delete_case(case_id):
    """Delete a case (admin only or creator)"""
    try:
        identity = get_jwt_identity()
        case = Case.query.get(case_id)
        
        if not case:
            return jsonify({"message": "Case not found", "success": False}), 404
        
        # Only admin or creator can delete
        user_id = identity.get("id")
        user_role = identity.get("role")
        if user_role != "admin" and case.created_by != user_id:
            return jsonify({"message": "Access denied", "success": False}), 403
        
        case_id = case.id
        db.session.delete(case)
        db.session.add(
            AuditLog(
                user_id=user_id,
                action="Deleted Case",
                case_id=case_id,
                details={"title": case.title}
            )
        )
        db.session.commit()
        
        return jsonify({
            "message": "Case deleted successfully",
            "success": True,
            "case_id": case_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting case: {str(e)}", "success": False}), 500


@case_bp.route("/<int:case_id>/assign-judge", methods=["POST"])
@jwt_required()
@roles_allowed("admin")
def assign_judge(case_id):
    """Assign a judge to a case"""
    try:
        data = request.json or {}
        judge_id = data.get("judge_id")
        
        if not judge_id:
            return jsonify({"message": "judge_id is required", "success": False}), 400
        
        case = Case.query.get(case_id)
        if not case:
            return jsonify({"message": "Case not found", "success": False}), 404
        
        identity = get_jwt_identity()
        case.assigned_judge_id = judge_id
        
        db.session.add(
            AuditLog(
                user_id=identity.get("id"),
                action="Assigned Judge to Case",
                case_id=case.id,
                details={"judge_id": judge_id}
            )
        )
        db.session.commit()
        
        return jsonify({
            "message": "Judge assigned successfully",
            "success": True,
            "case_id": case.id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error assigning judge: {str(e)}", "success": False}), 500
