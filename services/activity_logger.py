from flask import request

from app.extensions import db
from app.models.case_activity import CaseActivity


def log_activity(case_id, user_id, action, metadata=None, system=False):

    activity = CaseActivity(
        case_id=case_id,
        user_id=user_id,
        action=action,
        details=metadata,
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        is_system_generated=system,
    )

    db.session.add(activity)
    db.session.commit()
