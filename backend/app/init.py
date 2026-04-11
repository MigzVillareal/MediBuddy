from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager

from .config import Config
from app.routes import api_bp

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'medibuddy_db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)
login = LoginManager(app)

# register routes
app.register_blueprint(api_bp, url_prefix='/api')

# load models and routes
from . import models