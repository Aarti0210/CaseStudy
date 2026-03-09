"""
Role model for the Judicial Case Management System.

Defines user roles and their associated permissions.
"""

from datetime import datetime
from app.extensions import db


class Role(db.Model):
    """Role model for user authorization."""

    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    users = db.relationship("User", backref="role_obj", lazy="dynamic")

    def __repr__(self):
        return f"<Role {self.name}>"

    def to_dict(self):
        """Convert role to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
