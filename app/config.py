import os
from datetime import timedelta
from pathlib import Path


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    # Do not use a default for JWT secret; must be provided via env in production
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Database URL: prefer `DATABASE_URL` env var; normalize Postgres prefix
    _PROJECT_ROOT = Path(__file__).resolve().parents[1]
    _DEFAULT_SQLITE = f"sqlite:///{_PROJECT_ROOT / 'judicial_dev.db'}"
    # Render and other providers may supply postgres:// which SQLAlchemy
    # warns about; convert to postgresql:// automatically.
    _dburl = os.getenv("DATABASE_URL", _DEFAULT_SQLITE)
    if isinstance(_dburl, str) and _dburl.startswith("postgres://"):
        _dburl = _dburl.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _dburl
    # Optional SQLAlchemy echo for debugging
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False") == "True"
    # Folder where user-uploaded files are stored. On hosts with
    # ephemeral filesystems (Render Free, Heroku), this directory will be
    # cleared on each deploy; use an external object store for persistence.
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))

    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 86400))
    OTP_TTL = int(os.getenv("OTP_TTL", 300))

    # risk thresholds (days) used by ML predictor
    LOW_DELAY_THRESHOLD = int(os.getenv("LOW_DELAY_THRESHOLD", 365))
    HIGH_DELAY_THRESHOLD = int(os.getenv("HIGH_DELAY_THRESHOLD", 900))

    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day;50 per hour")
    # Optional storage URI for Flask-Limiter (e.g. redis://localhost:6379)
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", None)
    # SQLAlchemy connection pooling settings (helpful for FreeDB/Render).
    # Do not apply pool settings for SQLite in-memory or file URIs (they are
    # incompatible with some pool parameters). The engine options will be an
    # empty dict for sqlite URIs and a configured dict otherwise.
    _db_url = os.getenv("DATABASE_URL", _DEFAULT_SQLITE)
    if _db_url.startswith("sqlite"):
        SQLALCHEMY_ENGINE_OPTIONS = {}
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", 5)),
            "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 2)),
            "pool_timeout": int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", 30)),
            "pool_recycle": int(os.getenv("SQLALCHEMY_POOL_RECYCLE", 1800)),
            "pool_pre_ping": True,  # Verify connection before use (important for Render/external DB)
        }
    # Mail settings (for OTP/email delivery)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "no-reply@judicial.local")
    # OTP resend cooldown (seconds) and retry behavior
    OTP_RESEND_COOLDOWN = int(os.getenv("OTP_RESEND_COOLDOWN", 60))
    OTP_SEND_MAX_RETRIES = int(os.getenv("OTP_SEND_MAX_RETRIES", 3))


class DevelopmentConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    """Config for pytest and test environments.
    Forces SQLite in-memory, disables rate limiting, and uses dummy JWT secret.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}  # SQLite in-memory doesn't support pool options
    RATELIMIT_ENABLED = False
    JWT_SECRET_KEY = "testing-secret-minimum-32-chars-long"
    SECRET_KEY = "testing-secret-minimum-32-chars-long"


class ProductionConfig(BaseConfig):
    # In production enforce DATABASE_URL and do not fall back to SQLite.
    _prod_db = os.getenv("DATABASE_URL")
    if not _prod_db:
        raise RuntimeError("DATABASE_URL must be set in production environment")
    # normalize Render's postgres:// prefix to postgresql:// for SQLAlchemy
    if isinstance(_prod_db, str) and _prod_db.startswith("postgres://"):
        _prod_db = _prod_db.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _prod_db

    # Ensure production engine options include pre-ping for remote DB stability
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", 5)),
        "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 2)),
        "pool_timeout": int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", 30)),
        "pool_recycle": int(os.getenv("SQLALCHEMY_POOL_RECYCLE", 1800)),
        "pool_pre_ping": True,
    }
    # Longer token expiry in production can be adjusted via env
