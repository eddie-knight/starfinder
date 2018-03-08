import flask

from starfinder import config, logging

CONF = config.CONF
LOG = logging.get_logger(__name__)

def create_app():
    LOG.debug("TEST")
    template_path = CONF.get('flask.templates.folder', 'templates')
    static_path = CONF.get('flask.static.folder', 'static')
    flask_app = flask.Flask(__name__,
                            template_folder=template_path,
                            static_folder=static_path)
    return flask_app

app = create_app()

def run_server():
    app.run()

@app.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')

if __name__ == "__main__":
    run_server()
