import os

base_dir = os.path.abspath(os.path.dirname(__file__))
if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
FBAPI_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FBAPI_APP_SECRET = os.environ.get('FACEBOOK_SECRET')
FBAPI_SCOPE = ['user_likes', 'user_photos', 'user_photo_video_tags']
CSRF_ENABLED = True
SECRET_KEY = '!th1553cr3tk3yha5thaty0l0swag!'
