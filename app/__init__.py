from flask import Flask
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()
db = SQLAlchemy(app)

csrf = CsrfProtect()
csrf.init_app(app)

app.config.from_object('config')

from app import views, models
