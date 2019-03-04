from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import DATABASE_URI, FORM_SECRET_KEY

app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config['SECRET_KEY'] = FORM_SECRET_KEY

db = SQLAlchemy(app)
