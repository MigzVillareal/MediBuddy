from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db
from extensions import db, login
from routes import register_routes

def create_app():
    # initialize flask object
    app = Flask(__name__)
    app.config.from_object(Config)

    # database initialization
    db.init_app(app)

    # CORS Config
    CORS(
        app,
        supports_credentials = True,
        origins=app.config["CORS_ORIGINS"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    return app

app = create_app()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)