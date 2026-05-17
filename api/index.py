import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app

flask_app = create_app()

def handler(environ, start_response):
    return flask_app(environ, start_response)