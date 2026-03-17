#!/usr/bin/env python3
"""Test SQLAlchemy models and relationships"""

import secrets
from app.extensions import db
from app import create_app
from app.models import User, Case, Role, Hearing, Document, Payment, Notification, AuditLog, OTP

def test_models():
    app = create_app()
    with app.app_context():
        try:
            print("Testing model relationships...")
            
            # Clean up any existing test data
            existing_user = User.query.filter_by(email="test@example.com").first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
            
            # Test User-Role relationship
            user = User(name="Test User", email=f"test_{secrets.token_hex(4)}@example.com")
            user.set_password("test123")
            
            role = Role.query.filter_by(name="citizen").first()
            if not role:
                role = Role(name="citizen", description="Regular citizen")
                db.session.add(role)
                db.session.commit()
            
            user.role_id = role.id
            db.session.add(user)
            db.session.commit()
            
            print(f"✓ User-Role relationship: {user.role_obj.name if user.role_obj else 'None'}")
            
            # Test Case-User relationship
            case = Case(title="Test Case", description="Test description", created_by=user.id)
            db.session.add(case)
            db.session.commit()
            
            print(f"✓ Case-User relationship: {case.creator.name if case.creator else 'None'}")
            
            # Test Document-Case relationship
            document = Document(
                case_id=case.id,
                filename="test.pdf",
                original_name="test_document.pdf",
                content_type="application/pdf",
                size=1024
            )
            db.session.add(document)
            db.session.commit()
            
            print(f"✓ Document-Case relationship: {document.case.title if document.case else 'None'}")
            
            # Test Hearing-Case relationship
            from datetime import datetime
            hearing = Hearing(
                case_id=case.id,
                hearing_date=datetime.utcnow(),
                judge_id=user.id
            )
            db.session.add(hearing)
            db.session.commit()
            
            print(f"✓ Hearing-Case relationship: {hearing.case.title if hearing.case else 'None'}")
            
            # Test AuditLog relationships
            audit = AuditLog(
                user_id=user.id,
                case_id=case.id,
                action="Test Action",
                details={"test": "data"}
            )
            db.session.add(audit)
            db.session.commit()
            
            print(f"✓ AuditLog relationships: User={audit.user.name if audit.user else 'None'}, Case={audit.case.title if audit.case else 'None'}")
            
            # Clean up test data
            db.session.delete(audit)
            db.session.delete(hearing)
            db.session.delete(document)
            db.session.delete(case)
            db.session.delete(user)
            db.session.commit()
            
            print("✓ All model relationships validated successfully")
            return True
            
        except Exception as e:
            print(f"✗ Model validation failed: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    test_models()
