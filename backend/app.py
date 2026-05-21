from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, login, migrate
from routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    CORS(
        app,
        supports_credentials=True,
        origins=app.config["CORS_ORIGINS"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    register_routes(app)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)