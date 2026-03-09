from sqlalchemy import inspect

from app import create_app
from app.extensions import bcrypt, db
from app.models.user import User

app = create_app()

ADMIN_EMAIL = "admin@judicial.local"
ADMIN_PASSWORD = "AdminPass123!"

with app.app_context():
    # import all models to ensure SQLAlchemy mappers are registered
    import app.models.ai_log
    import app.models.audit
    import app.models.case
    import app.models.case_activity
    import app.models.document
    import app.models.hearing
    import app.models.notification
    import app.models.otp
    import app.models.payment
    import app.models.user

    insp = inspect(db.engine)
    if "roles" in insp.get_table_names():
        # ensure basic roles exist
        try:
            db.session.execute(
                "INSERT IGNORE INTO roles (role_name) VALUES ('admin'), ('judge'), ('lawyer'), ('citizen')"
            )
            db.session.commit()
        except Exception:
            db.session.rollback()
    # create admin user if not exists
    existing = User.query.filter_by(email=ADMIN_EMAIL).first()
    if existing:
        print("Admin user already exists:", existing.email)
    else:
        pw_hash = bcrypt.generate_password_hash(ADMIN_PASSWORD).decode("utf-8")
        admin = User(
            name="System Admin",
            email=ADMIN_EMAIL,
            password=pw_hash,
            role="admin",
            is_active=True,
        )
        db.session.add(admin)
        db.session.commit()
        print("Created admin user:", ADMIN_EMAIL)
