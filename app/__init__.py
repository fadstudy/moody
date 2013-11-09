from flask import Flask
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
api = Api(app)
db = SQLAlchemy(app)

from app import views, models

api.add_resource(models.UserListAPI, '/api/v0.1/users')
api.add_resource(models.UserAPI, '/api/v0.1/users/<int:id>', endpoint='User')
