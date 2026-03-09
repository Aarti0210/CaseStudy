#!/usr/bin/env python
"""Seed default roles into the database."""

from app import create_app
from app.extensions import db
from app.models.role import Role

app = create_app()

with app.app_context():
    # Check if roles exist
    existing_roles = {r.name for r in Role.query.all()}
    roles_to_add = [
        {"name": "admin", "description": "System administrator with full access"},
        {"name": "judge", "description": "Judge who can review cases and issue orders"},
        {"name": "lawyer", "description": "Lawyer representing clients in court"},
        {"name": "citizen", "description": "Regular citizen or public user"},
    ]

    for role_data in roles_to_add:
        if role_data["name"] not in existing_roles:
            role = Role(**role_data)
            db.session.add(role)
            print(f"Added role: {role_data['name']}")
        else:
            print(f"Role '{role_data['name']}' already exists, skipping")

    db.session.commit()
    print("✓ Roles seeded successfully")

    # Display all roles
    all_roles = Role.query.all()
    print(f"\nAll roles in database ({len(all_roles)}):")
    for role in all_roles:
        print(f"  - {role.name}: {role.description}")
