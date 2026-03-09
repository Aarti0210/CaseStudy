#!/usr/bin/env python
"""Create test users for ML endpoint validation."""
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.role import Role

def seed_users():
    app = create_app()
    with app.app_context():
        # Ensure roles exist
        admin_role = Role.query.filter_by(name="admin").first()
        lawyer_role = Role.query.filter_by(name="lawyer").first()
        judge_role = Role.query.filter_by(name="judge").first()
        citizen_role = Role.query.filter_by(name="citizen").first()
        
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator")
            db.session.add(admin_role)
        if not lawyer_role:
            lawyer_role = Role(name="lawyer", description="Lawyer")
            db.session.add(lawyer_role)
        if not judge_role:
            judge_role = Role(name="judge", description="Judge")
            db.session.add(judge_role)
        if not citizen_role:
            citizen_role = Role(name="citizen", description="Citizen")
            db.session.add(citizen_role)
        
        db.session.commit()
        
        # Create test users
        users_to_create = [
            {"email": "admin@example.com", "name": "Admin User", "password": "admin123", "role": admin_role},
            {"email": "judge@example.com", "name": "Judge User", "password": "judge123", "role": judge_role},
            {"email": "lawyer@example.com", "name": "Lawyer User", "password": "lawyer123", "role": lawyer_role},
            {"email": "citizen@example.com", "name": "Citizen User", "password": "citizen123", "role": citizen_role},
        ]
        
        for user_data in users_to_create:
            existing = User.query.filter_by(email=user_data["email"]).first()
            if not existing:
                user = User(
                    email=user_data["email"],
                    name=user_data["name"],
                    role_id=user_data["role"].id
                )
                user.set_password(user_data["password"])
                db.session.add(user)
                print(f"✓ Created user: {user_data['email']}")
            else:
                print(f"- User already exists: {user_data['email']}")
        
        db.session.commit()
        print("\n✓ User seeding complete")

if __name__ == "__main__":
    try:
        seed_users()
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
