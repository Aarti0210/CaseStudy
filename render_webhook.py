#!/usr/bin/env python3
"""
Render Webhook Handler
Run this after deployment to initialize the database with proper schema
"""

import os
import sys
from app.extensions import db
from app import create_app
from app.models import Role, User
from sqlalchemy import text

def initialize_production_database():
    """Initialize database with proper schema and initial data"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🚀 Initializing Production Database on Render")
            print("=" * 50)
            
            # Test database connection
            result = db.session.execute(text('SELECT 1')).fetchone()
            print(f"✅ Database connected: {result}")
            
            # Run migrations to ensure schema is up to date
            print("🔄 Running database migrations...")
            try:
                from flask_migrate import upgrade
                upgrade()
                print("✅ Migrations completed")
            except Exception as e:
                print(f"⚠️  Migration issue: {e}")
                print("🔧 Creating tables manually...")
                db.create_all()
                print("✅ Tables created manually")
            
            # Create initial roles
            print("👥 Creating user roles...")
            roles = [
                ('admin', 'System administrator with full access'),
                ('lawyer', 'Legal professional who can manage cases'),
                ('judge', 'Judicial officer who can hear cases'),
                ('citizen', 'Regular user who can create cases')
            ]
            
            for role_name, description in roles:
                existing_role = Role.query.filter_by(name=role_name).first()
                if not existing_role:
                    role = Role(name=role_name, description=description)
                    db.session.add(role)
                    print(f"  ✅ Created role: {role_name}")
                else:
                    print(f"  ✓ Role exists: {role_name}")
            
            # Create admin user if not exists
            print("\n👤 Creating admin user...")
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@judicial.local')
            admin_password = os.getenv('ADMIN_PASSWORD', 'Admin123!@#')
            
            existing_admin = User.query.filter_by(email=admin_email).first()
            if not existing_admin:
                admin_role = Role.query.filter_by(name='admin').first()
                admin_user = User(
                    name='System Administrator',
                    email=admin_email,
                    role_id=admin_role.id
                )
                admin_user.set_password(admin_password)
                db.session.add(admin_user)
                print(f"  ✅ Created admin user: {admin_email}")
                print(f"  🔑 Password: {admin_password}")
            else:
                print(f"  ✓ Admin user exists: {admin_email}")
            
            db.session.commit()
            
            # Verify database
            print("\n🔍 Database Verification:")
            tables = db.session.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)).fetchone()[0]
            
            print(f"  📋 Total tables: {tables}")
            
            role_count = Role.query.count()
            user_count = User.query.count()
            
            print(f"  👥 Roles: {role_count}")
            print(f"  👤 Users: {user_count}")
            
            print("\n🎉 Production database initialized successfully!")
            print("🚀 Your Judicial Supreme Backend is ready!")
            
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            db.session.rollback()
            return False

def health_check():
    """Perform comprehensive health check"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n🏥 Comprehensive Health Check")
            print("=" * 35)
            
            # Database health
            try:
                result = db.session.execute(text('SELECT 1')).fetchone()
                print("✅ Database: Connected")
            except Exception as e:
                print(f"❌ Database: {e}")
                return False
            
            # Model health
            try:
                from app.models import User, Role, Case
                user_count = User.query.count()
                role_count = Role.query.count()
                print(f"✅ Models: Users ({user_count}), Roles ({role_count})")
            except Exception as e:
                print(f"❌ Models: {e}")
                return False
            
            # Configuration health
            secret_key = app.config.get('SECRET_KEY', '')
            jwt_secret = app.config.get('JWT_SECRET_KEY', '')
            
            if len(secret_key) >= 32 and len(jwt_secret) >= 32:
                print("✅ Security: Keys properly configured")
            else:
                print("❌ Security: Keys too short")
                return False
            
            # Database URL check
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'postgresql://' in db_url:
                print("✅ Configuration: PostgreSQL database")
            else:
                print("❌ Configuration: Not PostgreSQL")
                return False
            
            print("\n🎉 All health checks passed!")
            return True
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

if __name__ == "__main__":
    print("🔧 Render Deployment Helper")
    print("=" * 30)
    
    # Initialize database
    if initialize_production_database():
        # Run health check
        if health_check():
            print("\n✅ RENDER DEPLOYMENT READY!")
            print("\n📋 Next Steps:")
            print("1. Test your API endpoints")
            print("2. Connect your frontend application")
            print("3. Set up monitoring and alerts")
            print("4. Configure custom domain (optional)")
        else:
            print("\n⚠️  Health check failed - check logs above")
    else:
        print("\n❌ Database initialization failed - check error above")
