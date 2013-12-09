import os

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
CSRF_ENABLED = True
debug = True
SECRET_KEY = '!th1553cr3tk3yha5thaty0l0swag!'
FACEBOOK_APP_ID = '498777246878058'
FACEBOOK_APP_NAME = 'The FAD Study'
FACEBOOK_APP_SECRET = '02272a1ef565d2bbbec38c64e464094f'
SHORT_TOKEN = 0
LONG_TOKEN = 1
ROLE_USER = 0
ROLE_ADMIN = 1

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIRECTORY, 'app.db') + '?check_same_thread=False'
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
