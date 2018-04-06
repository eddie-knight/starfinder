import arrow
import wtforms
from wtforms.csrf.session import SessionCSRF
from flask import session

from starfinder import config, logging

CONF = config.CONF
LOG = logging.get_logger(__name__)

class MyBaseForm(wtforms.Form):
	class Meta:
		csrf = True
		csrf_class = SessionCSRF
		secret = CONF.get("csrf.secret.key")
		csrf_secret = str.encode(secret)
		csrf_time_limit = arrow.Arrow.utcnow().replace(minutes=20).utcoffset()

		@property
		def csrf_context(self):
			return session

class CharacterCreateForm(MyBaseForm):
	name = wtforms.StringField(
		"Character Name", [wtforms.validators.DataRequired()])
	submit = wtforms.SubmitField('Create Character')

class CharacterDeleteForm(MyBaseForm):
	id = wtforms.StringField("Character ID")
	submit = wtforms.SubmitField('Delete Character')
