from .auth import auth_bp
from .medications import meds_bp
from .autocomplete import autocomplete_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(meds_bp, url_prefix="/api/meds")
    app.register_blueprint(autocomplete_bp)
