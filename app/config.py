import os

basedir = os.path.abspath(os.path.dirname(__file__))

LOCAL_DEV_CORS_ORIGINS = [
    "http://127.0.0.1:5000",
    "http://localhost:5173"
]

def get_cors_origins():
    cors_value = os.getenv("CORS_ORIGINS","")

    configured_origins = [
        origin.strip() for origin in cors_value.split(",") if origin.strip()
    ]
    
    if configured_origins:
        return configured_origins

    return LOCAL_DEV_CORS_ORIGINS

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"

    db_url = os.environ.get("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    if db_url and db_url.startswith("postgresql"):
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CORS_ORIGINS = get_cors_origins()