import os

# App details
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
CSRF_ENABLED = True
SECRET_KEY = '!th1553cr3tk3yha5thaty0l0swag!'

# Facebook details
FACEBOOK_APP_ID = '498777246878058'
FACEBOOK_APP_NAME = 'The FAD Study'
FACEBOOK_APP_SECRET = '02272a1ef565d2bbbec38c64e464094f'

# Token details
LONG_TERM_TOKEN = 1
SHORT_TERM_TOKEN = 0

# Role details
ROLE_ADMIN = 1
ROLE_USER = 0

# API details
API_VERSION = 'v0.3'
API_PASSWORD = 'letmeinbrah'
API_USERNAME = 'apiuser'

# Database details
if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIRECTORY, 'app.db') + '?check_same_thread=False'
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
