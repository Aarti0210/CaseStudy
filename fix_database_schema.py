#!/usr/bin/env python3
"""Fix database schema issues"""

from app.extensions import db
from app import create_app
from sqlalchemy import text

def fix_database_schema():
    app = create_app()
    with app.app_context():
        try:
            print("🔧 Fixing Database Schema")
            print("=" * 30)
            
            # Check user table structure
            user_columns = db.session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                ORDER BY ordinal_position
            """)).fetchall()
            
            print("📋 User table columns:")
            for col in user_columns:
                print(f"   - {col[0]} ({col[1]})")
            
            # Check if password_hash exists
            has_password_hash = any(col[0] == 'password_hash' for col in user_columns)
            
            if not has_password_hash:
                print("\n⚠️  password_hash column missing. Adding it...")
                
                # Add password_hash column
                db.session.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN password_hash VARCHAR(255)
                """))
                
                db.session.commit()
                print("✅ password_hash column added")
            else:
                print("✅ password_hash column exists")
            
            # Check other required columns
            required_columns = ['name', 'email', 'password_hash', 'role_id', 'is_active', 'created_at', 'updated_at']
            existing_columns = [col[0] for col in user_columns]
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            if missing_columns:
                print(f"\n⚠️  Missing columns: {missing_columns}")
                
                # Add missing columns
                if 'name' in missing_columns:
                    db.session.execute(text('ALTER TABLE "user" ADD COLUMN name VARCHAR(100) NOT NULL'))
                if 'email' in missing_columns:
                    db.session.execute(text('ALTER TABLE "user" ADD COLUMN email VARCHAR(120) UNIQUE NOT NULL'))
                if 'role_id' in missing_columns:
                    db.session.execute(text('ALTER TABLE "user" ADD COLUMN role_id INTEGER'))
                if 'is_active' in missing_columns:
                    db.session.execute(text('ALTER TABLE "user" ADD COLUMN is_active BOOLEAN DEFAULT TRUE'))
                if 'created_at' in missing_columns:
                    db.session.execute(text('ALTER TABLE "user" ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'))
                if 'updated_at' in missing_columns:
                    db.session.execute(text('ALTER TABLE "user" ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'))
                
                db.session.commit()
                print("✅ Missing columns added")
            
            # Check role table
            print("\n👥 Checking role table...")
            try:
                role_count = db.session.execute(text('SELECT COUNT(*) FROM role')).fetchone()[0]
                print(f"✅ Role table exists with {role_count} roles")
            except:
                print("⚠️  Role table missing. Creating it...")
                db.session.execute(text("""
                    CREATE TABLE role (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50) UNIQUE NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                db.session.commit()
                print("✅ Role table created")
            
            # Create roles if they don't exist
            roles = ['admin', 'lawyer', 'judge', 'citizen']
            for role_name in roles:
                try:
                    existing_role = db.session.execute(text('SELECT id FROM role WHERE name = :name'), {'name': role_name}).fetchone()
                    if not existing_role:
                        db.session.execute(text('INSERT INTO role (name, description) VALUES (:name, :desc)'), 
                                        {'name': role_name, 'desc': f'{role_name.capitalize()} role'})
                        print(f"✅ Created role: {role_name}")
                    else:
                        print(f"✓ Role exists: {role_name}")
                except Exception as e:
                    print(f"⚠️  Error with role {role_name}: {e}")
            
            db.session.commit()
            
            # Final verification
            print("\n🔍 Final Verification:")
            final_user_columns = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'user' 
                ORDER BY ordinal_position
            """)).fetchall()
            
            print(f"✅ User table has {len(final_user_columns)} columns")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing schema: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if fix_database_schema():
        print("\n🎉 Database schema fixed successfully!")
        print("🚀 Ready to run application tests!")
    else:
        print("\n❌ Schema fix failed. Check the error above.")
