from flask import Flask
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()
db = SQLAlchemy(app)

app.config.from_object('config')

from app import views, models
