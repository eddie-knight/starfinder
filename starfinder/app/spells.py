import flask

spells = flask.Blueprint('spells', __name__, template_folder='templates')
URL_PREFIX = '/spells'
BLUEPRINT = spells

@spells.route('/')
def view_all():
	return flask.render_template('spells/show.html')
