"""
Authentication routes module.
Handles user registration, login, token management, and OTP verification.
"""

import json
import secrets
from datetime import datetime, timedelta

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required
)

from app.extensions import bcrypt, db, limiter
from app.jwt_utils import get_jwt_identity
from app.models.audit import AuditLog
from app.models.otp import OTP
from app.models.user import User
from app.models.role import Role
from app.services.otp_email import send_otp_email
from app.utils.api_response import success_response, error_response
from app.utils.validators import validate_email, validate_password

auth_bp = Blueprint("auth", __name__)


def _create_user_tokens(user):
    """Create JWT tokens for user."""
    user_role = user.role_obj.name if user.role_obj else None
    # JWT requires string identity, so we encode as JSON
    identity = json.dumps({"id": user.id, "role": user_role})
    
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 3600)
    }


def _handle_database_error(error, operation="operation"):
    """Standardized database error handling."""
    db.session.rollback()
    current_app.logger.error(f"Database error during {operation}: {str(error)}")
    return error_response("Database operation failed", 500)


@auth_bp.route("/signup", methods=["POST"])
@limiter.limit("100 per hour")
def signup():
    """User registration endpoint."""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        required_fields = ["name", "email", "password", "role"]
        for field in required_fields:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        
        # Validate input data
        if not validate_email(data["email"]):
            return error_response("Invalid email format", 400)
        
        if not validate_password(data["password"]):
            return error_response("Password must be at least 8 characters", 400)
        
        # Validate role
        allowed_roles = ["admin", "lawyer", "judge", "citizen"]
        if data["role"] not in allowed_roles:
            return error_response("Invalid role", 400)
        
        # Check for existing user
        if User.query.filter_by(email=data["email"]).first():
            return error_response("Email already registered", 409)
        
        # Get or create role
        role_obj = Role.query.filter_by(name=data["role"]).first()
        if not role_obj:
            role_obj = Role(name=data["role"])
            db.session.add(role_obj)
            db.session.flush()
        
        # Create user
        user = User(
            name=data["name"],
            email=data["email"],
            role_id=role_obj.id
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()
        
        # Log audit
        db.session.add(
            AuditLog(
                user_id=user.id,
                action="User Registration",
                details={"email": data["email"], "role": data["role"]}
            )
        )
        db.session.commit()
        
        # Create tokens for immediate login
        tokens = _create_user_tokens(user)
        
        return success_response(
            data={
                "user": user.to_dict(),
                **tokens
            },
            message="User created successfully",
            status_code=201
        )
        
    except Exception as e:
        return _handle_database_error(e, "user registration")


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("200 per hour")
def login():
    """User login endpoint."""
    try:
        data = request.get_json() or {}
        
        if not data.get("email") or not data.get("password"):
            return error_response("Email and password required", 400)
        
        # Find user
        user = User.query.filter_by(email=data["email"]).first()
        if not user or not user.check_password(data["password"]):
            return error_response("Invalid credentials", 401)
        
        if not user.is_active:
            return error_response("Account is deactivated", 401)
        
        # Create tokens
        tokens = _create_user_tokens(user)
        
        # Log audit
        db.session.add(
            AuditLog(
                user_id=user.id,
                action="User Login",
                details={"email": data["email"]}
            )
        )
        db.session.commit()
        
        return success_response(
            data={
                "user": user.to_dict(),
                **tokens
            },
            message="Login successful"
        )
        
    except Exception as e:
        return _handle_database_error(e, "user login")


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required()
@limiter.limit("100 per hour")
def refresh():
    """Refresh access token."""
    try:
        identity = get_jwt_identity()
        if not identity:
            return error_response("Invalid token", 401)
        
        # Create new tokens
        access_token = create_access_token(identity=json.dumps(identity))
        refresh_token = create_refresh_token(identity=json.dumps(identity))
        
        return success_response(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 3600)
            },
            message="Token refreshed successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return error_response("Token refresh failed", 500)


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
@limiter.limit("100 per hour")
def logout():
    """User logout endpoint."""
    try:
        identity = get_jwt_identity()
        if identity:
            # Log audit
            db.session.add(
                AuditLog(
                    user_id=identity.get("id"),
                    action="User Logout",
                    details={}
                )
            )
            db.session.commit()
        
        return success_response(message="Logout successful")
        
    except Exception as e:
        return _handle_database_error(e, "user logout")


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
@limiter.limit("100 per hour")
def get_profile():
    """Get current user profile."""
    try:
        identity = get_jwt_identity()
        if not identity:
            return error_response("Invalid token", 401)
        
        user = User.query.get(identity.get("id"))
        if not user:
            return error_response("User not found", 404)
        
        return success_response(
            data={"user": user.to_dict()},
            message="Profile retrieved successfully"
        )
        
    except Exception as e:
        return _handle_database_error(e, "profile retrieval")


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
@limiter.limit("50 per hour")
def update_profile():
    """Update user profile."""
    try:
        identity = get_jwt_identity()
        if not identity:
            return error_response("Invalid token", 401)
        
        user = User.query.get(identity.get("id"))
        if not user:
            return error_response("User not found", 404)
        
        data = request.get_json() or {}
        
        # Update allowed fields
        if "name" in data:
            user.name = data["name"]
        if "phone" in data:
            user.phone = data["phone"]
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log audit
        db.session.add(
            AuditLog(
                user_id=user.id,
                action="Profile Update",
                details={"updated_fields": list(data.keys())}
            )
        )
        db.session.commit()
        
        return success_response(
            data={"user": user.to_dict()},
            message="Profile updated successfully"
        )
        
    except Exception as e:
        return _handle_database_error(e, "profile update")
