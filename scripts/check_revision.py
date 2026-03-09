import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    try:
        from sqlalchemy import text
        res = db.session.execute(text('SELECT version_num FROM alembic_version')).fetchall()
        print('applied revisions:', res)
    except Exception as e:
        print('error reading alembic_version:', e)
