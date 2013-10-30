
from flask import Flask, g, url_for, request
from flask.ext.sqlalchemy import SQLAlchemy
import facebook

FACEBOOK_APP_ID = '498777246878058'
FACEBOOK_APP_NAME = 'The FAD Study'
FACEBOOK_APP_SECRET = '02272a1ef565d2bbbec38c64e464094f'

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

from app import views, models
