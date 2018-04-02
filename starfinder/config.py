import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from starfinder import exception
from starfinder.app import users, classes, feats

class Config(object):

    def __init__(self):
    	self._cfg = {}

    def _to_env_key(self, key):
        return ('_'.join(key.split('.'))).upper()

    def get(self, key, default=None):
        if key not in self._cfg:
            env_key = self._to_env_key(key)
            if env_key not in os.environ:
                if default:
                    return default
                raise exception.ConfigKeyNotFound(key=key)
            else:
                self._cfg[key] = os.environ[env_key]
        return self._cfg[key]

    def get_array(self, key, default=None):
        return [value.strip() for value in self.get(key, default).split(",")]

CONF = Config()
ENGINE_URL = CONF.get("DB_ENGINE_URL")

def create_app():
    app = Flask(__name__)
    app.config['template_folder'] = 'templates'
    app.config['static_folder'] = 'static'
    app.config['SQLALCHEMY_DATABASE_URI'] = ENGINE_URL
    # Establish the following .py files and their routes
    blueprint_mods = [users, classes, feats]
    for mod in blueprint_mods:
        app.register_blueprint(mod.BLUEPRINT, url_prefix=mod.URL_PREFIX)
    return app

app = create_app()
db_engine = SQLAlchemy(app)

