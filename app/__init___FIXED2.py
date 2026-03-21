"""
Production-ready Flask application factory.
Clean, secure, and maintainable architecture.
"""

import os
import json
import uuid
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

# Load environment variables
load_dotenv()


def create_app(config_object=None):
    """Create and configure Flask application."""
    app = Flask(__name__, static_folder=None)
    
    # Configuration
    _configure_app(app, config_object)
    
    # Initialize extensions
    _init_extensions(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Register routes
    _register_routes(app)
    
    return app


def _configure_app(app, config_object):
    """Configure Flask application with validation."""
    if config_object:
        app.config.from_object(config_object)
    else:
        # Environment-based configuration
        from .config import DevelopmentConfig, ProductionConfig, TestingConfig
        
        env = os.getenv("FLASK_ENV", "development").lower()
        if env == "production":
            app.config.from_object(ProductionConfig)
        elif env == "testing":
            app.config.from_object(TestingConfig)
        else:
            app.config.from_object(DevelopmentConfig)
    
    # Override with environment-specific settings
    app.config["DEBUG"] = os.getenv("FLASK_ENV", "development").lower() == "development"
    
    # Validate production configuration
    if app.config.get("FLASK_ENV") == "production":
        _validate_production_config(app)


def _validate_production_config(app):
    """Validate critical production configuration."""
    errors = []
    
    jwt_key = app.config.get("JWT_SECRET_KEY")
    if not jwt_key or len(jwt_key) < 32:
        errors.append("JWT_SECRET_KEY is insecure or missing")
    
    secret = app.config.get("SECRET_KEY")
    if not secret or len(secret) < 32:
        errors.append("SECRET_KEY is insecure or missing")
    
    if errors:
        raise RuntimeError("Production configuration errors: " + "; ".join(errors))


def _init_extensions(app):
    """Initialize Flask extensions with proper error handling."""
    from .extensions import db, jwt, bcrypt, cors, socketio, migrate
    from .logging_config import setup_logging
    from .middleware.structured_logging import init_structured_logging
    
    # Setup logging
    setup_logging("judicial_supreme")
    init_structured_logging(app)
    
    # Initialize extensions
    cors.init_app(app)
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize rate limiter
    _init_rate_limiter(app)


def _init_rate_limiter(app):
    """Initialize rate limiter with Redis fallback."""
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    )
    
    if app.config.get('RATELIMIT_STORAGE_URI'):
        try:
            app.logger.info("Initializing Redis rate limiter...")
            limiter.init_app(app)
            app.logger.info("Redis rate limiter initialized")
        except Exception as e:
            app.logger.warning(f"Redis rate limiter failed: {e}")
            app.logger.info("Using memory rate limiter instead")
            limiter.storage_uri = "memory://"
            limiter.init_app(app)
    else:
        app.logger.info("Using memory rate limiter (Redis not configured)")
        limiter.init_app(app)
    
    # Store limiter in app context
    app.limiter = limiter


def _register_blueprints(app):
    """Register application blueprints."""
    # Import from routes package (using original files)
    from .routes import auth, case, case_activity, document, hearing, payment, audit, notification
    from .admin.routes import admin_bp
    from .ai.routes import ai_bp
    from .docs.swagger import docs_bp
    
    # Register blueprints with versioned URLs
    app.register_blueprint(auth.auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(case.case_bp, url_prefix="/api/v1/case")
    app.register_blueprint(case_activity.activity_bp, url_prefix="/api/v1/activity")
    app.register_blueprint(hearing.hearing_bp, url_prefix="/api/v1/hearing")
    app.register_blueprint(payment.payment_bp, url_prefix="/api/v1/payment")
    app.register_blueprint(audit.audit_bp, url_prefix="/api/v1/audit")
    app.register_blueprint(notification.notification_bp, url_prefix="/api/v1/notification")
    app.register_blueprint(document.document_bp, url_prefix="/api/v1/document")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(ai_bp, url_prefix="/api/v1/ai")
    app.register_blueprint(docs_bp, url_prefix="/api/v1/docs")


def _register_error_handlers(app):
    """Register standardized error handlers."""
    from .utils.api_response import api_response
    
    def _make_error_payload(err):
        """Create standardized error payload."""
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        code = err.code if isinstance(err, HTTPException) else 500
        err_type = type(err).__name__ if not isinstance(err, HTTPException) else err.name
        msg = err.description if isinstance(err, HTTPException) else str(err)
        
        data = {"error": err_type, "request_id": req_id}
        return api_response(False, data=data, message=msg, status_code=code)
    
    # Register error handlers for common HTTP errors
    for code in [400, 401, 403, 404, 429, 500, 422]:
        def _handler(err, code=code):
            payload, status_code = _make_error_payload(err)
            return payload, (400 if code == 422 else status_code)
        
        app.register_error_handler(code, _handler)


def _register_routes(app):
    """Register application routes."""
    from .socket.chat import register_socket
    
    # Register Socket.IO handlers
    register_socket(app.socketio)
    
    @app.route("/")
    def home():
        """Home route - health check."""
        return {"message": "Backend is running 🚀"}
    
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        from .extensions import db
        from sqlalchemy import text
        
        status = {"db": False}
        try:
            # Lightweight database check
            db.session.execute(text("SELECT 1"))
            status["db"] = True
        except Exception:
            status["db"] = False
        
        overall = "ok" if status["db"] else "degraded"
        
        return jsonify({
            "status": overall,
            "service": "judicial-backend",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": status
        }), 200 if overall == "ok" else 503
