import flask

themes = flask.Blueprint('themes', __name__, template_folder='templates')
URL_PREFIX = '/themes'
BLUEPRINT = themes

@themes.route('/')
def view_all():
	return flask.render_template('themes/show.html')