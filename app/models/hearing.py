from datetime import datetime

from app.extensions import db


class Hearing(db.Model):
    """Court hearings scheduled for cases."""

    __tablename__ = "hearing"
    __table_args__ = (
        db.Index("idx_hearing_date", "hearing_date"),
        db.Index("idx_hearing_case_id", "case_id"),
        db.Index("idx_hearing_judge_id", "judge_id"),
        db.Index("idx_hearing_status", "status"),
        db.Index("idx_hearing_created_at", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    hearing_date = db.Column(db.DateTime, nullable=False)
    judge_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    status = db.Column(db.String(50), default="Scheduled")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
