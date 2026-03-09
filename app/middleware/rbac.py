from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request
from app.jwt_utils import get_jwt_identity


def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_jwt_identity()

            if not user or user.get("role") != required_role:
                return jsonify({"message": "Access denied"}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def roles_allowed(*allowed_roles):
    """Decorator to allow multiple roles."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_jwt_identity()
            if not user or user.get("role") not in allowed_roles:
                return jsonify({"message": "Access denied"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
