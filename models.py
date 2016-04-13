"""
models.py - This file defines the data store entities for between the sheets.

"""

import random
from datetime import datetime
from protorpc import messages
from google.appengine.ext import ndb

class User(ndb.Model):
	# Basic user profile
	name = ndb.StringProperty(required=True)
	email = ndb.StringProperty()

class Game(ndb.Model):
	# Game object
	user = ndb.KeyPropety(required=True, kind='User')
	game_over = ndb.BooleanProperty(required=True, default=False)
	streak = ndb.IntegerProperty(required=True, default=0)
	first_random_number = ndb.IntegerProperty(required=True)
	second_random_number = ndb.IntegerProperty(required=True)

	# Class methods require class to be passed as the first object. 
	# Means you can reuse them depending on the value inside of the class instantiating this function.
	@classmethod 
	def new_game(cls, user, streak, max, first_random_number, second_random_number):
		# Create a new game.  The order of the 2 numbers don't matter, so we're not going to worry about it.
		game = Game(user=user, 
					first_random_number = random.choice(range(1, max+1)),  # max + 1 because of computer counting.
					second_random_number = random.choice(range(1, max+1)),
					streak = 0,
					game_over = False)
		game.put
		return game

	def to_form(self, message):
		#returns a GameForm representation of the game.  Basically, a format to tell where you are in at the game.
		form = GameForm()
		form.urlsafekey = self.key.urlsafe()
		form.user_name = self.user.get().name
		form.streak = self.streak
		form.game_over = self.game_over
		form.message = message
		return form

	def end_game(self):
		#ends the game, stores the date and streak.
		self.game_over = True
		self.put
		score = Score(user=self.user, date=date.today(), streak=self.streak)
		score.put()


class Score(ndb.Model):
	# Score object
	user = ndb.KeyPropety(required=True, kind='User')
	date = ndb.DateProperty(required=True)
	max_streak = ndb.IntegerProperty(required=True)

	def to_form(self):
		return ScoreForm(user_name=self.user.get().name, max_streak=self.max_streak,
			date=str(self.date))

"""Here are the forms section - they're the protorpc fields that API endpoints will be using to send info.
The reason this exists is because Google App Engine requires info sent messages inside of 
request containers rather than the messages themselves."""

class GameForm(messages.Message):
	# GameForm for outbound sate information
	urlsafe_key = messages.StringField(1, required=True)
	streak = messages.StringField(2, required=True)
	game_over = messages.BooleanField(3, required=True)
	message = messages.StringField(4, required=True) #not sure what this is, find out
	user_name = messages.StringField(5, required=True)

class NewGameForm(messages.Message):
	# Used to create a new game
	user_name = messages.StringField(1, required=True)
	first_random_number = messages.IntegerField(2, required=True)
	second_random_number = messages.IntegerField(3, required=True)
	streak = messages.IntegerField(4, default=0)

class MakeMoveForm(messages.Message):
	# Make your guess in an existing game
	guess = messages.IntegerField(1, required=True)

class ScoreForm(messages.Message):
	# Form used to send stats
	user_name = messages.StringField(1, required=True)
	date = messages.StringField(2, required=True)
	streak = messages.IntegerField(3, required=True)

class ScoreForms(messages.Message):
	# Form used to send multiple stats
	items = messages.MessageField(ScoreForm, 1, repeated=True)

class StringMessage(messages.Message):
	# Not sure what this is used for, but seems like it's for sending the player a message?
	message = messages.StringField(1, required=True)






