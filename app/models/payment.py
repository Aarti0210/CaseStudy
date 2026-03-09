from datetime import datetime

from app.extensions import db


class Payment(db.Model):
    """Payments recorded against cases."""

    __tablename__ = "payment"
    __table_args__ = (
        db.Index("idx_payment_case", "case_id"),
        db.Index("idx_payment_status", "status"),
        db.Index("idx_payment_created", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="USD")
    status = db.Column(db.String(50), default="pending")
    provider = db.Column(db.String(50))
    provider_ref = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
