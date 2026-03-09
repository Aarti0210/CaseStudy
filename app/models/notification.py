from datetime import datetime

from app.extensions import db


class Notification(db.Model):
    """Simple notification messages for users."""

    __tablename__ = "notification"
    __table_args__ = (
        db.Index("idx_notification_user", "user_id"),
        db.Index("idx_notification_created", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    data = db.Column(db.JSON)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
