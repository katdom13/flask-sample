from datetime import datetime
from functools import wraps

import pytest
from flask import url_for
from flask_login import current_user
from werkzeug import security

from app.extensions import db


class ResourceMixin(object):
    """
    Common fields and methods for the data models
    """

    create_date = db.Column(db.DateTime, default=datetime.now())
    update_date = db.Column(db.DateTime, default=datetime.now())

    def save(self):
        """
        Saves an instance object to the database

        :return: None
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Deletes an object from the database
        """
        db.session.delete(self)
        db.session.commit()


def encrypt_password(raw_password):
    """
    Encrypts a raw password

    :param raw_password: Raw text to be encrypted
    :return: Encrypted/hashed password
    """
    return security.generate_password_hash(
        raw_password, method="pbkdf2:sha256", salt_length=8
    )


def decrypt_password(input_password, encrypted_password):
    """
    Decrypts an encrypted password

    :param input_password: Password to be checked
    :param encrypted_password: Password to be checked against
    :return: bool
    """
    return security.check_password_hash(encrypted_password, input_password)


def login_required(func):
    """
    Imitates flask-login's login_required but for APIs

    :param func: The view function to decorate.
    :type func: function
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return {"error": "You are unauthorized to do that"}, 401
        else:
            return func(*args, **kwargs)

    return decorated_view


class TestMixin(object):
    """
    Automatically load in a session and a client.
    This is common for a lot of tests
    """

    @pytest.fixture(autouse=True)
    def set_common_fixtures(self, session, client):
        self.session = session
        self.client = client

    def login(self, identity="admin", password="password"):
        """
        Logs a specific user in

        :param identity: A unique username
        :param password: User password

        :return: Flask response
        """
        user = dict(identity=identity, password=password)
        response = self.client.post(url_for("v1.login"), json=user)
        return response

    def logout(self):
        """
        Logs the current user out

        :return: Flask response
        """
        return self.client.get(url_for("v1.logout"))
