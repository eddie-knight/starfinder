import flask

races = flask.Blueprint('races', __name__, template_folder='templates')
URL_PREFIX = '/races'
BLUEPRINT = races

@races.route('/')
def view_all():
	return flask.render_template('races/show.html')
