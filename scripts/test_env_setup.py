#!/usr/bin/env python3
"""
Test Environment Setup
Validates that environment variables are properly loaded and working
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_env_loading():
    """Test that environment variables are loaded correctly"""
    print("🧪 Testing Environment Setup")
    print("=" * 35)
    
    # Test .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    print(f"✅ .env file found: {env_file.absolute()}")
    
    # Load and test environment variables
    try:
        from app.env_manager import EnvManager
        
        # Test required variables
        print("\n🔒 Testing Security Variables:")
        secret_key = EnvManager.get_required('SECRET_KEY')
        print(f"  SECRET_KEY: {'✅ ' + str(len(secret_key)) + ' chars' if len(secret_key) >= 32 else '❌ Too short: ' + str(len(secret_key))}")
        
        jwt_secret = EnvManager.get_required('JWT_SECRET_KEY')
        print(f"  JWT_SECRET_KEY: {'✅ ' + str(len(jwt_secret)) + ' chars' if len(jwt_secret) >= 32 else '❌ Too short: ' + str(len(jwt_secret))}")
        
        # Test database
        print("\n🗄️  Testing Database Configuration:")
        db_url = EnvManager.get_required('DATABASE_URL')
        print(f"  DATABASE_URL: {'✅ Set' if db_url else '❌ Missing'}")
        if 'postgresql://' in db_url:
            print(f"  Type: PostgreSQL")
            print(f"  Host: {db_url.split('@')[1] if '@' in db_url else 'Unknown'}")
        else:
            print(f"  Type: {db_url.split('://')[0] if '://' in db_url else 'Unknown'}")
        
        # Test Flask config
        print("\n🚀 Testing Flask Configuration:")
        flask_env = EnvManager.get_required('FLASK_ENV')
        print(f"  FLASK_ENV: {flask_env}")
        debug = EnvManager.get_bool('DEBUG', False)
        print(f"  DEBUG: {debug}")
        log_level = EnvManager.get_optional('LOG_LEVEL', 'INFO')
        print(f"  LOG_LEVEL: {log_level}")
        
        # Test optional variables
        print("\n🤖 Testing Optional Services:")
        ai_key = EnvManager.get_optional('OPENAI_API_KEY')
        print(f"  OPENAI_API_KEY: {'✅ Set' if ai_key else '⚠️  Not Set'}")
        
        email_server = EnvManager.get_optional('MAIL_SERVER')
        print(f"  MAIL_SERVER: {'✅ Set' if email_server else '⚠️  Not Set'}")
        
        # Test configuration loading
        print("\n🔧 Testing Configuration Loading:")
        from app.config_loader import load_config
        
        config = load_config()
        flask_config = config.get_flask_config()
        print(f"  Flask config loaded: {len(flask_config)} items")
        
        # Test app creation
        print("\n🏗 Testing Application Creation:")
        from app import create_app
        
        app = create_app()
        print(f"  App created: {type(app).__name__}")
        print(f"  Config loaded: {app.config.get('ENV', 'Unknown')}")
        
        # Test database connection through app
        print("\n🗄️  Testing Database Connection:")
        from app.extensions import db
        from sqlalchemy import text
        
        try:
            with app.app_context():
                result = db.session.execute(text('SELECT 1')).fetchone()
                print(f"  Database connection: ✅ {result}")
        except Exception as e:
            print(f"  Database connection: ❌ {e}")
            return False
        
        print("\n🎉 All environment tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def test_render_specific():
    """Test Render-specific configuration"""
    print("🚀 Testing Render-Specific Configuration")
    print("=" * 40)
    
    # Test Render environment variables
    render_vars = [
        'RENDER_SERVICE_NAME',
        'RENDER_SERVICE_ID',
        'RENDER_EXTERNAL_URL',
        'RENDER_EXTERNAL_HOSTNAME'
    ]
    
    print("\n🏢 Render Environment Variables:")
    for var in render_vars:
        value = os.getenv(var)
        if value:
            print(f"  {var}: ✅ Set")
        else:
            print(f"  {var}: ⚠️  Not Set (will be on Render)")
    
    # Test Gunicorn configuration
    print("\n⚙️  Gunicorn Configuration:")
    workers = os.getenv('GUNICORN_WORKERS', '1')
    timeout = os.getenv('GUNICORN_TIMEOUT', '120')
    print(f"  Workers: {workers}")
    print(f"  Timeout: {timeout}s")
    
    return True

def show_env_summary():
    """Show complete environment summary"""
    print("📋 Environment Summary")
    print("=" * 25)
    
    try:
        from app.env_manager import EnvManager
        EnvManager.print_all_configs()
        return True
    except Exception as e:
        print(f"❌ Could not load environment: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Environment Setup')
    parser.add_argument('--render', action='store_true', 
                       help='Test Render-specific configuration')
    parser.add_argument('--summary', action='store_true',
                       help='Show environment summary')
    
    args = parser.parse_args()
    
    if args.summary:
        show_env_summary()
    elif args.render:
        test_render_specific()
    else:
        test_env_loading()

if __name__ == "__main__":
    main()
