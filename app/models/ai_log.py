from datetime import datetime

from app.extensions import db


class AILog(db.Model):
    """Records interactions with AI services for auditing and metrics."""

    __tablename__ = "ai_log"
    __table_args__ = (
        db.Index("idx_ai_log_user", "user_id"),
        db.Index("idx_ai_log_case", "case_id"),
        db.Index("idx_ai_log_created", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    role = db.Column(db.String(50))
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=True)
    prompt = db.Column(db.Text)
    response = db.Column(db.Text)
    model = db.Column(db.String(100))
    language = db.Column(db.String(20), default="en")
    prompt_tokens = db.Column(db.Integer)
    completion_tokens = db.Column(db.Integer)
    total_tokens = db.Column(db.Integer)
    usage = db.Column(db.JSON)
    feature_used = db.Column(db.String(100))
    ip_address = db.Column(db.String(100))
    token_usage = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
