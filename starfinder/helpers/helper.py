from starfinder.db import models


class Helper(object):

	def existing_user(self, username):
	    return models.User._get_by("username", username)

	def is_existing_user(self, username):
	    return self.existing_user(username) is not None
