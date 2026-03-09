"""
AuditLog model for the Judicial Case Management System.

Tracks all user actions and system events for security and compliance.
"""

from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    """AuditLog model for tracking user actions and system events."""

    __tablename__ = "audit_log"
    __table_args__ = (db.Index("idx_audit_user", "user_id"),
                      db.Index("idx_audit_case", "case_id"),
                      db.Index("idx_audit_timestamp", "timestamp"))

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=True, index=True
    )
    action = db.Column(db.String(255), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=True, index=True)
    details = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.action} at {self.timestamp}>"

    def to_dict(self):
        """Convert audit log to dictionary for serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "case_id": self.case_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
