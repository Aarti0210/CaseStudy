#!/usr/bin/env python3
from app import create_app
from app.extensions import db

def create_all_tables():
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ All database tables created successfully!")

if __name__ == "__main__":
    create_all_tables()
