from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    try:
        engine = db.engine
        with engine.connect() as conn:
            print("OK: DB connection succeeded")
    except Exception as e:
        print("ERROR: DB connection failed:", e)
