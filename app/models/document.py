from datetime import datetime

from app.extensions import db


class Document(db.Model):
    """Files attached to legal cases."""

    __tablename__ = "document"
    __table_args__ = (
        db.Index("idx_document_case", "case_id"),
        db.Index("idx_document_uploaded", "uploaded_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255))
    content_type = db.Column(db.String(120))
    size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
