#!/usr/bin/env python3
"""Test database connection and models"""

from app.extensions import db
from app import create_app
from app.models import User, Case, Role, Hearing, Document
from sqlalchemy import text

def test_db_connection():
    app = create_app()
    with app.app_context():
        try:
            # Test basic connection
            result = db.session.execute(text('SELECT 1')).fetchone()
            print(f"✓ Database connection successful: {result}")
            
            # Test model imports
            print("✓ Models imported successfully")
            
            # Test table creation (in development)
            if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
                db.create_all()
                print("✓ SQLite tables created successfully")
            
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False

if __name__ == "__main__":
    test_db_connection()
