from datetime import timedelta

# App variables
SECRET_KEY = "23d5485f2400ab342cef5516bc4c6400cd8639f0597b6df4"
DEBUG = True
SERVER_NAME = "localhost"
REMEMBER_COOKIE_DURATION = timedelta(days=3)

#  CORS
CORS_HEADERS = "Content-Type"

# Database variables
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "sqlite:///../app.db"
