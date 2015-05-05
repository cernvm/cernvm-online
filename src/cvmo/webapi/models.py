from django.db import models
from django.contrib.auth.models import User

class WebAPIOneTimeTag(models.Model):

	uuid = models.TextField(max_length=10, primary_key=True, unique=True )
	payload = models.TextField()

	def __unicode__(self):
		return "Tag #%i" % self.id
