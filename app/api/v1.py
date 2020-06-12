from flask import Blueprint, request
from flask_login import login_user, logout_user

from app.lib import decrypt_password, encrypt_password, login_required
from app.models import Account

v1 = Blueprint("v1", __name__, url_prefix="/api/v1")


@v1.route("/users", methods=["GET"])
@login_required
def get_users():
    """
    Get json of all user accounts

    :return: dict
    """
    users = Account.query.all()
    user_list = []

    for user in users:
        user_list.append(user.get_dict())

    return {"users": user_list}


@v1.route("/users/<username>", methods=["GET"])
@login_required
def get_user(username):
    """
    Get a single user

    :param username: Unique username
    :return: dict
    """
    user = Account.find(username)

    if not user:
        return {"error": "No user found"}, 404

    return {"user": user.get_dict()}


@v1.route("/users", methods=["POST"])
def create_user():
    """
    Creates and adds a new user

    :return: dict
    """
    data = request.get_json()
    encrypted_password = encrypt_password(data["password"])

    user = Account(
        extl_ref_id=data.get("extl_ref_id"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        username=data.get("username"),
        password=encrypted_password,
    )

    user.save()

    return {"status": "success", "user": user.get_dict()}


@v1.route("/users/<username>", methods=["PUT"])
@login_required
def update_user(username):
    user = Account.find(username)

    if not user:
        return {"error": "No user found"}, 404

    data = request.get_json()

    for key, value in data.items():
        if hasattr(user, key):
            if key == "password":
                setattr(user, key, encrypt_password(value))
            else:
                setattr(user, key, value)

    user.save()

    return {"status": "success", "user": user.get_dict()}


@v1.route("/users/<username>", methods=["DELETE"])
@login_required
def delete_user(username):
    user = Account.find(username)

    if not user:
        return {"error": "No user found"}, 404

    user.delete()

    return {"status": "success", "user": user.get_dict()}


# @v1.route("/login")
# def login():
#     auth = request.authorization

#     if not auth or not auth.username or not auth.password:
#         return make_response(
#             "Could not verify",
#             401,
#             {"WWW-Authenticate": "Basic realm='Login required'"},
#         )

#     user = Account.find(auth.username)

#     if not user:
#         return {"error": "No user found"}, 404

#     if decrypt_password(auth.password, user.password):
#         if user.is_active():
#             login_user(user, remember=True)
#             return {"status": "success"}
#         else:
#             {"error": "Account is inactive"}, 401
#     else:
#         return {"error": "Invalid credentials provided"}, 401


@v1.route("/login", methods=["POST"])
def login():
    auth = request.get_json()

    if not auth or not auth.get("identity") or not auth.get("password"):
        return {"error": "Could not verify"}, 401

    user = Account.find(auth.get("identity"))

    if not user:
        return {"error": "No user found"}, 404

    if decrypt_password(auth.get("password"), user.password):
        if user.is_active():
            login_user(user, remember=True)
            return {"status": "success"}
        else:
            return {"error": "Account is inactive"}, 401
    else:
        return {"error": "Invalid credentials provided"}, 401


@v1.route("/logout")
@login_required
def logout():
    logout_user()
    return {"status": "success"}
