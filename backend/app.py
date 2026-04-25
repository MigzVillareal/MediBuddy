from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    CORS(
        app,
        supports_credentials = True,
        origins=app.config["CORS_ORIGINS"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    # app.register_blueprint(lookup_bp)
    # app.register_blueprint(drug_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)