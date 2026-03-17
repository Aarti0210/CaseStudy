"""
Environment Variable Manager
Handles loading and validation of environment variables with fallbacks
"""

import os
from typing import Optional, Dict, Any

class EnvManager:
    """Centralized environment variable management"""
    
    @staticmethod
    def get_required(key: str) -> str:
        """Get required environment variable"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value
    
    @staticmethod
    def get_optional(key: str, default: Any = None) -> Any:
        """Get optional environment variable with default"""
        return os.getenv(key, default)
    
    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        """Get integer environment variable"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @staticmethod
    def validate_required() -> Dict[str, bool]:
        """Validate all required environment variables"""
        required_vars = {
            'SECRET_KEY': bool(os.getenv('SECRET_KEY')),
            'JWT_SECRET_KEY': bool(os.getenv('JWT_SECRET_KEY')),
            'DATABASE_URL': bool(os.getenv('DATABASE_URL')),
            'FLASK_ENV': bool(os.getenv('FLASK_ENV')),
        }
        
        return required_vars
    
    @staticmethod
    def get_database_config() -> Dict[str, str]:
        """Get database configuration"""
        return {
            'url': EnvManager.get_required('DATABASE_URL'),
            'type': 'postgresql',
        }
    
    @staticmethod
    def get_security_config() -> Dict[str, str]:
        """Get security configuration"""
        return {
            'secret_key': EnvManager.get_required('SECRET_KEY'),
            'jwt_secret_key': EnvManager.get_required('JWT_SECRET_KEY'),
        }
    
    @staticmethod
    def get_app_config() -> Dict[str, Any]:
        """Get application configuration"""
        return {
            'flask_env': EnvManager.get_required('FLASK_ENV'),
            'debug': EnvManager.get_bool('DEBUG', False),
            'log_level': EnvManager.get_optional('LOG_LEVEL', 'INFO'),
            'port': EnvManager.get_int('PORT', 5000),
        }
    
    @staticmethod
    def get_ai_config() -> Dict[str, Any]:
        """Get AI service configuration"""
        return {
            'openai_api_key': EnvManager.get_optional('OPENAI_API_KEY'),
            'ai_timeout': EnvManager.get_int('AI_TIMEOUT_SECONDS', 30),
            'ai_max_tokens': EnvManager.get_int('AI_MAX_TOKENS', 4000),
        }
    
    @staticmethod
    def get_email_config() -> Dict[str, Any]:
        """Get email configuration"""
        return {
            'server': EnvManager.get_optional('MAIL_SERVER'),
            'port': EnvManager.get_int('MAIL_PORT', 587),
            'use_tls': EnvManager.get_bool('MAIL_USE_TLS', True),
            'username': EnvManager.get_optional('MAIL_USERNAME'),
            'password': EnvManager.get_optional('MAIL_PASSWORD'),
            'default_sender': EnvManager.get_optional('MAIL_DEFAULT_SENDER'),
        }
    
    @staticmethod
    def get_rate_limit_config() -> Dict[str, Any]:
        """Get rate limiting configuration"""
        return {
            'storage_uri': EnvManager.get_optional('RATELIMIT_STORAGE_URI'),
        }
    
    @staticmethod
    def get_render_config() -> Dict[str, Any]:
        """Get Render-specific configuration"""
        return {
            'workers': EnvManager.get_int('GUNICORN_WORKERS', 1),
            'timeout': EnvManager.get_int('GUNICORN_TIMEOUT', 120),
        }
    
    @staticmethod
    def print_all_configs():
        """Print all configurations for debugging"""
        print("🔧 Environment Configuration")
        print("=" * 30)
        
        # Required variables
        print("🔒 Security:")
        security = EnvManager.get_security_config()
        print(f"  SECRET_KEY: {'✅ Set' if security['secret_key'] else '❌ Missing'}")
        print(f"  JWT_SECRET_KEY: {'✅ Set' if security['jwt_secret_key'] else '❌ Missing'}")
        
        # Database
        print("\n🗄️  Database:")
        db_config = EnvManager.get_database_config()
        print(f"  URL: {'✅ Set' if db_config['url'] else '❌ Missing'}")
        
        # Application
        print("\n🚀 Application:")
        app_config = EnvManager.get_app_config()
        print(f"  FLASK_ENV: {app_config['flask_env']}")
        print(f"  DEBUG: {app_config['debug']}")
        print(f"  LOG_LEVEL: {app_config['log_level']}")
        
        # Optional services
        print("\n🤖 AI Services:")
        ai_config = EnvManager.get_ai_config()
        print(f"  OPENAI_API_KEY: {'✅ Set' if ai_config['openai_api_key'] else '⚠️  Not Set'}")
        
        print("\n📧 Rate Limiting:")
        rate_config = EnvManager.get_rate_limit_config()
        print(f"  STORAGE_URI: {'✅ Set' if rate_config['storage_uri'] else '⚠️  Using Memory'}")
        
        print("\n📧 Render:")
        render_config = EnvManager.get_render_config()
        print(f"  GUNICORN_WORKERS: {render_config['workers']}")
        print(f"  GUNICORN_TIMEOUT: {render_config['timeout']}")

# Convenience functions for backward compatibility
get_env = EnvManager.get_required
get_optional_env = EnvManager.get_optional
get_bool_env = EnvManager.get_bool
get_int_env = EnvManager.get_int
