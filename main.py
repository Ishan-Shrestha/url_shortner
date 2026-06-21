from flask import Flask, flash, render_template, redirect, request
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy.orm import DeclarativeBase
import os
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import secrets
from datetime import datetime

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

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# DATABASE AND MODEL SETUP
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)

class User(UserMixin, db.Model):
    id = db.Column(db.String(20), primary_key = True)
    password = db.Column(db.String(200), nullable=False)

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

# FUNCTIONS
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, str(user_id))

def generate_short_url():
    short_url = secrets.token_urlsafe(8)
    return short_url

def store_url(short_url, original_url):
    data = URL(
        short_url= short_url,
        original_url = original_url,
        date_created = datetime.now(),
        user = current_user.id
    )
    db.session.add(data)
    db.session.commit()
    return "URL Link created in database!"

def store_user(id, password):
    user = User(
        id= id,
        password=password
    )
    db.session.add(user)
    db.session.commit()
    return "User is sucessfully registered in the database!"

def register_click(url):
    click = Clicks(
        url=url,
        last_click=datetime.now()
    )
    db.session.add(click)
    db.session.commit()
    return "Click was registered!"

def verify_user(id, password):
    user = User.query.filter_by(id=id).first()
    if user and bcrypt.check_password_hash(user.password, password):
        flash('successfully login!')
        return user
    else:
        flash('Error password!')
        return None

# ROUTES
@app.route('/shorten', methods=['GET','POST'])
@login_required
def shorten_link():
    if request.method == 'POST':
        original_url = request.form.get('url','').strip()
        short_url = generate_short_url()
        store_url(short_url, original_url)
        return f"A link was shortened as {short_url}!"
    return render_template('index.html')

@app.route('/<short_code>')
def look_up(short_code):
    data = URL.query.filter_by(short_url=short_code).first_or_404()
    original_url = data.original_url
    register_click(data.id)
    return redirect(original_url)

@app.route('/register', methods = ['GET','POST'])
def register_user():
    if request.method == 'POST':
        id = request.form.get('id','').strip()
        password = request.form.get('password','').strip()
        encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')
        existing_user = User.query.filter_by(id=id).first()
        if existing_user:
            flash('User of same id already exist in the database.')
            return redirect('/register')
        store_user(id, encrypted_password)
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        id = request.form.get('id','').strip()
        password = request.form.get('password','').strip()
        user = verify_user(id, password)
        if user:
            login_user(user)
            return redirect('/shorten')
    return render_template('login.html')

@app.route('/logout')
@login_required
def log_out():
    logout_user()
    return redirect('/login')

# APP START
if __name__ == '__main__':
    app.run(debug=True)