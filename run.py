"""
Production-safe application entry point.
Use with Gunicorn: gunicorn -k eventlet -w 2 run:app
For local development: python -m flask run
"""

# monkey-patch early so that eventlet green threads behave correctly.
# Without this, gunicorn emits "1 RLock(s) were not greened" on startup.
import eventlet
eventlet.monkey_patch()

from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == "__main__":
    # Development only: use flask's built-in server
    # Production: use Gunicorn with eventlet worker
    import os
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"

    if os.getenv("FLASK_ENV") == "development":
        socketio.run(app, debug=True, host=host, port=port)
    else:
        # warn the user but still start the server so that local
        # `python run.py` doesn't immediately exit with an error code.
        # This makes the command easier to use for quick checks and
        # testing while preserving the documented recommendation.
        print("WARNING: Running built-in server; use Gunicorn for production.")
        print("  Standard deployment: gunicorn -k eventlet -w 2 run:app")
        print("  Render Free (1 worker): gunicorn -k eventlet -w 1 run:app")
        socketio.run(app, host=host, port=port)

