from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# initialized extensions
db = SQLAlchemy()
socketio = SocketIO()
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()
# Limiter initialized with default settings; will read storage_uri from app config if present
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=None  # will be overridden in init_app if config provides RATELIMIT_STORAGE_URI
)
migrate = Migrate()
