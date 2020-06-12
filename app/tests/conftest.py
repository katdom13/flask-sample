import pytest
from config import settings
from app.app import create_app
from app.extensions import db as _db
from app.models import Account
from app.lib import encrypt_password


@pytest.yield_fixture(scope="session")
def app():
    """
    Setup the flask test app, this only gets executed once

    :return: Flask app
    """
    app_db_uri = settings.SQLALCHEMY_DATABASE_URI.split(".db")

    test_db_uri = f"{app_db_uri[0]}_test.db"
    params = {
        "DEBUG": False,
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": test_db_uri,
    }

    _app = create_app(settings_override=params)

    # Establish an application context before running the tests
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.yield_fixture(scope="function")
def client(app):
    """
    Setup an app client, this gets executed for each test function

    :param app: Pytest fixture
    :return: Flask app client
    """
    yield app.test_client()


@pytest.fixture(scope="session")
def db(app):
    """
    Setup our database, this only gets executed once per session

    :param app: Pytest fixture
    :return: SQLAlchemy database session
    """
    _db.drop_all()
    _db.create_all()

    # Create a single user because a lot of tests do not mutate this user.
    # It will result in faster tests.
    params = {
        "first_name": "Admin",
        "last_name": "Dummy",
        "username": "admin",
        "password": encrypt_password("password"),
    }

    admin = Account(**params)

    _db.session.add(admin)
    _db.session.commit()

    return _db


@pytest.yield_fixture(scope="function")
def session(db):
    """
    Allow very fast tests by using rollbacks and nested sessions.
    This requires that your database supports SQL savepoints.

    :param db: Pytest fixture
    :return: None
    """
    db.session.begin_nested()

    yield db.session

    db.session.rollback()


@pytest.fixture(scope="function")
def users(db):
    """
    Create user fixtures. They reset per test

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    db.session.query(Account).delete()

    users = [
        {
            "first_name": "Admin",
            "last_name": "Dummy",
            "username": "admin",
            "password": encrypt_password("password"),
        },
        {
            "first_name": "Disabled",
            "last_name": "Dummy",
            "username": "disabled",
            "password": encrypt_password("password"),
            "active": False,
        },
    ]

    for user in users:
        db.session.add(Account(**user))

    db.session.commit()

    return db
