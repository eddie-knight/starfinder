import flask

characters = flask.Blueprint('characters', __name__, template_folder='templates')
URL_PREFIX = '/characters'
BLUEPRINT = characters

@characters.route('/')
def view_all():
	current_route = 'characters.view_all'
	return flask.render_template('characters/show.html', current_route=current_route)
