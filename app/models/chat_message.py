from datetime import datetime

from app.extensions import db


class ChatMessage(db.Model):
    """Messages exchanged between users about a case."""

    __tablename__ = "chat_message"
    __table_args__ = (
        db.Index("idx_chat_case", "case_id"),
        db.Index("idx_chat_sender", "sender_id"),
        db.Index("idx_chat_receiver", "receiver_id"),
        db.Index("idx_chat_created", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    message = db.Column(db.Text, nullable=False)
    attachments = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
