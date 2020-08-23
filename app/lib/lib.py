import json
from datetime import datetime
from functools import wraps

import pytest
from flask import request, url_for
from flask_login import login_user
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
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return {"error": "You are unauthorized to do that"}, 401

        from app.models import Account

        user = Account.deserialize_token(token)

        if not user:
            return {"error": "You are unauthorized to do that"}, 401

        login_user(user, remember=True)
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
        token = json.loads(response.get_data(as_text=True))['token']
        return response, token

    def logout(self, token=None):
        """
        Logs the current user out

        :return: Flask response
        """
        return self.client.get(url_for("v1.logout"), headers={'x-access-token': token})
