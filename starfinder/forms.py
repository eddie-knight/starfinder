import arrow
import wtforms
from wtforms.csrf.session import SessionCSRF
from flask import session

from starfinder import config, logging
from starfinder.db import models

CONF = config.CONF
LOG = logging.get_logger(__name__)


def race_options():
	return [('1','Android'),
			('2','Human'),
			('3', 'Kasatha')]


def theme_options():
	return [('Ace Pilot','Ace Pilot'),
			('Bounty Hunter','Bounty Hunter'),
			('Xenoseeker', 'Xenoseeker'),
			('Outlaw','Outlaw'),
			('Priest', 'Priest')]


def alignment_options():
	return [('a', 'a'),
			('b', 'b'),
			('c', 'c')]


def class_options():
	return [('a', 'a'),
			('b', 'b'),
			('c', 'c')]


def deity_options():
	return [('a', 'a'),
			('b', 'b'),
			('c', 'c')]


def world_options():
	return [('a', 'a'),
			('b', 'b'),
			('c', 'c')]


def gender_options():
	return [('a', 'a'),
			('b', 'b'),
			('c', 'c')]


def character_options():
	return [('a', 'a'),
			('b', 'b'),
			('c', 'c')]


def spell_options():
	return [('a', 'a'),
			('b', 'b'),
			('c', 'c')]


def feat_options():
	return [('a', 'a'),
			('b', 'b'),
			('c', 'c')]


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
	alignment_id = wtforms.SelectField('Select Alignment', choices=alignment_options())
	class_id = wtforms.SelectField('Select Class', choices=class_options())
	deity_id = wtforms.SelectField('Select Deity', choices=deity_options())
	description = wtforms.StringField('Describe Character')
	home_world_id = wtforms.SelectField('Select Home World', choices=world_options())
	gender = wtforms.SelectField('Select Gender', choices=gender_options())
	name = wtforms.StringField('Change Name')
	race_id = wtforms.SelectField('Select Race', choices=race_options())
	theme_id = wtforms.SelectField('Select Theme', choices=theme_options())
	strength = wtforms.IntegerField('Strength')
	dexterity = wtforms.IntegerField('Dexterity')
	constitution = wtforms.IntegerField('Constitution')
	intelligence = wtforms.IntegerField('Intelligence')
	wisdom = wtforms.IntegerField('Wisdom')
	charisma = wtforms.IntegerField('Charisma')
	submit = wtforms.SubmitField('Save')


class CharacterFeatsForm(MyBaseForm):
	id = wtforms.StringField("")
	character_id = wtforms.SelectField('Select Character', choices=character_options())
	feat_id = wtforms.SelectField('Select Feat', choices=feat_options())


class CharacterSpellsForm(MyBaseForm):
	id = wtforms.StringField("")
	character_id = wtforms.SelectField('Select Character', choices=character_options())
	spell_id = wtforms.SelectField('Select Spell', choices=spell_options())


class CharacterSkillsForm(MyBaseForm):
	id = wtforms.StringField("")
	acrobatics = wtforms.IntegerField('acrobatics')
	athletics = wtforms.IntegerField('athletics')
	bluff = wtforms.IntegerField('bluff')
	computers = wtforms.IntegerField('computers')
	culture = wtforms.IntegerField('culture')
	diplomacy = wtforms.IntegerField('diplomacy')
	disguise = wtforms.IntegerField('disguise')
	engineering = wtforms.IntegerField('engineering')
	intimidate = wtforms.IntegerField('intimidate')
	life_science = wtforms.IntegerField('life_science')
	medicine = wtforms.IntegerField('medicine')
	mysticsm = wtforms.IntegerField('mysticsm')
	perception = wtforms.IntegerField('perception')
	physical_science = wtforms.IntegerField('physical_science')
	piloting = wtforms.IntegerField('piloting')
	profession = wtforms.IntegerField('profession')
	sense_motive = wtforms.IntegerField('sense_motive')
	sleight_of_hand = wtforms.IntegerField('sleight_of_hand')
	stealth = wtforms.IntegerField('stealth')
	survival = wtforms.IntegerField('survival')
	submit = wtforms.SubmitField('Save')
