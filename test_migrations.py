#!/usr/bin/env python
"""Test script to verify migrations work with updated models."""

import os
import sys
from datetime import datetime

sys.path.insert(0, '.')

def check_migration_setup():
    """Check if migrations directory and setup are correct."""
    print("=" * 60)
    print("CHECKING MIGRATION SETUP")
    print("=" * 60)
    
    paths_to_check = [
        'migrations',
        'migrations/alembic.ini',
        'migrations/env.py',
        'migrations/versions'
    ]
    
    for path in paths_to_check:
        if os.path.exists(path):
            print(f"✓ {path} exists")
        else:
            print(f"✗ {path} NOT FOUND")
            return False
    
    return True

def list_existing_migrations():
    """List existing migrations."""
    print("\n" + "=" * 60)
    print("EXISTING MIGRATIONS")
    print("=" * 60)
    
    versions_dir = 'migrations/versions'
    if os.path.exists(versions_dir):
        migrations = [f for f in os.listdir(versions_dir) if f.endswith('.py')]
        if migrations:
            print(f"Found {len(migrations)} migration(s):")
            for migration in sorted(migrations):
                print(f"  - {migration}")
        else:
            print("No migrations found (fresh setup)")
        return True
    return False

def test_model_discovery():
    """Test that models are discoverable."""
    print("\n" + "=" * 60)
    print("TESTING MODEL DISCOVERY")
    print("=" * 60)
    
    try:
        from app.extensions import db
        from app.models import User, Role, Case, AuditLog
        
        # Check that models are registered with SQLAlchemy
        models = [User, Role, Case, AuditLog]
        
        for model in models:
            table_name = model.__tablename__ if hasattr(model, '__tablename__') else model.__name__.lower()
            print(f"✓ {model.__name__:15} -> table: {table_name}")
        
        print(f"\n✓ {len(models)} core models discoverable")
        return True
        
    except Exception as e:
        print(f"✗ Error discovering models: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_model_schemas():
    """Check model schema definitions."""
    print("\n" + "=" * 60)
    print("MODEL SCHEMAS")
    print("=" * 60)
    
    try:
        from app.models import User, Role, Case, AuditLog
        
        models = {
            'User': User,
            'Role': Role,
            'Case': Case,
            'AuditLog': AuditLog
        }
        
        for name, model in models.items():
            columns = [col.name for col in model.__table__.columns]
            print(f"\n{name}:")
            print(f"  Columns: {', '.join(columns[:3])}{'...' if len(columns) > 3 else ''}")
            print(f"  Total: {len(columns)} columns")
        
        return True
        
    except Exception as e:
        print(f"✗ Error checking schemas: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all migration tests."""
    success = True
    
    success = check_migration_setup() and success
    success = list_existing_migrations() and success
    success = test_model_discovery() and success
    success = check_model_schemas() and success
    
    print("\n" + "=" * 60)
    print("MIGRATION READINESS")
    print("=" * 60)
    
    if success:
        print("""
✓ Migration system is ready!

NEXT STEPS:
1. Generate migration: python -m flask db migrate -m "Add role model and password hashing"
2. Review migrations/versions/[latest].py
3. Apply migration: python -m flask db upgrade
4. Run tests: pytest tests/
        """)
    else:
        print("✗ Some checks failed - review output above")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
