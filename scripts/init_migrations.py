#!/usr/bin/env python3
"""
Initialize database migrations for Render deployment.
Run this script after setting up the database environment.
"""

import os
import sys
from flask import Flask
from flask_migrate import init, migrate, upgrade
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def init_database():
    """Initialize database migrations."""
    app = Flask(__name__)
    
    # Configure app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from app.extensions import db
    db.init_app(app)
    
    with app.app_context():
        try:
            # Initialize migration repository
            init()
            print("✅ Migration repository initialized")
            
            # Create initial migration
            migrate(message='Initial migration')
            print("✅ Initial migration created")
            
            # Apply migration
            upgrade()
            print("✅ Migration applied successfully")
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            raise


# Alias for backward compatibility
init_migrations = init_database
    
    # Configure app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from app.extensions import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        try:
            # Initialize migrations if not already done
            if not os.path.exists('migrations'):
                print("Initializing migrations...")
                init()
                print("✓ Migrations initialized")
            
            # Create initial migration
            print("Creating initial migration...")
            migrate(message='Initial migration')
            print("✓ Initial migration created")
            
            # Apply migrations
            print("Applying migrations...")
            upgrade()
            print("✓ Migrations applied successfully")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
