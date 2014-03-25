from os import environ, path

# App details
BASE_DIRECTORY = path.abspath(path.dirname(__file__))
CSRF_ENABLED = True
DEBUG = environ.get('DEBUG')
SECRET_KEY = environ.get('SECRET_KEY')

# Facebook details
FACEBOOK_APP_ID = environ.get('FACEBOOK_APP_ID')
FACEBOOK_APP_NAME = environ.get('FACEBOOK_APP_NAME')
FACEBOOK_APP_SECRET = environ.get('FACEBOOK_APP_SECRET')

# Token details
LONG_TERM_TOKEN = 1
SHORT_TERM_TOKEN = 0

# Role details
ROLE_ADMIN = 1
ROLE_USER = 0

# API details
API_VERSION = 'v0.3'
API_PASSWORD = environ.get('API_PASSWORD')
API_USERNAME = environ.get('API_USERNAME')

# Database details
if environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(BASE_DIRECTORY, 'app.db') + '?check_same_thread=False'
else:
    SQLALCHEMY_DATABASE_URI = environ.get['DATABASE_URL']
