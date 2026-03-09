from sqlalchemy import inspect

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    insp = inspect(db.engine)
    tables = insp.get_table_names()
    print("Tables in DB:")
    for t in tables:
        print("-", t)
