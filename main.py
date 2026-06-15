from flask import Flask, flash, render_template, redirect, request
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

# PATH VARIABLES
BASE_PATH = os.path.dirname(os.path.abspath(__name__))

load_dotenv()
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
 
# LOGGER SETUP
logging.basicConfig(
    filename='Info.log',
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# APP SETUP
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY

# DATABASE AND MODEL SETUP
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.String(20), primary_key = True)
    password = db.Column(db.String(20), nullable=False)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    short_url = db.Column(db.String(50), nullable=False, unique= True)
    original_url = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, nullable = False)
    user = db.Column(db.String(50), db.ForeignKey("user.id"), nullable = False)

class Clicks(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.Integer, db.ForeignKey("url.id"))
    last_click = db.Column(db.DateTime, nullable = False)

# APP START
if __name__ == '__main__':
    app.run(debug=True)