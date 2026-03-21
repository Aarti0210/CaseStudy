"""
Flask extensions initialization module.
Centralizes all Flask extensions for clean initialization.
"""

from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO()
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()
migrate = Migrate()

# Limiter will be initialized in app factory to avoid conflicts
