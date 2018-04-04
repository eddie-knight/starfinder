import flask

skills = flask.Blueprint('skills', __name__, template_folder='templates')
URL_PREFIX = '/skills'
BLUEPRINT = skills

@skills.route('/')
def view_all():
	return flask.render_template('skills/show.html')