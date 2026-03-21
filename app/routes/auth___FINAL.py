"""
Production-ready authentication routes.
Secure, validated, and standardized.
"""

import json
import secrets
from datetime import datetime, timedelta

from flask import Blueprint, current_app, request
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required
)

from app.extensions import bcrypt, db
from app.jwt_utils import get_jwt_identity
from app.models.audit import AuditLog
from app.models.otp import OTP
from app.models.user import User
from app.models.role import Role
from app.services.otp_email import send_otp_email
from app.utils.api_response import success_response, error_response
from app.utils.validators import validate_email, validate_password, validate_role
from app.utils.database import safe_commit, safe_add
from app.services.audit_service import log_user_action

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
        
        if not validate_role(data["role"]):
            return error_response("Invalid role", 400)
        
        # Check for existing user
        if User.query.filter_by(email=data["email"]).first():
            return error_response("Email already registered", 409)
        
        # Get or create role
        role_obj = Role.query.filter_by(name=data["role"]).first()
        if not role_obj:
            role_obj = Role(name=data["role"])
            if not safe_add(role_obj, "role creation"):
                return _handle_database_error(Exception("Failed to create role"))
        
        # Create user
        user = User(
            name=data["name"],
            email=data["email"],
            role_id=role_obj.id
        )
        user.set_password(data["password"])
        
        if not safe_add(user, "user creation"):
            return _handle_database_error(Exception("Failed to create user"))
        
        # Log audit
        log_user_action(user.id, "User Registration", {"email": data["email"], "role": data["role"]})
        
        if not safe_commit("user registration"):
            return _handle_database_error(Exception("Failed to commit user"))
        
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
        log_user_action(user.id, "User Login", {"email": data["email"]})
        
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
def logout():
    """User logout endpoint."""
    try:
        identity = get_jwt_identity()
        if identity:
            log_user_action(identity.get("id"), "User Logout", {})
        
        return success_response(message="Logout successful")
        
    except Exception as e:
        return _handle_database_error(e, "user logout")


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
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
            user.name = data["name"][:100]  # Limit length
        if "phone" in data:
            user.phone = data["phone"][:30] if data["phone"] else None
        
        user.updated_at = datetime.utcnow()
        
        log_user_action(user.id, "Profile Update", {"updated_fields": list(data.keys())})
        
        if not safe_commit("profile update"):
            return _handle_database_error(Exception("Failed to update profile"))
        
        return success_response(
            data={"user": user.to_dict()},
            message="Profile updated successfully"
        )
        
    except Exception as e:
        return _handle_database_error(e, "profile update")
