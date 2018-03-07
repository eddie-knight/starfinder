import flask

from starfinder import config

CONF = config.CONF
LOG = logging.get_logger(__name__)

def create_app():
    template_path = CONF.get('flask.templates.folder', default="templates")
    LOG.debug("TEST:" template_path)


