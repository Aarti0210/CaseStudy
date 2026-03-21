"""
Case management routes module.
Handles CRUD operations for legal cases.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.jwt_utils import get_jwt_identity
from app.extensions import db
from app.middleware.rbac import roles_allowed
from app.models.case import Case
from app.models.user import User
from app.utils.api_response import success_response, error_response
from app.utils.database import safe_commit, safe_add, get_by_id, paginate_query
from app.utils.validators import validate_required_fields, validate_string_length
from app.services.audit_service import log_case_action

case_bp = Blueprint("case", __name__)


def _validate_case_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate case data."""
    required_fields = ["title"]
    missing = validate_required_fields(data, required_fields)
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    if not validate_string_length(data.get("title", ""), 1, 200):
        return False, "Title must be between 1 and 200 characters"
    
    if not validate_string_length(data.get("description", ""), 0, 2000):
        return False, "Description must be less than 2000 characters"
    
    return True, ""


@case_bp.route("/create", methods=["POST"])
@jwt_required()
@roles_allowed("lawyer", "citizen", "admin")
def create_case():
    """Create a new case."""
    try:
        identity = get_jwt_identity()
        data = request.get_json() or {}
        
        # Validate input
        is_valid, error_msg = _validate_case_data(data)
        if not is_valid:
            return error_response(error_msg, 400)
        
        # Create case
        case = Case(
            title=data["title"],
            description=data.get("description", ""),
            created_by=identity.get("id"),
            status="Pending"
        )
        
        if not safe_add(case, "case creation"):
            return error_response("Failed to create case", 500)
        
        # Log audit
        log_case_action(
            user_id=identity.get("id"),
            case_id=case.id,
            action="Created Case",
            details={"title": data["title"]}
        )
        
        if not safe_commit("case creation"):
            return error_response("Failed to save case", 500)
        
        return success_response(
            data={"case": case.to_dict()},
            message="Case created successfully",
            status_code=201
        )
        
    except Exception as e:
        return error_response("Internal server error", 500)


@case_bp.route("/list", methods=["GET"])
@jwt_required()
@roles_allowed("lawyer", "citizen", "admin", "judge")
def list_cases():
    """List cases with pagination and filtering."""
    try:
        identity = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        
        # Build query
        query = Case.query
        
        # Filter by user role
        if identity.get("role") != "admin":
            query = query.filter_by(created_by=identity.get("id"))
        
        # Filter by status if provided
        if status:
            query = query.filter_by(status=status)
        
        # Order by creation date (newest first)
        query = query.order_by(Case.created_at.desc())
        
        # Paginate
        paginated = paginate_query(query, page, per_page)
        if not paginated:
            return error_response("Failed to retrieve cases", 500)
        
        cases = [case.to_dict() for case in paginated.items]
        
        return success_response(
            data={
                "cases": cases,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": paginated.total,
                    "pages": paginated.pages,
                    "has_next": paginated.has_next,
                    "has_prev": paginated.has_prev
                }
            },
            message="Cases retrieved successfully"
        )
        
    except Exception as e:
        return error_response("Internal server error", 500)


@case_bp.route("/<int:case_id>", methods=["GET"])
@jwt_required()
@roles_allowed("lawyer", "citizen", "admin", "judge")
def get_case(case_id: int):
    """Get case details."""
    try:
        identity = get_jwt_identity()
        
        case = get_by_id(Case, case_id)
        if not case:
            return error_response("Case not found", 404)
        
        # Check access permissions
        if (identity.get("role") != "admin" and 
            case.created_by != identity.get("id") and
            case.assigned_judge_id != identity.get("id")):
            return error_response("Access denied", 403)
        
        return success_response(
            data={"case": case.to_dict()},
            message="Case retrieved successfully"
        )
        
    except Exception as e:
        return error_response("Internal server error", 500)


@case_bp.route("/<int:case_id>", methods=["PUT"])
@jwt_required()
@roles_allowed("lawyer", "citizen", "admin")
def update_case(case_id: int):
    """Update case details."""
    try:
        identity = get_jwt_identity()
        data = request.get_json() or {}
        
        case = get_by_id(Case, case_id)
        if not case:
            return error_response("Case not found", 404)
        
        # Check permissions
        if (identity.get("role") != "admin" and 
            case.created_by != identity.get("id")):
            return error_response("Access denied", 403)
        
        # Validate input
        if "title" in data:
            if not validate_string_length(data["title"], 1, 200):
                return error_response("Title must be between 1 and 200 characters", 400)
            case.title = data["title"]
        
        if "description" in data:
            if not validate_string_length(data["description"], 0, 2000):
                return error_response("Description must be less than 2000 characters", 400)
            case.description = data["description"]
        
        if "status" in data:
            allowed_statuses = ["Pending", "In Progress", "Completed", "Closed"]
            if data["status"] not in allowed_statuses:
                return error_response("Invalid status", 400)
            case.status = data["status"]
        
        case.updated_at = datetime.utcnow()
        
        # Log audit
        log_case_action(
            user_id=identity.get("id"),
            case_id=case.id,
            action="Updated Case",
            details={"updated_fields": list(data.keys())}
        )
        
        if not safe_commit("case update"):
            return error_response("Failed to update case", 500)
        
        return success_response(
            data={"case": case.to_dict()},
            message="Case updated successfully"
        )
        
    except Exception as e:
        return error_response("Internal server error", 500)


@case_bp.route("/<int:case_id>", methods=["DELETE"])
@jwt_required()
@roles_allowed("lawyer", "citizen", "admin")
def delete_case(case_id: int):
    """Delete a case."""
    try:
        identity = get_jwt_identity()
        
        case = get_by_id(Case, case_id)
        if not case:
            return error_response("Case not found", 404)
        
        # Check permissions
        if (identity.get("role") != "admin" and 
            case.created_by != identity.get("id")):
            return error_response("Access denied", 403)
        
        # Log audit before deletion
        log_case_action(
            user_id=identity.get("id"),
            case_id=case.id,
            action="Deleted Case",
            details={"title": case.title}
        )
        
        db.session.delete(case)
        
        if not safe_commit("case deletion"):
            return error_response("Failed to delete case", 500)
        
        return success_response(message="Case deleted successfully")
        
    except Exception as e:
        return error_response("Internal server error", 500)


@case_bp.route("/<int:case_id>/assign", methods=["POST"])
@jwt_required()
@roles_allowed("admin", "judge")
def assign_judge(case_id: int):
    """Assign a judge to a case."""
    try:
        identity = get_jwt_identity()
        data = request.get_json() or {}
        
        case = get_by_id(Case, case_id)
        if not case:
            return error_response("Case not found", 404)
        
        judge_id = data.get("judge_id")
        if not judge_id:
            return error_response("Judge ID is required", 400)
        
        # Validate judge exists and is a judge
        judge = get_by_id(User, judge_id)
        if not judge:
            return error_response("Judge not found", 404)
        
        # Check if user is a judge
        if judge.role_obj.name != "judge":
            return error_response("User is not a judge", 400)
        
        case.assigned_judge_id = judge_id
        case.updated_at = datetime.utcnow()
        
        # Log audit
        log_case_action(
            user_id=identity.get("id"),
            case_id=case.id,
            action="Assigned Judge",
            details={"judge_id": judge_id, "judge_name": judge.name}
        )
        
        if not safe_commit("judge assignment"):
            return error_response("Failed to assign judge", 500)
        
        return success_response(
            data={"case": case.to_dict()},
            message="Judge assigned successfully"
        )
        
    except Exception as e:
        return error_response("Internal server error", 500)
