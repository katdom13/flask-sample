import uuid

from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer

from app.extensions import db, ma
from app.lib import ResourceMixin


class Account(db.Model, UserMixin, ResourceMixin):
    """
    Represents a user account
    """

    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(32), nullable=False, default=uuid.uuid4().hex)
    extl_ref_id = db.Column(db.String(32), nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(1024), nullable=False)
    active = db.Column("is_active", db.Boolean(), nullable=False, server_default="1")

    @classmethod
    def find(cls, identity):
        """
        Find a user account based on username or public id

        :param identity: Username or email
        :return: Account instance
        """
        return Account.query.filter(
            (cls.username == identity) | (cls.public_id == identity)
        ).first()

    @classmethod
    def deserialize_token(cls, token):
        """
        Obtain a user from de-serializing a signed token.

        :param token: Signed token
        :type token: str
        :return: User instance or None
        """
        private_key = TimedJSONWebSignatureSerializer(current_app.config["SECRET_KEY"])

        try:
            decoded_payload = private_key.loads(token)
            return Account.find(decoded_payload.get("username"))
        except Exception:
            return None

    def is_active(self):
        """
        Return whether or not the user account is active, this satisfies
        Flask-Login by overwriting the default value.

        :return: bool
        """
        return self.active

    def get_id(self):
        """
        Override from UserMixin
        """
        return self.username

    def serialize_token(self, expiration=3600):
        """
        Sign and create a token that can be used for things such as resetting a password
        or othe tasks that involve a one-off token.

        :param expiration: Seconds until the token expires, defaults to 1 hour
        :type expiration: int
        :return: str
        """
        private_key = current_app.config["SECRET_KEY"]
        serializer = TimedJSONWebSignatureSerializer(private_key, expiration)
        return serializer.dumps({"username": self.username}).decode("utf-8")

    def get_dict(self):
        """
        Returns a dictionary containing an object's fields

        :return: dict
        """
        schema = AccountSchema()
        return schema.dump(self)


class AccountSchema(ma.ModelSchema):
    """
    Deserializes a Model
    """

    class Meta:
        model = Account
