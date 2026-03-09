import json

from app.extensions import db
from app.models.user import User


def test_signup_and_login(client, app):
    # signup
    resp = client.post(
        "/auth/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "TestPass123!",
            "role": "citizen",
        },
    )
    assert resp.status_code == 201

    # login
    resp = client.post(
        "/auth/login", json={"email": "test@example.com", "password": "TestPass123!"}
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data


def test_otp_flow(client, app, db):
    # create user; ensure citizen role exists
    from app.models.role import Role
    # Role.query needs an application context
    with app.app_context():
        role = Role.query.filter_by(name="citizen").first()
        if not role:
            role = Role(name="citizen")
            db.session.add(role)
            db.session.commit()
        user = User(name="OTP User", email="otp@example.com", role_id=role.id)
        user.set_password("x")
        db.session.add(user)
        db.session.commit()
        uid = user.id

    # monkeypatch sending to always succeed by importing service and replacing

    # monkeypatch sending to always succeed by importing service and replacing
    import services.otp_email as otp_email
    # also override the reference imported by the auth blueprint
    import app.routes.auth as auth_module

    def fake_send(to_email, code, ttl):
        return True

    otp_email.send_otp_email = fake_send
    auth_module.send_otp_email = fake_send

    # request otp
    resp = client.post("/auth/otp/request", json={"email": "otp@example.com"})
    assert resp.status_code == 200
    # retrieve code from DB
    from app.models.otp import OTP

    with app.app_context():
        otp = OTP.query.filter_by(user_id=uid).order_by(OTP.created_at.desc()).first()
        assert otp is not None

    # verify otp
    resp = client.post(
        "/auth/otp/verify", json={"email": "otp@example.com", "code": otp.code}
    )
    assert resp.status_code == 200
