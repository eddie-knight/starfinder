from flask import Flask
from starfinder import config
from flask_sqlalchemy import SQLAlchemy

__all__ = ["config", "db", "email", "signature", "token", "webpack"]
__version__ = "0.0.1"

flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@database/starfinder_development?charset=utf8'
db_engine = SQLAlchemy(flask_app)
