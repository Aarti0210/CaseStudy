from datetime import datetime, timedelta

from app.extensions import db


class OTP(db.Model):
    """One-time passwords issued to users."""

    __tablename__ = "otp"
    __table_args__ = (
        db.Index("idx_otp_user", "user_id"),
        db.Index("idx_otp_expires", "expires_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create_for_user(cls, user_id, code, ttl_seconds=300):
        return cls(
            user_id=user_id,
            code=code,
            expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds),
        )
