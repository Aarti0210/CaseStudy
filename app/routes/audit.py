from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.middleware.rbac import role_required
from app.models.audit import AuditLog
from app.utils.api_response import success_response, error_response
from app.utils.pagination import get_pagination_params, paginate_query, create_paginated_response

audit_bp = Blueprint("audit", __name__)


@audit_bp.route("/logs", methods=["GET"])
@jwt_required()
@role_required("admin")
def logs():
    """Get all audit logs with pagination"""
    try:
        # Get pagination parameters
        limit, offset = get_pagination_params()
        
        # Build query
        query = AuditLog.query.order_by(AuditLog.timestamp.desc())
        
        # Apply pagination
        logs, pagination_metadata = paginate_query(query, limit, offset)
        
        # Format response data
        logs_data = [
            {
                "id": l.id,
                "user_id": l.user_id,
                "action": l.action,
                "case_id": l.case_id,
                "details": l.details,
                "timestamp": l.timestamp.isoformat() if l.timestamp else None
            }
            for l in logs
        ]
        
        paginated_data = create_paginated_response(logs_data, pagination_metadata)
        
        return success_response(
            data=paginated_data,
            message=f"Retrieved {len(logs)} audit logs"
        )
    except Exception as e:
        return error_response(f"Error fetching logs: {str(e)}", 500)


@audit_bp.route("/user/<int:user_id>", methods=["GET"])
@jwt_required()
@role_required("admin")
def user_logs(user_id):
    """Get audit logs for a specific user"""
    try:
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        logs_query = AuditLog.query.filter_by(user_id=user_id).order_by(AuditLog.timestamp.desc())
        total_count = logs_query.count()
        
        logs_data = logs_query.limit(limit).offset(offset).all()
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "total": total_count,
            "returned": len(logs_data),
            "logs": [
                {
                    "id": l.id,
                    "action": l.action,
                    "case_id": l.case_id,
                    "timestamp": l.timestamp.isoformat() if l.timestamp else None
                }
                for l in logs_data
            ]
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching user logs: {str(e)}", "success": False}), 500


@audit_bp.route("/case/<int:case_id>", methods=["GET"])
@jwt_required()
@role_required("admin")
def case_logs(case_id):
    """Get audit logs for a specific case"""
    try:
        logs_data = AuditLog.query.filter_by(case_id=case_id).order_by(AuditLog.timestamp.desc()).all()
        
        return jsonify({
            "success": True,
            "case_id": case_id,
            "count": len(logs_data),
            "logs": [
                {
                    "id": l.id,
                    "user_id": l.user_id,
                    "action": l.action,
                    "timestamp": l.timestamp.isoformat() if l.timestamp else None
                }
                for l in logs_data
            ]
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching case logs: {str(e)}", "success": False}), 500
