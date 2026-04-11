import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    "postgresql://jimivan:jimivan@localhost:5432/medibuddy"

    SQLALCHEMY_TRACK_MODIFICATIONS = False