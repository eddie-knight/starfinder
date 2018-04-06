import flask

from starfinder import config, logging, flask_app
from starfinder.helpers import helper
from starfinder.db import models
from starfinder.app import (users, characters, classes, feats, 
                            themes, spells, equipment, races, skills)

CONF = config.CONF
LOG = logging.get_logger(__name__)

helper = helper.Helper()

def run_server():
    flask_app.run()

def create_app():
    flask_app.config['template_folder'] = 'templates'
    flask_app.config['static_folder'] = 'static'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = CONF.get('db_engine_url')
    # Establish the following .py files and their routes
    blueprint_mods = [users, characters, classes, feats, themes,
                      spells, equipment, equipment, races, skills]
    for mod in blueprint_mods:
        flask_app.register_blueprint(mod.BLUEPRINT, url_prefix=mod.URL_PREFIX)
    return flask_app

app = create_app()

@app.route('/', methods=['GET'])
def index():
	context = {
		'current_route':'index'
	}
	return flask.render_template('index.html', **context)

if __name__ == "__main__":
    run_server()
