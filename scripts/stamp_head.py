import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    # latest revision from migration files
    head = '3271b2efc58b'
    try:
        from sqlalchemy import text
        db.session.execute(text("UPDATE alembic_version SET version_num = :rev"), {'rev': head})
        db.session.commit()
        print('Stamped database to', head)
    except Exception as e:
        print('Failed to stamp:', e)
        db.session.rollback()
