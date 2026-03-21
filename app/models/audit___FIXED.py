"""
AuditLog model for Judicial Case Management System.

Tracks all user actions and system events for security and compliance.
Fixed table name and improved schema.
"""

from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    """AuditLog model for tracking user actions and system events."""

    __tablename__ = "audit_log"
    __table_args__ = (
        db.Index("idx_audit_user_id", "user_id"),
        db.Index("idx_audit_case_id", "case_id"),
        db.Index("idx_audit_timestamp", "timestamp"),
        db.Index("idx_audit_action", "action"),
        db.Index("idx_audit_composite", "timestamp", "user_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=True, index=True
    )
    action = db.Column(db.String(255), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey("legal_case.id"), nullable=True, index=True)  # Fixed: was "case.id"
    details = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(64), nullable=True)  # Fixed: increased from 45 to 64
    user_agent = db.Column(db.String(500), nullable=True)  # Added: user agent tracking

    # Relationships
    user = db.relationship("User", backref="user_audit_logs", foreign_keys=[user_id])
    case = db.relationship("Case", backref="case_audit_logs", foreign_keys=[case_id])

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
            "user_agent": self.user_agent,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
