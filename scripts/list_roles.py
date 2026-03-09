from app import create_app
from app.models.role import Role

app = create_app()
with app.app_context():
    roles = Role.query.all()
    if not roles:
        print('No roles found')
    else:
        print('Roles:')
        for r in roles:
            print(f' - {r.name}: {r.description}')
