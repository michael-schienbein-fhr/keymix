import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_debugtoolbar import DebugToolbarExtension
# from auth import secret_key


app = Flask(__name__)
# testing:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///keymix'
# app.config['SECRET_KEY'] = 'secret_key'
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# debug = DebugToolbarExtension(app)
# production:
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres:///flask-heroku')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'akey')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy()
def connect_db(app):
    db.app = app
    db.init_app(app)
connect_db(app)
db.create_all()

from keymix import routes, forms, models, auth, util