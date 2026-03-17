"""
Configuration Loader
Loads configuration from environment variables using the EnvManager
"""

from app.env_manager import EnvManager

class Config:
    """Base configuration class"""
    
    def __init__(self):
        # Load all configurations
        self.security = EnvManager.get_security_config()
        self.database = EnvManager.get_database_config()
        self.app = EnvManager.get_app_config()
        self.ai = EnvManager.get_ai_config()
        self.email = EnvManager.get_email_config()
        self.rate_limit = EnvManager.get_rate_limit_config()
        self.render = EnvManager.get_render_config()
    
    def validate(self) -> bool:
        """Validate all required configurations"""
        required = EnvManager.validate_required()
        missing = [key for key, exists in required.items() if not exists]
        
        if missing:
            print("❌ Missing required environment variables:")
            for var in missing:
                print(f"  - {var}")
            return False
        
        print("✅ All required environment variables are set")
        return True
    
    def get_flask_config(self) -> dict:
        """Get Flask-specific configuration"""
        return {
            'SECRET_KEY': self.security['secret_key'],
            'JWT_SECRET_KEY': self.security['jwt_secret_key'],
            'SQLALCHEMY_DATABASE_URI': self.database['url'],
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'DEBUG': self.app['debug'],
            'ENV': self.app['flask_env'],
            'LOG_LEVEL': self.app['log_level'],
        }
    
    def get_gunicorn_config(self) -> dict:
        """Get Gunicorn-specific configuration"""
        return {
            'workers': self.render['workers'],
            'worker_class': 'eventlet',
            'bind': f"0.0.0.0:{self.app['port']}",
            'timeout': self.render['timeout'],
            'access_logfile': '-',
            'error_logfile': '-',
        }
    
    def print_summary(self):
        """Print configuration summary"""
        print("🔧 Configuration Loaded")
        print("=" * 25)
        print(f"Environment: {self.app['flask_env']}")
        print(f"Database: {self.database['url'].split('@')[1] if '@' in self.database['url'] else 'Configured'}")
        print(f"Security: {'✅ Configured' if self.security['secret_key'] else '❌ Missing'}")
        print(f"AI Services: {'✅ Enabled' if self.ai['openai_api_key'] else '⚠️  Disabled'}")
        print(f"Workers: {self.render['workers']}")

# Global configuration instance
config = Config()

def load_config():
    """Load and validate configuration"""
    if config.validate():
        return config
    else:
        raise ValueError("Configuration validation failed. Check environment variables.")
