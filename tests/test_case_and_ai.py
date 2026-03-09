import json

from app.extensions import db
from app.models.user import User


def get_token(client, email, password="pw"):
    r = client.post("/auth/login", json={"email": email, "password": password})
    return r.get_json().get("access_token")


def test_case_creation_and_aiprivileged(client, app, db):
    # ensure the lawyer role exists and use its id
    from app.models.role import Role
    # ensure we are inside app context when querying
    with app.app_context():
        lawyer_role = Role.query.filter_by(name="lawyer").first()
        if not lawyer_role:
            lawyer_role = Role(name="lawyer")
            db.session.add(lawyer_role)
            db.session.commit()
        lawyer_role_id = lawyer_role.id

    # create a lawyer user and record id & role while in context
    with app.app_context():
        u = User(name="Lawyer", email="lawyer@example.com", role_id=lawyer_role_id)
        u.set_password("pw")
        db.session.add(u)
        db.session.commit()
        user_id = u.id
        user_role = u.role_obj.name if u.role_obj else None

    # login through API to obtain a valid token
    resp_login = client.post(
        "/auth/login",
        json={"email": "lawyer@example.com", "password": "pw"},
    )
    assert resp_login.status_code == 200
    token = resp_login.get_json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # create case
    resp = client.post("/case/create", json={"title": "Test Case"}, headers=headers)
    assert resp.status_code == 201

    # Mock AI services to avoid external calls
    import app.ai.services as ai_services

    ai_services.draft_notice = lambda client_name, case_type, facts, user_id, role: {
        "ok": True,
        "result": "notice",
    }

    # lawyer can call draft-notice
    resp = client.post(
        "/ai/draft-notice",
        json={"client_name": "C", "case_type": "T", "facts": "F"},
        headers=headers,
    )
    assert resp.status_code == 200

    # caching should prevent a second ML prediction call
    from app.ml import predictor as ml_predictor
    
    # Save original predict method to restore later
    original_predict = ml_predictor.predict
    original_model = ml_predictor.model
    
    try:
        calls = {"n": 0}
        # ensure the module appears ready with a dummy model
        ml_predictor.model = object()
        def fake_predict(case_data):
            calls["n"] += 1
            return {"result": "x"}
        ml_predictor.predict = fake_predict

        # first hit should exercise the predictor with valid payload
        valid_case = {
            "case_type": "type",
            "number_of_hearings": 0,
            "judge_workload": 0,
            "document_count": 0,
            "case_priority": "low",
            "filing_to_first_hearing_days": 0,
            "court_level": "level",
            "previous_adjournments": 0,
        }
        resp1 = client.post(
            "/ai/predict-delay",
            json={"case_data": valid_case},
            headers=headers,
        )
        assert resp1.status_code == 200
        # second hit with identical payload should be cached
        resp2 = client.post(
            "/ai/predict-delay",
            json={"case_data": valid_case},
            headers=headers,
        )
        assert resp2.status_code == 200
        assert calls["n"] == 1

        # test new endpoints exist
        resp = client.post(
            "/ai/predict-delay",
            json={"case_data": valid_case},
            headers=headers,
        )
        assert resp.status_code == 200

        resp = client.post(
            "/ai/judicial-intelligence",
            json={"case_data": "some data"},
            headers=headers,
        )
        assert resp.status_code == 200
    finally:
        # Restore original predict method to prevent test isolation issues
        ml_predictor.predict = original_predict
        ml_predictor.model = original_model

    # citizen cannot call lawyer-only endpoint (ensure citizen role exists)
    from app.models.role import Role
    with app.app_context():
        citizen_role = Role.query.filter_by(name="citizen").first()
        if not citizen_role:
            citizen_role = Role(name="citizen")
            db.session.add(citizen_role)
            db.session.commit()
        citizen_role_id = citizen_role.id

    with app.app_context():
        c = User(name="Citizen", email="citizen@example.com", role_id=citizen_role_id)
        c.set_password("pw")
        db.session.add(c)
        db.session.commit()
    # login citizen to get token
    resp_c_login = client.post(
        "/auth/login",
        json={"email": "citizen@example.com", "password": "pw"},
    )
    assert resp_c_login.status_code == 200
    ct = resp_c_login.get_json().get("access_token")
    resp = client.post(
        "/ai/draft-notice",
        json={"client_name": "C", "case_type": "T", "facts": "F"},
        headers={"Authorization": f"Bearer {ct}"},
    )
    assert resp.status_code == 403


def test_file_upload_validation(client, app, db):
    # create user and token (ensure citizen role exists)
    from app.models.role import Role
    with app.app_context():
        citizen_role = Role.query.filter_by(name="citizen").first()
        if not citizen_role:
            citizen_role = Role(name="citizen")
            db.session.add(citizen_role)
            db.session.commit()
        citizen_role_id = citizen_role.id

    with app.app_context():
        u = User(name="Uploader", email="up@example.com", role_id=citizen_role_id)
        u.set_password("pw")
        db.session.add(u)
        db.session.commit()
    # login uploader
    resp_upload_login = client.post(
        "/auth/login",
        json={"email": "up@example.com", "password": "pw"},
    )
    assert resp_upload_login.status_code == 200
    token = resp_upload_login.get_json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # invalid extension
    data = {"file": (bytes("d", "utf-8"), "bad.exe")}
    resp = client.post(
        "/document/upload",
        data=data,
        content_type="multipart/form-data",
        headers=headers,
    )
    assert resp.status_code == 400
