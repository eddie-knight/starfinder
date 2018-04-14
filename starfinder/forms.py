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



themes = models.Theme.query.all()

def theme_options():
	return [{'Ace Pilot','Ace Pilot'},
			{'Bounty Hunter','Bounty Hunter'},
			{'Xenoseeker', 'Xenoseeker'},
			{'Outlaw','Outlaw'},
			{'Priest', 'Priest'}]

def alignment_options():
	pass

def class_options():
	pass

def deity_options():
	pass

def world_options():
	pass

def gender_options():
	pass


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
	id = wtforms.StringField("")
	submit = wtforms.SubmitField('Delete Character')

class CharacterUpdateForm(MyBaseForm):
	id = wtforms.StringField("")
	alignment = wtforms.SelectField('Select Alignment', choices=alignment_options())
	class_type = wtforms.SelectField('Select Class', choices=class_options())
	deity = wtforms.SelectField('Select Deity', choices=deity_options())
	description = wtforms.StringField('Describe Character')
	home_world = wtforms.SelectField('Select Home World', choices=world_options())
	gender = wtforms.SelectField('Select Gender', choices=gender_options())
	name = wtforms.StringField('Change Name')
	race = wtforms.SelectField('Select Race', choices=race_options())
	theme = wtforms.SelectField('Select Theme', choices=theme_options())
	submit = wtforms.SubmitField('Save')
