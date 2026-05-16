# backend/index.py
from backend.app import app

def handler(environ, start_response):
    # Strips /_/backend from the path of Flask Blueprints
    path_info = environ.get('PATH_INFO', '')
    if path_info.startswith('/_/backend'):
        environ['PATH_INFO'] = path_info[len('/_/backend'):] or '/'
        
    return app(environ, start_response)