import flask

from starfinder import config

CONF = config.CONF
LOG = logging.get_logger(__name__)

def create_app():
    LOG.debug("TEST")

create_app()
