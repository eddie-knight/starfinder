import flask

feats = flask.Blueprint('feats', __name__, template_folder='templates')
URL_PREFIX = '/feats'
BLUEPRINT = feats

@feats.route('/')
def view_all():
	return flask.render_template('feats/show.html')