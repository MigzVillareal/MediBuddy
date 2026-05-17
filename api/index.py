import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app

def handler(environ, start_response):
    return app(environ, start_response)