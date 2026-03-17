#!/usr/bin/env python3
"""Fix password column issues"""

from app.extensions import db
from app import create_app
from sqlalchemy import text

def fix_password_columns():
    app = create_app()
    with app.app_context():
        try:
            print("🔧 Fixing Password Columns")
            print("=" * 30)
            
            # Check current columns
            columns = db.session.execute(text("""
                SELECT column_name, is_nullable, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND 
                      (column_name = 'password' OR column_name = 'password_hash')
                ORDER BY column_name
            """)).fetchall()
            
            print("📋 Password-related columns:")
            for col in columns:
                print(f"   - {col[0]} (nullable: {col[1]}, type: {col[2]})")
            
            # Drop password column if it exists
            password_exists = any(col[0] == 'password' for col in columns)
            if password_exists:
                print("🗑️  Dropping 'password' column...")
                db.session.execute(text('ALTER TABLE "user" DROP COLUMN password'))
                db.session.commit()
                print("✅ 'password' column dropped")
            
            # Ensure password_hash column exists and is NOT NULL
            password_hash_exists = any(col[0] == 'password_hash' for col in columns)
            if password_hash_exists:
                print("🔧 Updating 'password_hash' column constraints...")
                # Set NOT NULL constraint
                db.session.execute(text('ALTER TABLE "user" ALTER COLUMN password_hash SET NOT NULL'))
                db.session.commit()
                print("✅ 'password_hash' column set to NOT NULL")
            else:
                print("❌ 'password_hash' column should exist but doesn't")
                return False
            
            # Verify final state
            final_columns = db.session.execute(text("""
                SELECT column_name, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND 
                      column_name IN ('password', 'password_hash')
                ORDER BY column_name
            """)).fetchall()
            
            print("\n📋 Final password columns:")
            for col in final_columns:
                print(f"   - {col[0]} (nullable: {col[1]})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing password columns: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if fix_password_columns():
        print("\n🎉 Password columns fixed successfully!")
    else:
        print("\n❌ Password column fix failed.")
