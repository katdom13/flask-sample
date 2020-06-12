from flask import Flask

from app.models import Account
from app.extensions import db, login_manager, ma
from app.api import v1


def create_app(settings_override=None):
    """
    Create a flask app using the app factory pattern.

    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.settings")
    app.config.from_pyfile("settings.py", silent=True)

    if settings_override:
        app.config.update(settings_override)

    app.register_blueprint(v1)

    extensions(app)
    authentication(app, Account)

    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates app).

    :param app: Application instance
    :return: None
    """
    db.init_app(app)
    login_manager.init_app(app)
    ma.init_app(app)


def authentication(app, model):
    """
    Initialize the Flask-Login extenstion (mutates app).

    :param app: Application instance
    :param model: Model that contains the authentication information
    :return: None
    """

    @login_manager.user_loader
    def load_user(username):
        return model.find(username)
