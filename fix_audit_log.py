#!/usr/bin/env python3
"""Fix audit_log table columns"""

from app.extensions import db
from app import create_app
from sqlalchemy import text

def fix_audit_log_table():
    app = create_app()
    with app.app_context():
        try:
            print("🔧 Fixing Audit Log Table")
            print("=" * 25)
            
            # Check current columns
            columns = db.session.execute(text("""
                SELECT column_name, is_nullable, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'audit_log' 
                ORDER BY ordinal_position
            """)).fetchall()
            
            print("📋 Audit log table columns:")
            for col in columns:
                print(f"   - {col[0]} (nullable: {col[1]}, type: {col[2]})")
            
            column_names = [col[0] for col in columns]
            
            # Add missing columns
            if 'ip_address' not in column_names:
                print("➕ Adding 'ip_address' column...")
                db.session.execute(text('ALTER TABLE audit_log ADD COLUMN ip_address VARCHAR(45)'))
                db.session.commit()
                print("✅ 'ip_address' column added")
            
            # Verify final state
            final_columns = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'audit_log' 
                ORDER BY ordinal_position
            """)).fetchall()
            
            print(f"\n📋 Final audit log table columns: {len(final_columns)}")
            for col in final_columns:
                print(f"   - {col[0]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing audit log table: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if fix_audit_log_table():
        print("\n🎉 Audit log table fixed successfully!")
    else:
        print("\n❌ Audit log table fix failed.")
