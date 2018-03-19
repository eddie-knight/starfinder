import flask

classes = flask.Blueprint('classes', __name__, template_folder='templates')
URL_PREFIX = '/classes'
BLUEPRINT = classes