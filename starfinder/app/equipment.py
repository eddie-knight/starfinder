import flask

equipment = flask.Blueprint('equipment', __name__, template_folder='templates')
URL_PREFIX = '/equipment'
BLUEPRINT = equipment

@equipment.route('/')
def view_all():
	return flask.render_template('equipment/show.html')