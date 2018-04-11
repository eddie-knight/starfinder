from flask import Flask

__all__ = ["config", "db", "email", "signature", "token", "webpack"]
__version__ = "0.0.1"

flask_app = Flask(__name__)
