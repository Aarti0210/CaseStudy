"""
Production-ready services package initialization.
Centralized business logic with proper error handling.
"""

from . import smart_scheduler
from .otp_email import send_otp_email
from .audit_service import log_audit_event, log_user_action, log_case_action
from .email_service import send_email

__all__ = [
    "smart_scheduler",
    "send_otp_email", 
    "log_audit_event",
    "log_user_action",
    "log_case_action",
    "send_email"
]
