from .auth import auth_bp
from .medications import meds_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(meds_bp, url_prefix="/api/meds")