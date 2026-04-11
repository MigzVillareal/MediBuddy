from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager

from .config import Config
from .routes import register_routes

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'medibuddy_db'

db = SQLAlchemy()
migrate = Migrate(app, db)
CORS(app)
login = LoginManager(app)

register_routes(app)

from . import models