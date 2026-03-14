#!/usr/bin/env python3
"""
Production server startup script with proper port binding and health checks.
"""

import os
import sys
import time
import socket

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def check_port_available(host, port):
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False

def wait_for_database(app):
    """Wait for database to be ready."""
    from app.extensions import db
    from sqlalchemy import text
    
    max_retries = 30
    for i in range(max_retries):
        try:
            with app.app_context():
                db.session.execute(text("SELECT 1"))
                print("✅ Database connection successful")
                return True
        except Exception as e:
            print(f"⏳ Waiting for database... ({i+1}/{max_retries})")
            time.sleep(2)
    
    print("❌ Database connection failed")
    return False

def run_production_server():
    """Run the production server with proper configuration."""
    
    # Create Flask app
    app = create_app()
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting Judicial Supreme Backend")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🌍 Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    # Check port availability
    if not check_port_available(host, port):
        print(f"❌ Port {port} is already in use")
        sys.exit(1)
    
    # Wait for database
    if not wait_for_database(app):
        print("❌ Cannot start without database connection")
        sys.exit(1)
    
    # Run migrations if needed
    if os.getenv("AUTO_MIGRATE", "false").lower() == "true":
        print("🔄 Running auto-migration...")
        try:
            from flask_migrate import upgrade
            with app.app_context():
                upgrade()
            print("✅ Migrations completed")
        except Exception as e:
            print(f"⚠️ Migration failed: {e}")
    
    # Start server
    print(f"🌐 Server starting on http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/api/v1/docs")
    print(f"💚 Health Check: http://{host}:{port}/health")
    
    try:
        if os.getenv("FLASK_ENV") == "production":
            # Use Gunicorn for production
            import subprocess
            cmd = [
                "gunicorn",
                "-k", "eventlet",
                "-w", os.getenv("GUNICORN_WORKERS", "1"),
                "-b", f"{host}:{port}",
                "--timeout", "120",
                "--access-logfile", "-",
                "--error-logfile", "-",
                "run:app"
            ]
            
            print(f"🔧 Running with Gunicorn: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        else:
            # Development server
            from app.extensions import socketio
            socketio.run(
                app,
                host=host,
                port=port,
                debug=os.getenv("DEBUG", "false").lower() == "true"
            )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_production_server()
