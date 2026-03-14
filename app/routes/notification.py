from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.jwt_utils import get_jwt_identity

from app.extensions import db
from app.middleware.rbac import role_required, roles_allowed
from app.models.audit import AuditLog
from app.models.notification import Notification
from app.models.user import User
from app.utils.api_response import success_response, error_response
from app.utils.pagination import get_pagination_params, paginate_query, create_paginated_response

notification_bp = Blueprint("notification", __name__)


@notification_bp.route("/send", methods=["POST"])
@jwt_required()
@roles_allowed("admin", "judge", "lawyer")
def send():
    """Send a notification to a user"""
    try:
        identity = get_jwt_identity()
        data = request.json or {}
        
        user_id = data.get("user_id")
        message = data.get("message")
        
        if not all([user_id, message]):
            return jsonify({
                "message": "user_id and message are required",
                "success": False
            }), 400
        
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found", "success": False}), 404
        
        note = Notification(
            user_id=user_id,
            message=message,
            data=data.get("data"),
            read=False
        )
        db.session.add(note)
        db.session.flush()
        
        db.session.add(
            AuditLog(
                user_id=identity.get("id"),
                action="Sent Notification",
                details={"notification_id": note.id, "recipient_id": user_id}
            )
        )
        db.session.commit()
        
        return jsonify({
            "message": "Notification sent successfully",
            "success": True,
            "notification": {
                "id": note.id,
                "user_id": note.user_id,
                "message": note.message,
                "sent_at": note.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error sending notification: {str(e)}", "success": False}), 500


@notification_bp.route("/user/<int:user_id>", methods=["GET"])
@jwt_required()
def user_notes(user_id):
    """Get all notifications for a user with pagination"""
    try:
        identity = get_jwt_identity()
        
        # Users can only see their own notifications, admins can see any
        if identity.get("role") != "admin" and identity.get("id") != user_id:
            return error_response("Access denied", 403)
        
        User.query.get_or_404(user_id)
        
        # Get pagination parameters
        limit, offset = get_pagination_params()
        
        # Build query
        query = Notification.query.filter_by(user_id=user_id).order_by(
            Notification.created_at.desc()
        )
        
        # Apply pagination
        notifications, pagination_metadata = paginate_query(query, limit, offset)
        
        # Format response data
        notifications_data = [
            {
                "id": n.id,
                "message": n.message,
                "read": n.read,
                "created_at": n.created_at.isoformat()
            }
            for n in notifications
        ]
        
        paginated_data = create_paginated_response(notifications_data, pagination_metadata)
        
        return success_response(
            data={
                "user_id": user_id,
                **paginated_data
            },
            message=f"Retrieved {len(notifications)} notifications"
        )
    except Exception as e:
        return error_response(f"Error fetching notifications: {str(e)}", 500)


@notification_bp.route("/<int:notif_id>/read", methods=["PUT"])
@jwt_required()
def mark_as_read(notif_id):
    """Mark a notification as read"""
    try:
        identity = get_jwt_identity()
        note = Notification.query.get(notif_id)
        
        if not note:
            return jsonify({"message": "Notification not found", "success": False}), 404
        
        # Check authorization
        if identity.get("role") != "admin" and note.user_id != identity.get("id"):
            return jsonify({"message": "Access denied", "success": False}), 403
        
        note.read = True
        db.session.commit()
        
        return jsonify({
            "message": "Notification marked as read",
            "success": True,
            "notification_id": notif_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating notification: {str(e)}", "success": False}), 500


@notification_bp.route("/<int:notif_id>", methods=["DELETE"])
@jwt_required()
def delete_notification(notif_id):
    """Delete a notification"""
    try:
        identity = get_jwt_identity()
        note = Notification.query.get(notif_id)
        
        if not note:
            return jsonify({"message": "Notification not found", "success": False}), 404
        
        # Check authorization
        if identity.get("role") != "admin" and note.user_id != identity.get("id"):
            return jsonify({"message": "Access denied", "success": False}), 403
        
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({
            "message": "Notification deleted successfully",
            "success": True,
            "notification_id": notif_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting notification: {str(e)}", "success": False}), 500
