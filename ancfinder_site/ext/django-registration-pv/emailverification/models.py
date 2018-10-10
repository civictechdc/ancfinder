from django.db import models
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django.conf import settings

import base64
import pickle
import random

from django.utils import timezone
from datetime import timedelta

CODE_LENGTH = 16
EXPIRATION_DAYS = 7
RETRY_DELAYS = [
	timedelta(minutes=15), 	# first retry is 15 minutes
	timedelta(hours=10), 		# second retry is 10 hours after the 1st retry
	timedelta(days=2)] 			# third retry is 2 days after the 2nd retry, after that we give up

class Record(models.Model):
	"""A record is for an email address pending verification, plus the action to take."""
	email = models.EmailField(db_index=True)
	code = models.CharField(max_length=CODE_LENGTH, db_index=True)
	searchkey = models.CharField(max_length=127, blank=True, null=True, db_index=True)
	action = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	last_send = models.DateTimeField(auto_now_add=True)
	hits = models.IntegerField(default=0)
	retries = models.IntegerField(default=0)
	killed = models.BooleanField(default=False)
	
	def __unicode__(self):
		try:
			a = unicode(self.get_action())
		except:
			a = "(invalid action data)"
		return self.email + ": " + a
		
	def set_code(self):
		self.code = ''.join(random.choice(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")) for x in range(CODE_LENGTH))

	def set_action(self, action):
		self.action = base64.encodestring(pickle.dumps(action))
		
	def get_action(self):
		return pickle.loads(base64.decodestring(self.action))

	def is_expired(self):
		if (timezone.now() - self.created).days >= EXPIRATION_DAYS:
			return True
		return False
	
	def url(self):
		return getattr(settings, 'SITE_ROOT_URL', "http://%s" % Site.objects.get_current().domain) \
			+ reverse("emailverification.views.processcode", args=[self.code])
	def killurl(self):
		return getattr(settings, 'SITE_ROOT_URL', "http://%s" % Site.objects.get_current().domain) \
			+ reverse("emailverification.views.killcode", args=[self.code])

class Ping(models.Model):
	"""A record to verify that an email address is still valid using a pingback."""

	def make_key():
		import os, string
		return "".join( string.letters[ord(b) % len(string.letters)] for b in os.urandom(12) )

	user = models.ForeignKey(User, unique=True, db_index=True)
	key = models.CharField(max_length=12, db_index=True, unique=True, default=make_key)
	pingtime = models.DateTimeField(blank=True, null=True)
	
	@staticmethod
	def get_ping_url(user):
		ping, isnew = Ping.objects.get_or_create(user=user)
		return settings.SITE_ROOT_URL + reverse("emailverification.views.emailping", args=[ping.key])

class BouncedEmail(models.Model):
	"""A record of a bounced email to a user."""

	user = models.ForeignKey(User, unique=True, db_index=True)
	firstbouncetime = models.DateTimeField(auto_now_add=True)
	bounces = models.IntegerField(default=1)
	

