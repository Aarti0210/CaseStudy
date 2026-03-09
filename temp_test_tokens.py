import os
from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.user import User
from flask_jwt_extended import create_access_token

os.environ['FLASK_ENV'] = 'testing'
os.environ['JWT_SECRET_KEY'] = 'x' * 32
app = create_app()
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

with app.app_context():
    db.create_all()
    for name in ['citizen', 'lawyer', 'judge', 'admin']:
        if not Role.query.filter_by(name=name).first():
            db.session.add(Role(name=name))
    db.session.commit()

    citizen = User(name='John Citizen', email='citizen@test.com', role_id=Role.query.filter_by(name='citizen').first().id)
    citizen.set_password('testpass123')
    lawyer = User(name='Jane Lawyer', email='lawyer@test.com', role_id=Role.query.filter_by(name='lawyer').first().id)
    lawyer.set_password('testpass123')
    judge = User(name='Judge Jim', email='judge@test.com', role_id=Role.query.filter_by(name='judge').first().id)
    judge.set_password('testpass123')
    admin = User(name='Admin Alice', email='admin@test.com', role_id=Role.query.filter_by(name='admin').first().id)
    admin.set_password('testpass123')

    db.session.add_all([citizen, lawyer, judge, admin])
    db.session.commit()

    print('IDs', citizen.id, lawyer.id, judge.id, admin.id)
    tokens = {}
    for user, role_name in [(citizen, 'citizen'), (lawyer, 'lawyer'), (judge, 'judge'), (admin, 'admin')]:
        tokens[role_name] = create_access_token(identity={'id': user.id, 'role': role_name})
    print(tokens)
