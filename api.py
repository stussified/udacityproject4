

import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache, taskqueue

from models import User, Game, Score
from models import # all the forms that need to be imported
from utils import get_by_urlsafe # this is an external py file from the project.  emulate it.

MEMCACHE_CURRENT_STREAK = 'CURRENT STREAK'

# Request parameters need to be held inside of Resource Containers
NEW_GAME_REQUEST = endpoints.ResourceContainer(#somethingtogohere#)




@endpoints.api(name='between_the_sheets', version='v1')
class BetweenTheSheets(remote.Service):
	@endpoints.method(
		request_message=USER_REQUEST, 
		reponse_message = StringMessage, 
		path='user',
		name='create_user',
		http_method='POST'
		)

	def create_user(self, request):
		# Create a user - requires an unique username.
		if User.query(User.name == request.user_name).get():
			raise endpoints.ConflictException(
				'Username already exists.'
				)
		user = User(name=request.user_name, email=request.email)
		user.put()
		return StringMessage(message='User {} created.'.format(
			request.user_name))

	@endpoints.method(
		request_message=NEW_GAME_REQUEST,
		reponse_message=GameForm, 
		path='game', 
		new='new_game',
		http_method='POST')
	def new_game(self, request):
		# Creates a new game.
		user = User.query(User.name == request.user_name).get()
		if not user:
			raise endpoints.NotFoundException(
				"Username doesn't exist")
		try:
			game = Game.new_game(user.key, ) # you need to figure out what variables are needed to create a game






api = endpoints.api_server([BetweenTheSheets])