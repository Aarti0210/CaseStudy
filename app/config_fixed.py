"""
Configuration management for Flask application.
Handles environment-based configuration with proper validation.
"""

import os
from pathlib import Path
from datetime import timedelta


class BaseConfig:
    """Base configuration class."""
    
    # Core Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database configuration
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    DEFAULT_SQLITE = f"sqlite:///{PROJECT_ROOT / 'judicial_dev.db'}"
    
    # Normalize database URL
    _dburl = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
    if isinstance(_dburl, str) and _dburl.startswith("postgres://"):
        _dburl = _dburl.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _dburl
    
    # Database engine options
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False") == "True"
    
    if _dburl.startswith("sqlite"):
        SQLALCHEMY_ENGINE_OPTIONS = {}
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", 5)),
            "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 2)),
            "pool_timeout": int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", 30)),
            "pool_recycle": int(os.getenv("SQLALCHEMY_POOL_RECYCLE", 3600)),
            "pool_pre_ping": True,
        }
    
    # File upload settings
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    
    # JWT settings
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 86400))
    
    # OTP settings
    OTP_TTL = int(os.getenv("OTP_TTL", 300))
    OTP_RESEND_COOLDOWN = int(os.getenv("OTP_RESEND_COOLDOWN", 60))
    OTP_SEND_MAX_RETRIES = int(os.getenv("OTP_SEND_MAX_RETRIES", 3))
    
    # Rate limiting
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day;50 per hour")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", None)
    
    # Email settings
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "no-reply@judicial.local")
    
    # ML settings
    LOW_DELAY_THRESHOLD = int(os.getenv("LOW_DELAY_THRESHOLD", 365))
    HIGH_DELAY_THRESHOLD = int(os.getenv("HIGH_DELAY_THRESHOLD", 900))
    
    # AI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AI_MODEL = os.getenv("AI_MODEL", "gpt-4-turbo")
    AI_CACHE_TTL = int(os.getenv("AI_CACHE_TTL", 300))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @staticmethod
    def validate_config():
        """Validate critical configuration settings."""
        errors = []
        
        if not BaseConfig.SECRET_KEY or len(BaseConfig.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be at least 32 characters")
        
        if not BaseConfig.JWT_SECRET_KEY or len(BaseConfig.JWT_SECRET_KEY) < 32:
            errors.append("JWT_SECRET_KEY must be at least 32 characters")
        
        if BaseConfig.OPENAI_API_KEY and not BaseConfig.OPENAI_API_KEY.startswith("sk-"):
            errors.append("OPENAI_API_KEY appears invalid")
        
        return errors


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Production-specific overrides
    SQLALCHEMY_ECHO = False
    
    @staticmethod
    def validate_config():
        """Validate production-specific settings."""
        errors = BaseConfig.validate_config()
        
        # Additional production validations
        if BaseConfig.MAIL_SERVER == "smtp.example.com":
            errors.append("MAIL_SERVER must be configured for production")
        
        if not BaseConfig.RATELIMIT_STORAGE_URI:
            errors.append("RATELIMIT_STORAGE_URI should be configured for production")
        
        return errors


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
