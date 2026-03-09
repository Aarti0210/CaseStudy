import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def create_app(config_object=None):
    app = Flask(__name__, static_folder=None)

    # configure from class or environment
    if config_object:
        app.config.from_object(config_object)
    else:
        # pick config based on FLASK_ENV or use BaseConfig defaults
        from .config import DevelopmentConfig, ProductionConfig, TestingConfig

        env = os.getenv("FLASK_ENV", "development").lower()
        if env == "production":
            app.config.from_object(ProductionConfig)
        elif env == "testing":
            app.config.from_object(TestingConfig)
        else:
            app.config.from_object(DevelopmentConfig)

    # initialize extensions and blueprints

    # ensure DEBUG only enabled when FLASK_ENV == 'development'
    env = os.getenv("FLASK_ENV", "development").lower()
    app.config["DEBUG"] = True if env == "development" else False

    # validate critical configuration in production only: fail fast if secrets are missing or weak
    if env == "production":
        jwt_key = app.config.get("JWT_SECRET_KEY")
        if not jwt_key or len(jwt_key) < 32:
            raise RuntimeError("JWT_SECRET_KEY is insecure or missing")
        secret = app.config.get("SECRET_KEY")
        if not secret or len(secret) < 32:
            raise RuntimeError("SECRET_KEY is insecure or missing")

    # register global error handlers with structured JSON responses
    from flask import jsonify, request
    from werkzeug.exceptions import HTTPException
    import uuid

    def _make_error_payload(err):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        code = err.code if isinstance(err, HTTPException) else 500
        err_type = type(err).__name__ if not isinstance(err, HTTPException) else err.name
        msg = err.description if isinstance(err, HTTPException) else str(err)
        return jsonify({"error": err_type, "message": msg, "request_id": req_id}), code

    for code in [400, 401, 403, 404, 429, 500, 422]:
        # map 422 (Unprocessable Entity) to 400 for client validation failures
        def _handler(err, code=code):
            payload, status_code = _make_error_payload(err)
            return payload, (400 if code == 422 else status_code)

        app.register_error_handler(code, _handler)

    # register extensions and blueprints
    from .extensions import bcrypt, cors, db, jwt, limiter, socketio
    from .logging_config import setup_logging

    setup_logging("judicial_supreme")
    cors.init_app(app)
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    jwt.init_app(app)
    bcrypt.init_app(app)
    # Configure rate limiter
    limiter.init_app(app)
    from .extensions import migrate

    migrate.init_app(app, db)

    from .admin.routes import admin_bp
    from .ai.routes import ai_bp
    from .routes import (audit, auth, case, case_activity, document, hearing, notification,
                         payment)
    from .socket.chat import register_socket

    app.register_blueprint(auth.auth_bp, url_prefix="/auth")
    app.register_blueprint(case.case_bp, url_prefix="/case")
    app.register_blueprint(case_activity.activity_bp, url_prefix="/activity")
    app.register_blueprint(hearing.hearing_bp, url_prefix="/hearing")
    app.register_blueprint(payment.payment_bp, url_prefix="/payment")
    app.register_blueprint(audit.audit_bp, url_prefix="/audit")
    app.register_blueprint(notification.notification_bp, url_prefix="/notification")
    app.register_blueprint(document.document_bp, url_prefix="/document")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(ai_bp, url_prefix="/ai")

    register_socket(socketio)

    @app.route("/health", methods=["GET"]) 
    def _health():
        from flask import jsonify
        from .extensions import db
        status = {"db": False}
        try:
            # lightweight DB check
            db.session.execute("SELECT 1")
            status["db"] = True
        except Exception:
            status["db"] = False
        overall = "ok" if status["db"] else "degraded"
        return jsonify({"status": overall, "checks": status}), 200 if overall == "ok" else 503

    # Do not auto-create tables during CLI/migration runs. Enable by setting
    # CREATE_ALL_ON_START=1 in env for quick dev setups (not for production).
    if os.getenv("CREATE_ALL_ON_START") == "1":
        with app.app_context():
            db.create_all()

    return app
