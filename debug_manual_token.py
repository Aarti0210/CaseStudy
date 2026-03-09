from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.user import User
import jwt

class DebugConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    RATELIMIT_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    JWT_SECRET_KEY = 'test-secret'
    SECRET_KEY = 'test-secret'

app = create_app(config_object=DebugConfig)

with app.app_context():
    db.create_all()
    lawyer_role = Role(name='lawyer')
    db.session.add(lawyer_role)
    db.session.commit()
    u = User(name='Lawyer', email='lawyer@example.com', role_id=lawyer_role.id)
    u.set_password('pw')
    db.session.add(u)
    db.session.commit()
    from flask_jwt_extended import create_access_token
    user_role = u.role_obj.name if u.role_obj else None
    token = create_access_token(identity={'id':u.id, 'role':user_role})
    print('manual token', token)
    print('decode result:')
    try:
        print(jwt.decode(token,'test-secret',algorithms=['HS256']))
    except Exception as e:
        print('decode error', e)
