import flask

feats = flask.Blueprint('feats', __name__, template_folder='templates')
URL_PREFIX = '/feats'
BLUEPRINT = feats