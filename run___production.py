"""
Production-ready application entry point.
Secure, optimized, and deployment-ready.
"""

import os
import sys

# Monkey-patch early so that eventlet green threads behave correctly
import eventlet
eventlet.monkey_patch()

from app import create_app
from app.extensions import socketio

# Create application instance
app = create_app()


def main():
    """Main entry point for production deployment."""
    try:
        # Get configuration from environment
        port = int(os.environ.get("PORT", 5000))
        host = os.environ.get("HOST", "0.0.0.0")
        
        # Log startup information
        app.logger.info(f"Starting Judicial Supreme Backend on {host}:{port}")
        app.logger.info(f"Environment: {app.config.get('FLASK_ENV', 'unknown')}")
        app.logger.info(f"Debug Mode: {app.config.get('DEBUG', False)}")
        
        # Production deployment
        if os.getenv("FLASK_ENV") == "production":
            app.logger.info("Running in production mode")
            # Use gunicorn for production (recommended)
            if 'gunicorn' in sys.modules:
                app.logger.info("Running under Gunicorn")
                return app
            else:
                app.logger.warning("Not running under Gunicorn - consider using Gunicorn for production")
                app.logger.info("Recommended: gunicorn -k eventlet -w 2 run:app")
        
        # Development mode
        else:
            app.logger.info("Running in development mode")
            socketio.run(app, debug=True, host=host, port=port)
    
    except Exception as e:
        app.logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
