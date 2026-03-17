#!/usr/bin/env python3
"""Fix case table columns"""

from app.extensions import db
from app import create_app
from sqlalchemy import text

def fix_case_table():
    app = create_app()
    with app.app_context():
        try:
            print("🔧 Fixing Case Table")
            print("=" * 20)
            
            # Check current columns
            columns = db.session.execute(text("""
                SELECT column_name, is_nullable, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'case' 
                ORDER BY ordinal_position
            """)).fetchall()
            
            print("📋 Case table columns:")
            for col in columns:
                print(f"   - {col[0]} (nullable: {col[1]}, type: {col[2]})")
            
            column_names = [col[0] for col in columns]
            
            # Add missing columns
            if 'updated_at' not in column_names:
                print("➕ Adding 'updated_at' column...")
                db.session.execute(text('ALTER TABLE "case" ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'))
                db.session.commit()
                print("✅ 'updated_at' column added")
            
            # Check other required columns
            required_columns = ['id', 'title', 'description', 'status', 'created_at', 'updated_at', 'created_by', 'assigned_judge_id']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"⚠️  Missing columns: {missing_columns}")
                
                for col in missing_columns:
                    if col == 'assigned_judge_id':
                        db.session.execute(text('ALTER TABLE "case" ADD COLUMN assigned_judge_id INTEGER'))
                    elif col == 'description':
                        db.session.execute(text('ALTER TABLE "case" ADD COLUMN description TEXT'))
                    elif col == 'status':
                        db.session.execute(text('ALTER TABLE "case" ADD COLUMN status VARCHAR(50) DEFAULT \'Pending\''))
                
                db.session.commit()
                print("✅ Missing columns added")
            
            # Verify final state
            final_columns = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'case' 
                ORDER BY ordinal_position
            """)).fetchall()
            
            print(f"\n📋 Final case table columns: {len(final_columns)}")
            for col in final_columns:
                print(f"   - {col[0]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing case table: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if fix_case_table():
        print("\n🎉 Case table fixed successfully!")
    else:
        print("\n❌ Case table fix failed.")
