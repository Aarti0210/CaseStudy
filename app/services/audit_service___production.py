"""
Production-ready audit service for centralized logging.
Secure, structured, and comprehensive activity tracking.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from flask import current_app, request
from app.extensions import db
from app.models.audit import AuditLog


class AuditServiceError(Exception):
    """Custom audit service error."""
    pass


def log_audit_event(
    user_id: Optional[int],
    action: str,
    details: Optional[Dict[str, Any]] = None,
    case_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> bool:
    """
    Log an audit event to the database.
    
    Args:
        user_id: ID of user performing the action
        action: Description of the action performed
        details: Additional details about the action
        case_id: ID of the related case (if applicable)
        ip_address: IP address of the request
        user_agent: User agent string
    
    Returns:
        bool: True if logging was successful, False otherwise
    """
    try:
        # Get request context information if not provided
        if ip_address is None:
            ip_address = request.remote_addr if request else None
        if user_agent is None:
            user_agent = request.headers.get("User-Agent") if request else None
        
        # Sanitize details for security
        sanitized_details = _sanitize_audit_details(details) if details else {}
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            details=sanitized_details,
            case_id=case_id,
            ip_address=_truncate_string(ip_address, 64) if ip_address else None,
            user_agent=_truncate_string(user_agent, 500) if user_agent else None,
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


def log_user_action(user_id: int, action: str, details: Dict[str, Any] = None) -> bool:
    """Convenience function for logging user actions."""
    return log_audit_event(user_id, action, details)


def log_case_action(user_id: int, case_id: int, action: str, details: Dict[str, Any] = None) -> bool:
    """Convenience function for logging case-related actions."""
    return log_audit_event(user_id, action, details, case_id)


def log_system_event(action: str, details: Dict[str, Any] = None) -> bool:
    """Convenience function for logging system events."""
    return log_audit_event(None, action, details)


def log_security_event(
    user_id: Optional[int],
    action: str,
    details: Dict[str, Any] = None,
    severity: str = "medium"
) -> bool:
    """Log security-related events with enhanced tracking."""
    security_details = {
        "severity": severity,
        "category": "security",
        **(details or {})
    }
    
    return log_audit_event(user_id, action, security_details)


def log_api_access(
    endpoint: str,
    method: str,
    user_id: Optional[int] = None,
    response_status: int = 200,
    duration_ms: Optional[int] = None
) -> bool:
    """Log API access for monitoring and analytics."""
    details = {
        "endpoint": endpoint,
        "method": method,
        "response_status": response_status,
        "duration_ms": duration_ms
    }
    
    return log_audit_event(user_id, f"API Access: {method} {endpoint}", details)


def _sanitize_audit_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize audit details to prevent sensitive data leakage."""
    if not isinstance(details, dict):
        return {}
    
    sanitized = {}
    for key, value in details.items():
        # Remove potentially sensitive fields
        if key.lower() in ['password', 'token', 'secret', 'key']:
            sanitized[key] = '[REDACTED]'
        else:
            # Truncate long strings
            if isinstance(value, str) and len(value) > 1000:
                sanitized[key] = value[:1000] + '...'
            else:
                sanitized[key] = value
    
    return sanitized


def _truncate_string(value: Optional[str], max_length: int) -> Optional[str]:
    """Truncate string to maximum length."""
    if not value or not isinstance(value, str):
        return value
    
    return value[:max_length] if len(value) > max_length else value


def get_user_activity_summary(user_id: int, days: int = 30) -> Dict[str, Any]:
    """Get summary of user activities for specified period."""
    try:
        from datetime import timedelta
        from sqlalchemy import text
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = text("""
            SELECT 
                action,
                COUNT(*) as count,
                MAX(created_at) as last_activity
            FROM audit_log 
            WHERE user_id = :user_id 
                AND created_at >= :cutoff_date
            GROUP BY action
            ORDER BY last_activity DESC
        """)
        
        result = db.session.execute(query, {
            'user_id': user_id,
            'cutoff_date': cutoff_date
        }).fetchall()
        
        return {
            "period_days": days,
            "activities": [dict(row) for row in result],
            "summary": {
                "total_activities": len(result),
                "last_activity": result[0]['last_activity'] if result else None
            }
        }
        
    except Exception as e:
        current_app.logger.error(f"Failed to get user activity summary: {str(e)}")
        return {"period_days": days, "activities": [], "summary": {}}
