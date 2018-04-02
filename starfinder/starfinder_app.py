import flask

from starfinder import config, logging
from starfinder.helpers import helper
from starfinder.db import models

CONF = config.CONF
LOG = logging.get_logger(__name__)

app = config.app

helper = helper.Helper()

def run_server():
    app.run()

@app.route('/', methods=['GET'])
def index():
	context = {
		'current_route':'index'
	}
	return flask.render_template('index.html', **context)

if __name__ == "__main__":
    run_server()
