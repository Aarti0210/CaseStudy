"""
SQLAlchemy models for the Judicial Case Management System.

This module imports all model classes to make them easily accessible
and ensure they are registered with SQLAlchemy.
"""

from app.models.audit import AuditLog
from app.models.case import Case
from app.models.case_activity import CaseActivity
from app.models.chat_message import ChatMessage
from app.models.document import Document
from app.models.hearing import Hearing
from app.models.notification import Notification
from app.models.otp import OTP
from app.models.payment import Payment
from app.models.user import User
from app.models.role import Role
from app.models.ai_log import AILog
from app.models.billing import Billing

__all__ = [
    "AuditLog",
    "Case",
    "CaseActivity",
    "ChatMessage",
    "Document",
    "Hearing",
    "Notification",
    "OTP",
    "Payment",
    "User",
    "Role",
    "AILog",
    "Billing",
]
