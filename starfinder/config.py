import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from starfinder import exception

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
