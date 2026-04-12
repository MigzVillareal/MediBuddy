from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS

from .extensions import db, login
from .config import Config
from .routes import register_routes

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'medibuddy_db'

# Initialize extensions
db.init_app(app)
login.init_app(app)
migrate = Migrate(app, db)
CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhost:5173"}},
    supports_credentials=True
)

register_routes(app)

from . import models