from starfinder.db import models
from starfinder import logging

LOG = logging.get_logger(__name__)

class Helper(object):

	def update_character(self, form, char):
		attributes = char.to_dict().keys()
		LOG.debug(attributes)
		for key in attributes:
			if key in form:
				field = getattr(form, key)
				setattr(char, key, field.data)
		models.Session.add(char)
		models.Session.commit()
