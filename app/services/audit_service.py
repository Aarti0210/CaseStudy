"""
Audit service for centralized logging of user activities.
Provides consistent audit logging across the application.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from flask import current_app, request
from app.extensions import db
from app.models.audit import AuditLog


def log_audit_event(
    user_id: Optional[int],
    action: str,
    details: Optional[Dict[str, Any]] = None,
    case_id: Optional[int] = None
) -> bool:
    """
    Log an audit event to the database.
    
    Args:
        user_id: ID of the user performing the action
        action: Description of the action performed
        details: Additional details about the action
        case_id: ID of the related case (if applicable)
    
    Returns:
        bool: True if logging was successful, False otherwise
    """
    try:
        # Get request context information
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get("User-Agent") if request else None
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            details=details or {},
            case_id=case_id,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        # Log to application logger for debugging
        current_app.logger.info(
            f"Audit: {action} by user {user_id} from {ip_address}"
        )
        
        return True
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to log audit event: {str(e)}")
        return False


def log_user_action(user_id: int, action: str, details: Dict[str, Any] = None):
    """Convenience function for logging user actions."""
    return log_audit_event(user_id, action, details)


def log_case_action(user_id: int, case_id: int, action: str, details: Dict[str, Any] = None):
    """Convenience function for logging case-related actions."""
    return log_audit_event(user_id, action, details, case_id)


def log_system_event(action: str, details: Dict[str, Any] = None):
    """Convenience function for logging system events."""
    return log_audit_event(None, action, details)
