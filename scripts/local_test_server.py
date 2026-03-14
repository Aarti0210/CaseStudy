#!/usr/bin/env python3
"""
Local test server for development and testing.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import socketio

def run_local_server():
    """Run local development server."""
    
    # Set development environment
    os.environ["FLASK_ENV"] = "development"
    os.environ["DEBUG"] = "true"
    
    # Create app
    app = create_app()
    
    # Get configuration
    host = "127.0.0.1"
    port = 8000
    
    print(f"🚀 Starting Judicial Supreme Backend (Local Development)")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🌐 Server URL: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/api/v1/docs")
    print(f"💚 Health Check: http://{host}:{port}/health")
    print(f"🔌 Socket.IO: ws://{host}:{port}/socket.io/")
    print("=" * 60)
    
    try:
        # Run with Socket.IO
        socketio.run(
            app,
            host=host,
            port=port,
            debug=True,
            use_reloader=False  # Disable reloader to avoid double startup
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_local_server()
