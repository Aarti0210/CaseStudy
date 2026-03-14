#!/usr/bin/env python3
"""
Create database indexes for optimal performance on production.
Run this script after database migration to ensure proper indexing.
"""

import os
import sys
from sqlalchemy import text

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

def create_database_indexes():
    """Create performance indexes for frequently queried columns."""
    
    indexes = [
        # Case table indexes
        "CREATE INDEX IF NOT EXISTS idx_case_status ON cases (status);",
        "CREATE INDEX IF NOT EXISTS idx_case_created_at ON cases (created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_case_assigned_judge_id ON cases (assigned_judge_id);",
        "CREATE INDEX IF NOT EXISTS idx_case_created_by ON cases (created_by);",
        "CREATE INDEX IF NOT EXISTS idx_case_composite ON cases (status, created_at DESC);",
        
        # Hearing table indexes
        "CREATE INDEX IF NOT EXISTS idx_hearing_date ON hearings (hearing_date);",
        "CREATE INDEX IF NOT EXISTS idx_hearing_case_id ON hearings (case_id);",
        "CREATE INDEX IF NOT EXISTS idx_hearing_judge_id ON hearings (judge_id);",
        "CREATE INDEX IF NOT EXISTS idx_hearing_status ON hearings (status);",
        
        # Notification table indexes
        "CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notifications (user_id);",
        "CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notifications (created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_notification_read ON notifications (read);",
        "CREATE INDEX IF NOT EXISTS idx_notification_user_read ON notifications (user_id, read, created_at DESC);",
        
        # AI Log table indexes
        "CREATE INDEX IF NOT EXISTS idx_ai_log_created_at ON ai_logs (created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_ai_log_user_id ON ai_logs (user_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_log_model ON ai_logs (model);",
        
        # Audit Log table indexes
        "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs (timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs (user_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs (action);",
        "CREATE INDEX IF NOT EXISTS idx_audit_case_id ON audit_logs (case_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_composite ON audit_logs (timestamp DESC, user_id);",
        
        # Document table indexes
        "CREATE INDEX IF NOT EXISTS idx_document_case_id ON documents (case_id);",
        "CREATE INDEX IF NOT EXISTS idx_document_uploaded_by ON documents (uploaded_by);",
        "CREATE INDEX IF NOT EXISTS idx_document_uploaded_at ON documents (uploaded_at DESC);",
        
        # User table indexes
        "CREATE INDEX IF NOT EXISTS idx_user_email ON users (email);",
        "CREATE INDEX IF NOT EXISTS idx_user_role ON users (role);",
        "CREATE INDEX IF NOT EXISTS idx_user_created_at ON users (created_at DESC);",
        
        # Payment table indexes
        "CREATE INDEX IF NOT EXISTS idx_payment_case_id ON payments (case_id);",
        "CREATE INDEX IF NOT EXISTS idx_payment_user_id ON payments (user_id);",
        "CREATE INDEX IF NOT EXISTS idx_payment_status ON payments (status);",
        "CREATE INDEX IF NOT EXISTS idx_payment_created_at ON payments (created_at DESC);",
        
        # Case Activity table indexes
        "CREATE INDEX IF NOT EXISTS idx_case_activity_case_id ON case_activities (case_id);",
        "CREATE INDEX IF NOT EXISTS idx_case_activity_created_at ON case_activities (created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_case_activity_user_id ON case_activities (user_id);",
        
        # Chat Message table indexes
        "CREATE INDEX IF NOT EXISTS idx_chat_message_room_id ON chat_messages (room_id);",
        "CREATE INDEX IF NOT EXISTS idx_chat_message_user_id ON chat_messages (user_id);",
        "CREATE INDEX IF NOT EXISTS idx_chat_message_created_at ON chat_messages (created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_chat_message_room_time ON chat_messages (room_id, created_at DESC);"
    ]
    
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating database indexes for production performance...")
            
            for index_sql in indexes:
                try:
                    db.session.execute(text(index_sql))
                    print(f"✓ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"⚠ Index already exists: {index_sql.split('idx_')[1].split(' ')[0]}")
                    else:
                        print(f"✗ Error creating index: {e}")
            
            db.session.commit()
            
            # Verify indexes were created
            print("\nVerifying created indexes...")
            result = db.session.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname;
            """))
            
            indexes_created = result.fetchall()
            print(f"\n✓ Total indexes in database: {len(indexes_created)}")
            
            # Show indexes for key tables
            key_tables = ['cases', 'hearings', 'notifications', 'ai_logs', 'audit_logs']
            for table in key_tables:
                table_indexes = [idx for idx in indexes_created if idx[1] == table]
                print(f"\n📊 {table.upper()} indexes ({len(table_indexes)}):")
                for idx in table_indexes:
                    print(f"  - {idx[2]}")
            
            print("\n✅ Database indexes created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = create_database_indexes()
    sys.exit(0 if success else 1)
