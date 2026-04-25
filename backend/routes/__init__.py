from .auth_routes import auth_bp
from .user_routes import user_bp
from .medications import meds_bp
from .autocomplete import autocomplete_bp
from .circle import circle_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(meds_bp, url_prefix="/api/meds")
    app.register_blueprint(autocomplete_bp, url_prefix="/api/autocomplete")
    app.register_blueprint(circle_bp, url_prefix="/api/circle")