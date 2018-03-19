import flask

users = flask.Blueprint('users', __name__, template_folder='templates')
URL_PREFIX = '/users'
BLUEPRINT = users

@users.route('/')
def view_all():
	return flask.render_template('users/all.html')
