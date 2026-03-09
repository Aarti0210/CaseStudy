from datetime import datetime

from app.extensions import db
from app.models.audit import AuditLog


def log_audit(user_id, action, case_id=None, metadata=None):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        case_id=case_id,
        metadata=metadata,
        timestamp=datetime.utcnow(),
    )
    try:
        db.session.add(audit)
        db.session.commit()
    except Exception:
        db.session.rollback()
