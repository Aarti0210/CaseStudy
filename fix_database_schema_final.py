#!/usr/bin/env python3
"""
Database schema fix script.
Fixes SQL keyword conflicts using proper PostgreSQL syntax.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(project_root))

def fix_database_schema():
    """Fix database schema issues."""
    print("🔧 Fixing Database Schema Issues...")
    print("=" * 60)
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import app components
        from app import create_app
        from app.extensions import db
        from sqlalchemy import text
        
        # Create app context
        app = create_app()
        
        with app.app_context():
            print("✅ App context created")
            
            # Fix 1: Rename 'case' table to 'legal_case' (using proper PostgreSQL syntax)
            print("\n📋 Fix 1: Renaming 'case' table to 'legal_case'")
            try:
                # Check if 'case' table exists
                result = db.session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'case'
                    )
                """))
                case_exists = result.fetchone()[0]
                
                if case_exists:
                    print("✅ Found 'case' table - renaming to 'legal_case'")
                    
                    # Rename table using proper PostgreSQL syntax
                    db.session.execute(text('ALTER TABLE "case" RENAME TO "legal_case"'))
                    db.session.commit()
                    print("✅ Table renamed successfully")
                else:
                    print("ℹ️  'case' table not found - checking for 'legal_case'")
                    
                    # Check if 'legal_case' already exists
                    result = db.session.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'legal_case'
                        )
                    """))
                    legal_case_exists = result.fetchone()[0]
                    
                    if legal_case_exists:
                        print("✅ 'legal_case' table already exists")
                    else:
                        print("❌ Neither 'case' nor 'legal_case' table found")
                        
            except Exception as e:
                print(f"❌ Failed to rename table: {str(e)}")
                db.session.rollback()
            
            # Fix 2: Update foreign key references (using quoted identifiers)
            print("\n📋 Fix 2: Updating foreign key references")
            try:
                # Update document table
                db.session.execute(text('''
                    ALTER TABLE document 
                    DROP CONSTRAINT IF EXISTS document_case_id_fkey,
                    ADD CONSTRAINT document_case_id_fkey 
                    FOREIGN KEY (case_id) REFERENCES "legal_case"(id)
                '''))
                
                # Update hearing table
                db.session.execute(text('''
                    ALTER TABLE hearing 
                    DROP CONSTRAINT IF EXISTS hearing_case_id_fkey,
                    ADD CONSTRAINT hearing_case_id_fkey 
                    FOREIGN KEY (case_id) REFERENCES "legal_case"(id)
                '''))
                
                # Update payment table
                db.session.execute(text('''
                    ALTER TABLE payment 
                    DROP CONSTRAINT IF EXISTS payment_case_id_fkey,
                    ADD CONSTRAINT payment_case_id_fkey 
                    FOREIGN KEY (case_id) REFERENCES "legal_case"(id)
                '''))
                
                # Update audit_log table
                db.session.execute(text('''
                    ALTER TABLE audit_log 
                    DROP CONSTRAINT IF EXISTS audit_log_case_id_fkey,
                    ADD CONSTRAINT audit_log_case_id_fkey 
                    FOREIGN KEY (case_id) REFERENCES "legal_case"(id)
                '''))
                
                db.session.commit()
                print("✅ Foreign key references updated")
                
            except Exception as e:
                print(f"❌ Failed to update foreign keys: {str(e)}")
                db.session.rollback()
            
            # Fix 3: Improve audit_log table
            print("\n📋 Fix 3: Improving audit_log table")
            try:
                # Add user_agent column if not exists
                result = db.session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'audit_log' 
                        AND column_name = 'user_agent'
                    )
                """))
                user_agent_exists = result.fetchone()[0]
                
                if not user_agent_exists:
                    db.session.execute(text('''
                        ALTER TABLE audit_log 
                        ADD COLUMN user_agent VARCHAR(500)
                    '''))
                    print("✅ Added user_agent column")
                
                # Increase ip_address column size
                db.session.execute(text('''
                    ALTER TABLE audit_log 
                    ALTER COLUMN ip_address TYPE VARCHAR(64)
                '''))
                print("✅ Increased ip_address column size")
                
                db.session.commit()
                print("✅ audit_log table improvements completed")
                
            except Exception as e:
                print(f"❌ Failed to improve audit_log: {str(e)}")
                db.session.rollback()
            
            # Fix 4: Create missing indexes (using quoted identifiers)
            print("\n📋 Fix 4: Creating missing indexes")
            try:
                indexes_to_create = [
                    ('idx_legal_case_status', '"legal_case"', 'status'),
                    ('idx_legal_case_created_by', '"legal_case"', 'created_by'),
                    ('idx_audit_log_composite', 'audit_log', 'timestamp, user_id'),
                ]
                
                for index_name, table, columns in indexes_to_create:
                    try:
                        db.session.execute(text(f'''
                            CREATE INDEX IF NOT EXISTS {index_name} 
                            ON {table} ({columns})
                        '''))
                        print(f"✅ Created index: {index_name}")
                    except Exception as e:
                        print(f"⚠️  Index {index_name} may already exist: {str(e)}")
                
                db.session.commit()
                print("✅ Index creation completed")
                
            except Exception as e:
                print(f"❌ Failed to create indexes: {str(e)}")
                db.session.rollback()
            
            print("\n" + "=" * 60)
            print("🎯 Database Schema Fix Complete!")
            return True
            
    except Exception as e:
        print(f"❌ Critical error during schema fix: {str(e)}")
        return False


def verify_fixes():
    """Verify that all fixes were applied correctly."""
    print("\n🔍 Verifying Database Fixes...")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.extensions import db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            # Verify table rename
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'legal_case'
                )
            """))
            legal_case_exists = result.fetchone()[0]
            
            if legal_case_exists:
                print("✅ legal_case table exists")
            else:
                print("❌ legal_case table missing")
            
            # Verify audit_log improvements
            result = db.session.execute(text("""
                SELECT column_name, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'audit_log' 
                AND column_name IN ('ip_address', 'user_agent')
            """))
            columns = {row[0]: row[1] for row in result.fetchall()}
            
            if columns.get('ip_address', 0) >= 64:
                print("✅ ip_address column size: 64")
            else:
                print(f"❌ ip_address column size: {columns.get('ip_address', 'unknown')}")
            
            if 'user_agent' in columns:
                print("✅ user_agent column exists")
            else:
                print("❌ user_agent column missing")
            
            print("\n" + "=" * 60)
            print("🎯 Database Verification Complete!")
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Judicial Supreme Backend - Database Schema Fix")
    print("=" * 70)
    
    # Apply fixes
    if fix_database_schema():
        # Verify fixes
        verify_fixes()
        print("\n🎉 All database fixes applied successfully!")
        sys.exit(0)
    else:
        print("\n💥 Database schema fix failed. Please check errors above.")
        sys.exit(1)
