#!/usr/bin/env python3
"""Fix role column issues"""

from app.extensions import db
from app import create_app
from sqlalchemy import text

def fix_role_columns():
    app = create_app()
    with app.app_context():
        try:
            print("🔧 Fixing Role Columns")
            print("=" * 25)
            
            # Check current columns
            columns = db.session.execute(text("""
                SELECT column_name, is_nullable, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND 
                      (column_name = 'role' OR column_name = 'role_id')
                ORDER BY column_name
            """)).fetchall()
            
            print("📋 Role-related columns:")
            for col in columns:
                print(f"   - {col[0]} (nullable: {col[1]}, type: {col[2]})")
            
            # Drop role column if it exists (old column)
            role_exists = any(col[0] == 'role' for col in columns)
            if role_exists:
                print("🗑️  Dropping 'role' column (old column)...")
                db.session.execute(text('ALTER TABLE "user" DROP COLUMN role'))
                db.session.commit()
                print("✅ 'role' column dropped")
            
            # Ensure role_id column exists
            role_id_exists = any(col[0] == 'role_id' for col in columns)
            if not role_id_exists:
                print("➕ Adding 'role_id' column...")
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN role_id INTEGER'))
                db.session.commit()
                print("✅ 'role_id' column added")
            
            # Set role_id as nullable (since it's optional)
            db.session.execute(text('ALTER TABLE "user" ALTER COLUMN role_id DROP NOT NULL'))
            db.session.commit()
            print("✅ 'role_id' column set to nullable")
            
            # Verify final state
            final_columns = db.session.execute(text("""
                SELECT column_name, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND 
                      column_name IN ('role', 'role_id')
                ORDER BY column_name
            """)).fetchall()
            
            print("\n📋 Final role columns:")
            for col in final_columns:
                print(f"   - {col[0]} (nullable: {col[1]})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing role columns: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if fix_role_columns():
        print("\n🎉 Role columns fixed successfully!")
    else:
        print("\n❌ Role column fix failed.")
