from datetime import datetime

from app.extensions import db


class Billing(db.Model):
    """Billing entries tied to cases."""

    __tablename__ = "billing"
    __table_args__ = (
        db.Index("idx_billing_case", "case_id"),
        db.Index("idx_billing_created_by", "created_by"),
    )

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    status = db.Column(db.String(50), default="open")
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
