from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import DATABASE_URI, FORM_SECRET_KEY, TRACK_MODIFICATIONS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = TRACK_MODIFICATIONS
app.config["SECRET_KEY"] = FORM_SECRET_KEY
app.config["JSON_AS_ASCII"] = False

db = SQLAlchemy(app)
