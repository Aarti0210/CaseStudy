"""Generate CREATE TABLE statements for all models.

This helper is provided for development. It compiles DDL using the
current SQLAlchemy dialect (PostgreSQL by default when DATABASE_URL is set
appropriately)."""
import os, sys
# ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import models so they register with SQLAlchemy metadata
import app.models  # noqa: F401
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    print("Loaded tables:", db.metadata.tables.keys())
    print("Sorted tables count:", len(db.metadata.sorted_tables))
    from sqlalchemy.schema import CreateTable
    # Get the dialect from the bound engine (PostgreSQL for Render, SQLite for dev)
    engine = db.engine
    dialect = engine.dialect
    for table in db.metadata.sorted_tables:
        # compile create statement using current database dialect
        stmt = str(CreateTable(table).compile(dialect=dialect, compile_kwargs={"literal_binds": True}))
        print(stmt)
        print()
