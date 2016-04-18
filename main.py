# Contains taskqueue and cron jobs.  Heavily inspired by main.py from Skeleton Project Guess a Number

import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import BetweenTheSheets
from models import User

class SendReminderEmail(webapp2.RequestHandler):
	# send an email reminder to users about games using cron
	def get(self):
		app_id = app_identity.get_application_id()
		users = User.query(User.email != None)
		for user in users:
			subject = 'Keep the streak alive!'
			body = "Hello {}, keep on playing Between the sheets!".format(user.name)
			# This will send test emails
			mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
				user.email,
				subject,
				body)



class UpdateMaxStreak(webapp2.RequestHandler):
	def post(self):
		# Update longest streak in memcache
		BetweenTheSheets._cache_longest_streak()
		self.response.set_status(204)

# I have a feeling the thing to update the random numbers is going to be in here.

app = webapp2.WSGIApplication([
	('/crons/send_reminder', SendReminderEmail),
	('/tasks/get_longest_streak', UpdateMaxStreak),
	], debug=True)