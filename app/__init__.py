from flask import Flask
from .extenstion import db
from .routes import main

def create_app(config_file='settings.py'):

    app = Flask(__name__)
    
    app.config.from_pyfile(config_file)

    db.init_app(app)
    
    app.register_blueprint(main)

    return app
