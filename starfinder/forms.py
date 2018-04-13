import arrow
import wtforms
from wtforms.csrf.session import SessionCSRF
from flask import session

from starfinder import config, logging
from starfinder.db import models

CONF = config.CONF
LOG = logging.get_logger(__name__)

races = models.Race.query.all()

def race_options():
	# These Left & Right values are occasionally inverting...?
	return [{'1','Android'},
			{'2','Human'},
			{'3', 'Kasatha'}]


themes = models.Theme.query.all()

def theme_options():
	return [{'Ace Pilot','Ace Pilot'},
			{'Bounty Hunter','Bounty Hunter'},
			{'Xenoseeker', 'Xenoseeker'},
			{'Outlaw','Outlaw'},
			{'Priest', 'Priest'}]


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

class CharacterRaceForm(MyBaseForm):
	id = wtforms.StringField("Character ID")
	race = wtforms.SelectField('Select Race', choices=race_options())
	submit = wtforms.SubmitField('Next')

class CharacterThemeForm(MyBaseForm):
	id = wtforms.StringField("Character ID")
	theme = wtforms.SelectField('Select Theme', choices=theme_options())
	submit = wtforms.SubmitField('Next')
