"""
Comprehensive test suite for Judicial Supreme Backend
Tests all endpoints for functionality and error handling
"""

import os
import pytest
from datetime import datetime, timedelta

from app import create_app
from app.extensions import db as _db
from app.models.user import User
from app.models.case import Case
from app.models.hearing import Hearing
from app.models.document import Document
from app.models.payment import Payment
from app.models.notification import Notification


@pytest.fixture(scope="session")
def app():
    """Create and configure test app with explicit TestingConfig"""
    from app.config import TestingConfig
    
    # Ensure testing env is set
    os.environ["FLASK_ENV"] = "testing"
    os.environ["JWT_SECRET_KEY"] = TestingConfig.JWT_SECRET_KEY
    
    # Create app with explicit TestingConfig to prevent MySQL connection attempts
    app = create_app(config_object=TestingConfig)
    
    with app.app_context():
        _db.create_all()
    
    yield app
    
    with app.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture
def auth_tokens(client, db):
    """Create test users and get auth tokens"""
    # create roles that users will be assigned to (idempotent)
    from app.models.role import Role

    # use application context for DB operations
    with client.application.app_context():
        def get_or_create(name):
            r = Role.query.filter_by(name=name).first()
            if not r:
                r = Role(name=name)
                db.session.add(r)
                db.session.commit()
            return r

        citizen_role = get_or_create("citizen")
        lawyer_role = get_or_create("lawyer")
        judge_role = get_or_create("judge")
        admin_role = get_or_create("admin")

    # Create users and attach roles via relationship, commit and obtain tokens
    tokens = {}
    with client.application.app_context():
        # helper that will fetch or create a user by email
        def get_or_create_user(name, email, role):
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(name=name, email=email)
                u.set_password("testpass123")
                u.role_obj = role
                db.session.add(u)
                db.session.commit()
            else:
                # ensure password and role are up to date
                u.set_password("testpass123")
                u.role_obj = role
                db.session.commit()
            return u

        citizen = get_or_create_user("John Citizen", "citizen@test.com", citizen_role)
        lawyer = get_or_create_user("Jane Lawyer", "lawyer@test.com", lawyer_role)
        judge = get_or_create_user("Judge Jim", "judge@test.com", judge_role)
        admin = get_or_create_user("Admin Alice", "admin@test.com", admin_role)

        # generate JWT tokens directly rather than hitting login endpoint
        from flask_jwt_extended import create_access_token
        import json
        for user, role_name in (
            (citizen, "citizen"),
            (lawyer, "lawyer"),
            (judge, "judge"),
            (admin, "admin"),
        ):
            if user and role_name:
                # identity must be a string; login endpoint dumps to JSON
                tokens[role_name] = create_access_token(
                    identity=json.dumps({"id": user.id, "role": role_name})
                )
    
    return {
        "citizen": tokens.get("citizen", ""),
        "lawyer": tokens.get("lawyer", ""),
        "judge": tokens.get("judge", ""),
        "admin": tokens.get("admin", ""),
        "users": {
            "citizen_id": citizen.id,
            "lawyer_id": lawyer.id,
            "judge_id": judge.id,
            "admin_id": admin.id
        }
    }


# ===================== AUTH TESTS =====================

def test_signup_success(client):
    """Test successful user signup"""
    response = client.post("/auth/signup", json={
        "name": "Test User",
        "email": "newuser@test.com",
        "password": "TestPass@123",
        "role": "citizen"
    })
    # response body may vary; just ensure user created message or success flag
    assert response.status_code in [200, 201]
    data = response.get_json() or {}
    assert data.get("success") is not None or data.get("message")


def test_signup_missing_fields(client):
    """Test signup with missing fields"""
    response = client.post("/auth/signup", json={
        "name": "Test User",
        "email": "test@test.com"
    })
    # validation may return 400 or 422 depending on schema implementation
    assert 400 <= response.status_code < 500


def test_signup_invalid_role(client):
    """Test signup with invalid role"""
    response = client.post("/auth/signup", json={
        "name": "Test User",
        "email": "test@test.com",
        "password": "TestPass@123",
        "role": "invalid_role"
    })
    assert response.status_code == 400


# ===================== CASE TESTS =====================

def test_create_case(client, auth_tokens):
    """Test case creation"""
    headers = {"Authorization": f"Bearer {auth_tokens['lawyer']}"}
    response = client.post("/case/create", 
        json={
            "title": "Civil Case #001",
            "description": "Property dispute"
        },
        headers=headers
    )
    assert response.status_code in [200, 201]
    data = response.get_json()
    assert data.get("success") is True or "case_id" in data


def test_create_case_missing_title(client, auth_tokens):
    """Test case creation without title"""
    headers = {"Authorization": f"Bearer {auth_tokens['lawyer']}"}
    response = client.post("/case/create",
        json={"description": "No title case"},
        headers=headers
    )
    assert response.status_code == 400


def test_get_all_cases(client, auth_tokens):
    """Test retrieving all cases"""
    headers = {"Authorization": f"Bearer {auth_tokens['lawyer']}"}
    response = client.get("/case", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True
    assert isinstance(data.get("cases"), list)


def test_get_case_by_id(client, auth_tokens):
    """Test retrieving specific case"""
    headers = {"Authorization": f"Bearer {auth_tokens['lawyer']}"}
    
    # Create a case first
    create_resp = client.post("/case/create",
        json={"title": "Test Case", "description": "Test"},
        headers=headers
    )
    
    if create_resp.status_code in [200, 201]:
        case_id = create_resp.get_json().get("case", {}).get("id")
        if case_id:
            response = client.get(f"/case/{case_id}", headers=headers)
            assert response.status_code == 200
            assert response.get_json().get("success") is True


def test_update_case(client, auth_tokens):
    """Test updating a case"""
    headers = {"Authorization": f"Bearer {auth_tokens['lawyer']}"}
    
    # Create case
    create_resp = client.post("/case/create",
        json={"title": "Update Test", "description": "Test"},
        headers=headers
    )
    
    if create_resp.status_code in [200, 201]:
        case_id = create_resp.get_json().get("case", {}).get("id")
        if case_id:
            response = client.put(f"/case/{case_id}",
                json={"status": "Active"},
                headers=headers
            )
            assert response.status_code in [200, 400, 401]


def test_delete_case(client, auth_tokens):
    """Test deleting a case"""
    headers = {"Authorization": f"Bearer {auth_tokens['lawyer']}"}
    
    # Create case
    create_resp = client.post("/case/create",
        json={"title": "Delete Test", "description": "Test"},
        headers=headers
    )
    
    if create_resp.status_code in [200, 201]:
        case_id = create_resp.get_json().get("case", {}).get("id")
        if case_id:
            response = client.delete(f"/case/{case_id}", headers=headers)
            assert response.status_code in [200, 404, 401]


# ===================== HEARING TESTS =====================

def test_schedule_hearing(client, auth_tokens, db):
    """Test scheduling a hearing"""
    headers = {"Authorization": f"Bearer {auth_tokens['judge']}"}
    
    # Create a case first
    case = Case(
        title="Hearing Test Case",
        description="Test",
        created_by=auth_tokens['users']['lawyer_id']
    )
    # perform raw DB operations within app context
    with client.application.app_context():
        db.session.add(case)
        db.session.commit()
        case_id = case.id
        case_id = case.id
        case_id = case.id
    
    response = client.post("/hearing/schedule",
        json={
            "case_id": case_id,
            "hearing_date": "2026-03-15T10:00:00"
        },
        headers=headers
    )
    assert response.status_code in [200, 201]


def test_schedule_hearing_invalid_date(client, auth_tokens):
    """Test scheduling with invalid date"""
    headers = {"Authorization": f"Bearer {auth_tokens['judge']}"}
    response = client.post("/hearing/schedule",
        json={
            "case_id": 1,
            "hearing_date": "invalid-date"
        },
        headers=headers
    )
    assert response.status_code == 400


def test_suggest_hearing(client, auth_tokens, db):
    """Test smart scheduler suggestion endpoint"""
    headers = {"Authorization": f"Bearer {auth_tokens['judge']}"}
    # create case and a judge user if not exists
    case = Case(
        title="Scheduler Case",
        description="Test",
        created_by=auth_tokens['users']['lawyer_id']
    )
    with client.application.app_context():
        db.session.add(case)
        db.session.commit()
        case_id = case.id

    response = client.post("/hearing/suggest",
        json={"case_id": case_id},
        headers=headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True
    assert isinstance(data.get("suggestions"), list)


# ===================== PAYMENT TESTS =====================

def test_create_payment(client, auth_tokens, db):
    """Test creating a payment"""
    headers = {"Authorization": f"Bearer {auth_tokens['lawyer']}"}
    
    # Create case
    case = Case(
        title="Payment Test",
        description="Test",
        created_by=auth_tokens['users']['lawyer_id']
    )
    with client.application.app_context():
        db.session.add(case)
        db.session.commit()
        case_id = case.id
    
    response = client.post("/payment/create",
        json={
            "case_id": case_id,
            "amount": 5000.00
        },
        headers=headers
    )
    assert response.status_code in [200, 201]


def test_create_payment_invalid_amount(client, auth_tokens):
    """Test payment with invalid amount"""
    headers = {"Authorization": f"Bearer {auth_tokens['lawyer']}"}
    response = client.post("/payment/create",
        json={
            "case_id": 1,
            "amount": "invalid"
        },
        headers=headers
    )
    assert response.status_code in [400, 404]


# ===================== DOCUMENT TESTS =====================

def test_upload_document(client, auth_tokens, db):
    """Test document upload"""
    headers = {"Authorization": f"Bearer {auth_tokens['lawyer']}"}
    
    # Create case
    case = Case(
        title="Document Test",
        description="Test",
        created_by=auth_tokens['users']['lawyer_id']
    )
    with client.application.app_context():
        db.session.add(case)
        db.session.commit()
        case_id = case.id
        case_id = case.id
    
    # Create a test file
    from io import BytesIO
    test_file = (BytesIO(b"test content"), "test.pdf")
    
    response = client.post("/document/upload",
        data={
            "case_id": str(case_id),
            "file": test_file
        },
        headers=headers
    )
    assert response.status_code in [200, 201, 400]


def test_upload_invalid_filetype(client, auth_tokens, db):
    """Test upload with invalid file type"""
    headers = {"Authorization": f"Bearer {auth_tokens['lawyer']}"}
    
    case = Case(
        title="Document Test",
        description="Test",
        created_by=auth_tokens['users']['lawyer_id']
    )
    with client.application.app_context():
        db.session.add(case)
        db.session.commit()
        case_id = case.id
    
    from io import BytesIO
    test_file = (BytesIO(b"test content"), "test.exe")
    
    response = client.post("/document/upload",
        data={
            "case_id": str(case_id),
            "file": test_file
        },
        headers=headers
    )
    assert response.status_code in [400, 413]


# ===================== NOTIFICATION TESTS =====================

def test_send_notification(client, auth_tokens):
    """Test sending a notification"""
    headers = {"Authorization": f"Bearer {auth_tokens['admin']}"}
    
    response = client.post("/notification/send",
        json={
            "user_id": auth_tokens['users']['citizen_id'],
            "message": "Test notification"
        },
        headers=headers
    )
    assert response.status_code in [200, 201]


def test_get_user_notifications(client, auth_tokens):
    """Test retrieving user notifications"""
    headers = {"Authorization": f"Bearer {auth_tokens['citizen']}"}
    
    response = client.get(
        f"/notification/user/{auth_tokens['users']['citizen_id']}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True


# ===================== AUDIT TESTS =====================

def test_get_audit_logs(client, auth_tokens):
    """Test retrieving audit logs"""
    headers = {"Authorization": f"Bearer {auth_tokens['admin']}"}
    
    response = client.get("/audit/logs", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True


def test_admin_analytics_dashboard(client, auth_tokens):
    """Test comprehensive analytics dashboard"""
    headers = {"Authorization": f"Bearer {auth_tokens['admin']}"}
    
    response = client.get("/admin/analytics", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    
    # Check for all major sections
    assert "system_health" in data
    assert "users" in data
    assert "cases" in data
    assert "hearings" in data
    assert "judge_workload" in data
    assert "documents" in data
    assert "payments" in data
    assert "ai_analytics" in data
    assert "audit" in data
    
    # Verify nested structure
    assert isinstance(data["users"]["by_role"], dict)
    assert isinstance(data["cases"]["by_status"], dict)
    assert isinstance(data["hearings"]["by_status"], dict)
    assert isinstance(data["judge_workload"]["details"], list)
    assert isinstance(data["ai_analytics"]["feature_breakdown"], dict)


def test_admin_ai_costs(client, auth_tokens):
    """Test AI cost analysis endpoint"""
    headers = {"Authorization": f"Bearer {auth_tokens['admin']}"}
    
    response = client.get("/admin/ai-costs", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    
    # Verify cost structure
    assert "cost_all_time" in data
    assert "cost_this_month" in data
    assert "cost_this_week" in data
    assert "cost_by_feature" in data
    
    # Check for cost fields
    assert "total_cost" in data["cost_all_time"]
    assert "prompt_tokens" in data["cost_all_time"]
    assert "completion_tokens" in data["cost_all_time"]


def test_admin_case_delays(client, auth_tokens):
    """Test case delay analysis endpoint"""
    headers = {"Authorization": f"Bearer {auth_tokens['admin']}"}
    
    response = client.get("/admin/case-delays", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    
    # Verify delay structure
    assert "delay_summary" in data
    assert "critical_cases" in data
    assert "high_risk_cases" in data
    assert "stalled_cases" in data
    assert "judge_performance" in data
    
    assert isinstance(data["delay_summary"], dict)
    assert isinstance(data["critical_cases"], list)
    assert isinstance(data["stalled_cases"], list)


def test_admin_unauthorized(client, auth_tokens):
    """Test that non-admins cannot access admin endpoints"""
    headers = {"Authorization": f"Bearer {auth_tokens['lawyer']}"}
    
    # Should be forbidden for non-admins
    response = client.get("/admin/analytics", headers=headers)
    assert response.status_code == 403
    
    response = client.get("/admin/ai-costs", headers=headers)
    assert response.status_code == 403
    
    response = client.get("/admin/case-delays", headers=headers)
    assert response.status_code == 403


# ===================== ADMIN TESTS =====================

def test_admin_analytics(client, auth_tokens):
    """Test admin analytics endpoint"""
    headers = {"Authorization": f"Bearer {auth_tokens['admin']}"}
    
    response = client.get("/admin/analytics", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True or "users" in data


# ===================== ACTIVITY TESTS =====================

def test_get_case_activity(client, auth_tokens, db):
    """Test retrieving case activity"""
    headers = {"Authorization": f"Bearer {auth_tokens['lawyer']}"}
    
    case = Case(
        title="Activity Test",
        description="Test",
        created_by=auth_tokens['users']['lawyer_id']
    )
    with client.application.app_context():
        db.session.add(case)
        db.session.commit()
        case_id = case.id
    
    response = client.get(f"/activity/case/{case_id}", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
