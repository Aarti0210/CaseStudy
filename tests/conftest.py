import os

import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    # configure test app with explicit testing config class to avoid
    # production database being used during initialization
    os.environ["FLASK_ENV"] = "testing"

    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        RATELIMIT_ENABLED = False
        JWT_ACCESS_TOKEN_EXPIRES = 3600
        JWT_SECRET_KEY = "x" * 32
        SECRET_KEY = "x" * 32

    app = create_app(config_object=TestConfig)

    with app.app_context():
        _db.create_all()
    yield app
    # teardown
    with app.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db
