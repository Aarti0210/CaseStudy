"""
Case model for Judicial Case Management System.

Represents legal cases being managed in system.
Fixed table name to avoid SQL keyword conflicts.
"""

from datetime import datetime
from app.extensions import db


class Case(db.Model):
    """Case model representing a legal case."""

    __tablename__ = "legal_case"  # Fixed: 'case' is reserved keyword
    __table_args__ = (
        db.Index("idx_case_status", "status"),
        db.Index("idx_case_created_at", "created_at"),
        db.Index("idx_case_created_by", "created_by"),
        db.Index("idx_case_assigned_judge_id", "assigned_judge_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.String(50), default="Pending", nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )
    assigned_judge_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    # Relationships
    documents = db.relationship("Document", backref="legal_case", lazy="dynamic")
    hearings = db.relationship("Hearing", backref="legal_case", lazy="dynamic")
    payments = db.relationship("Payment", backref="legal_case", lazy="dynamic")
    activities = db.relationship("CaseActivity", backref="legal_case", lazy="dynamic")
    audit_logs = db.relationship("AuditLog", backref="legal_case", lazy="dynamic")

    def __repr__(self):
        return f"<Case {self.title}>"

    def to_dict(self):
        """Convert case to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "assigned_judge_id": self.assigned_judge_id,
        }
