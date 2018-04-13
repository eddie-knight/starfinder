from starfinder.db import models
from starfinder import logging

LOG = logging.get_logger(__name__)

class Helper(object):

	def update_character(self, form, char):
		LOG.debug(char)
		attributes = dict(char).keys
		for key, value in attributes:
			if key in form:
				setattr(char, key, getattr(form, key))
		models.Session.add(char)
		models.Session.commit()
