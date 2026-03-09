import secrets
from datetime import datetime, timedelta

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required)
from app.jwt_utils import get_jwt_identity

from app.extensions import bcrypt, db, limiter
from app.models.audit import AuditLog
from app.models.otp import OTP
from app.models.user import User
from app.models.role import Role
from services.otp_email import send_otp_email

auth_bp = Blueprint("auth", __name__)


def _validate_email(email):
    return isinstance(email, str) and "@" in email


@auth_bp.route("/signup", methods=["POST"])
@limiter.limit("10 per hour")
def signup():
    data = request.get_json() or {}
    required_fields = ["name", "email", "password", "role"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    allowed_roles = ["admin", "lawyer", "judge", "citizen"]
    if data["role"] not in allowed_roles:
        return jsonify({"message": "Invalid role"}), 400

    if not _validate_email(data["email"]):
        return jsonify({"message": "Invalid email"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 409

    # look up role record and set foreign key
    role_obj = Role.query.filter_by(name=data["role"]).first()
    if not role_obj:
        # create role automatically if missing to reduce configuration errors
        role_obj = Role(name=data["role"])
        try:
            db.session.add(role_obj)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify({"message": "Invalid role"}), 400

    user = User(name=data["name"], email=data["email"], role_id=role_obj.id)
    # store password using model helper to keep hashing consistent
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("20 per hour")
def login():
    data = request.get_json() or {}
    if not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password required"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    user_role = user.role_obj.name if user.role_obj else None
    # identity must be serialized to a string because PyJWT requires the
    # "sub" claim to be a string.  We preserve the structure by
    # dumping to JSON and parsing it later in our helper.
    import json
    identity = json.dumps({"id": user.id, "role": user_role})
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return (
        jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user_role,
                },
            }
        ),
        200,
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token}), 200


@auth_bp.route("/otp/request", methods=["POST"])
@limiter.limit("5 per hour")
def request_otp():
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"message": "Email required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # enforce resend cooldown
    cooldown = int(current_app.config.get("OTP_RESEND_COOLDOWN", 60))
    last = OTP.query.filter_by(user_id=user.id).order_by(OTP.created_at.desc()).first()
    if last:
        elapsed = (datetime.utcnow() - last.created_at).total_seconds()
        if elapsed < cooldown:
            retry_after = int(cooldown - elapsed)
            # log cooldown attempt
            try:
                db.session.add(
                    AuditLog(
                        user_id=user.id,
                        action="otp_send_cooldown",
                        details={"email": email, "retry_after": retry_after},
                    )
                )
                db.session.commit()
            except Exception:
                db.session.rollback()
            return (
                jsonify(
                    {
                        "message": "Please wait before requesting another OTP",
                        "retry_after": retry_after,
                    }
                ),
                429,
            )

    # generate 6-digit numeric code
    code = f"{secrets.randbelow(1000000):06d}"
    otp = OTP.create_for_user(
        user.id, code, ttl_seconds=int(current_app.config.get("OTP_TTL", 300))
    )
    db.session.add(otp)
    db.session.commit()

    # send email with retries
    sent = send_otp_email(user.email, code, int(current_app.config.get("OTP_TTL", 300)))

    # log send attempt to audit
    try:
        db.session.add(
            AuditLog(
                user_id=user.id,
                action="otp_send",
                details={"email": email, "sent": bool(sent)},
            )
        )
        db.session.commit()
    except Exception:
        db.session.rollback()

    if not sent:
        return jsonify({"message": "Failed to send OTP, try again later"}), 500

    return (
        jsonify({"message": "OTP sent", "ttl": current_app.config.get("OTP_TTL", 300)}),
        200,
    )


@auth_bp.route("/otp/verify", methods=["POST"])
def verify_otp():
    data = request.get_json() or {}
    email = data.get("email")
    code = data.get("code")
    if not email or not code:
        return jsonify({"message": "Email and code required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    otp = (
        OTP.query.filter_by(user_id=user.id, code=code, used=False)
        .order_by(OTP.created_at.desc())
        .first()
    )
    if not otp or otp.expires_at < datetime.utcnow():
        try:
            db.session.add(
                AuditLog(
                    user_id=user.id,
                    action="otp_verify_failed",
                    details={"email": email},
                )
            )
            db.session.commit()
        except Exception:
            db.session.rollback()
        return jsonify({"message": "Invalid or expired OTP"}), 400

    otp.used = True
    db.session.commit()
    try:
        db.session.add(
            AuditLog(
                user_id=user.id, action="otp_verify_success", details={"email": email}
            )
        )
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({"message": "OTP verified"}), 200
