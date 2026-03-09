from datetime import datetime

from app.extensions import db


class CaseActivity(db.Model):
    """Activity log entries for actions taken on cases."""

    __tablename__ = "case_activity"
    __table_args__ = (
        db.Index("idx_activity_case", "case_id"),
        db.Index("idx_activity_user", "user_id"),
        db.Index("idx_activity_created", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.JSON)

    ip_address = db.Column(db.String(100))
    user_agent = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_system_generated = db.Column(db.Boolean, default=False)
