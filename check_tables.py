#!/usr/bin/env python3
"""Check and create missing database tables"""

from app.extensions import db
from app import create_app
from app.models import User, Role, Case, Hearing, Document, Payment, Notification, AuditLog, OTP
from sqlalchemy import text

def check_and_create_tables():
    app = create_app()
    with app.app_context():
        try:
            print("🗄️  Database Table Check")
            print("=" * 30)
            
            # Get all tables in database
            all_tables = db.session.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)).fetchall()
            
            table_names = [row[0] for row in all_tables]
            print(f"📋 Existing tables: {len(table_names)}")
            for table in table_names:
                print(f"  - {table}")
            
            # Expected tables from models
            expected_tables = [
                'user', 'role', 'case', 'hearing', 'document', 
                'payment', 'notification', 'audit_log', 'otp',
                'case_activity', 'ai_log', 'billing', 'chat_message'
            ]
            
            missing_tables = [t for t in expected_tables if t not in table_names]
            
            if missing_tables:
                print(f"\n⚠️  Missing tables: {missing_tables}")
                print("🔧 Creating missing tables...")
                
                # Create all tables
                db.create_all()
                print("✅ All tables created successfully")
                
                # Verify again
                all_tables = db.session.execute(text("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """)).fetchall()
                
                table_names = [row[0] for row in all_tables]
                print(f"\n📋 Total tables after creation: {len(table_names)}")
                
            else:
                print("\n✅ All expected tables exist!")
            
            # Create initial roles if they don't exist
            print("\n👥 Creating initial roles...")
            roles = ['admin', 'lawyer', 'judge', 'citizen']
            
            for role_name in roles:
                role = Role.query.filter_by(name=role_name).first()
                if not role:
                    role = Role(name=role_name, description=f'{role_name.capitalize()} role')
                    db.session.add(role)
                    print(f"  ✅ Created role: {role_name}")
                else:
                    print(f"  ✓ Role exists: {role_name}")
            
            db.session.commit()
            print("\n🎉 Database setup complete!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up database: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    check_and_create_tables()
