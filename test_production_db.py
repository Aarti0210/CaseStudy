#!/usr/bin/env python3
"""Test production database connection"""

from app.extensions import db
from app import create_app
from sqlalchemy import text

def test_production_db():
    app = create_app()
    with app.app_context():
        try:
            print("🔗 Testing Production Database Connection")
            print("=" * 50)
            
            # Show database URL (masked for security)
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            masked_url = db_url.split('@')[-1]  # Show only host/database part
            print(f"Database Host: {masked_url}")
            
            # Test basic connection
            result = db.session.execute(text('SELECT 1')).fetchone()
            print(f"✅ Database connection successful: {result}")
            
            # Test database info
            db_info = db.session.execute(text('SELECT version()')).fetchone()
            print(f"📊 PostgreSQL Version: {db_info[0][:50]}...")
            
            # Test current database
            current_db = db.session.execute(text('SELECT current_database()')).fetchone()
            print(f"🗄️  Current Database: {current_db[0]}")
            
            # Test table creation (check if models can be created)
            from app.models import User, Role, Case
            
            # Check if tables exist
            tables_exist = db.session.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('user', 'role', 'case', 'audit_log')
            """)).fetchone()[0]
            
            print(f"📋 Core tables exist: {tables_exist}/4")
            
            if tables_exist < 4:
                print("⚠️  Some tables missing. Running migrations may be needed.")
                print("💡 Run: flask db upgrade")
            else:
                print("✅ All core tables present")
            
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            print("\n🔧 Troubleshooting:")
            print("1. Check if database server is accessible")
            print("2. Verify connection credentials")
            print("3. Ensure database exists")
            print("4. Check network/firewall settings")
            return False

if __name__ == "__main__":
    success = test_production_db()
    
    if success:
        print("\n🎉 Production database is ready!")
        print("🚀 You can now start the application with:")
        print("   python run.py")
        print("   or")
        print("   gunicorn -k eventlet -w 2 run:app")
    else:
        print("\n⚠️  Please fix database connection issues before starting the application.")
