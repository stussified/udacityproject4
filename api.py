

import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache, taskqueue

from models import User, Game, Score
from models import GameForm, NewGameForm, MakeMoveForm, ScoreForms, StringMessage
from utils import get_by_urlsafe # this is an external py file from the project.  emulate it.
import random

# Resource containers are the objects that hold messages (aka the forms in models.py)
# It's an app engine thing.

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)

#I think there's a comma at the end because the function that uses it has additional fields to add.
GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),) 

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(MakeMoveForm, 
												urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name = messages.StringField(1),
											email=messages.StringField(2))

# I think this instantiates this variable hence the value 'CURRENT STREAK'
MEMCACHE_LONGEST_STREAK = 'LONGEST STREAK'

# The API section
@endpoints.api(name='between_the_sheets', version='v1')
class BetweenTheSheets(remote.Service):
	@endpoints.method(
		request_message=USER_REQUEST, 
		response_message = StringMessage, 
		path='user',
		name='create_user',
		http_method='POST')

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
		response_message=GameForm, 
		path='game', 
		name='new_game',
		http_method='POST')
	def new_game(self, request):
		# Creates a new game.
		user = User.query(User.name == request.user_name).get()
		if not user:
			raise endpoints.NotFoundException(
				"Username doesn't exist")
		game = Game.new_game(user.key, request.streak, request.max_guess, request.first_random_number, request.second_random_number, request.third_random_number) 

		# Use task queue to update the average streak.
		# Can be performed out of sequence.
		taskqueue.add(url='/tasks/get_longest_streak')
		return game.to_form('Good luck playing Between The Sheets!')

	@endpoints.method(
		request_message=GET_GAME_REQUEST,
		response_message=GameForm,
		path='game/{urlsafe_game_key}',
		name='get_game',
		http_method='GET')
	def get_game(self, request):
		# Make a move.  Reutrns a game state with message
		# This is where the game logic takes place.
		# you need to figure out how to save streak and also re-randomize the numbers.
		game = get_by_urlsafe(request.urlsafe_game_key, Game)
		if game:
			return game.to_form('Time to make a move!')
		else:
			raise endpoints.NotFoundException('Game not found!')

	@endpoints.method(request_message=MAKE_MOVE_REQUEST, 
						response_message=GameForm,
						path='game/{urlsafe_game_key}',
						name='make_move',
						http_method='PUT')
	def make_move(self, request):
		game = get_by_urlsafe(request.urlsafe_game_key, Game)
		if game.game_over:
			return game.to_form('Game already over!')
		print request
		sorting_list = [game.first_random_number, game.second_random_number]
		sorting_list = sorted(sorting_list, key=int)
		first_random_number = sorting_list[0]
		second_random_number = sorting_list[1]
		third_random_number = game.third_random_number
		max_guess = game.max_guess

		if first_random_number == second_random_number or third_random_number == second_random_number or third_random_number == first_random_number: # tie is auto lose
			msg = 'tie'
		elif first_random_number < third_random_number < second_random_number:
			msg = 'inside'
		elif third_random_number < first_random_number or third_random_number > second_random_number:
			msg = 'outside'
		
		if request.guess != msg or msg == 'tie':
			game.end_game()
			return game.to_form("Sorry, you lost!")

		elif request.guess == msg:
			game.first_random_number = random.choice(range(1, max_guess+1))  # max + 1 because of computer counting.
			game.second_random_number = random.choice(range(1, max_guess+1))
			game.third_random_number =random.choice(range(1, max_guess+1))
			game.streak += 1
			game.put()
			return game.to_form("You're correct!")

	@endpoints.method(response_message=ScoreForms,
					path='scores', 
					name='get_scores', 
					http_method='GET')
	
	def get_scores(self, request):
		# returns streak
		return ScoreForms(items=[score.to_form() for score in Score.query()])

	@endpoints.method(request_message=USER_REQUEST, 
		response_message=ScoreForms,
	 	path='scores/user/{user_name}',
	 	name='get_user_scores', 
	 	http_method='GET')
	 
	def get_user_scores(self, request):
	 	#returns all of an individual's streak
	 	user = User.query(User.name == request.user_name).get()
	 	if not user:
	 		raise endpoints.NotFoundException(
	 			'A user with that name does not exist')
 		scores = Score.query(Score.user == user.key)
 		return ScoreForms(items=[score.to_form() for score in scores])

	@endpoints.method(response_message=StringMessage,
	 	path='games/longest_streak', 
	 	name='get_longest_streak',
	 	http_method='GET')
	def get_longest_streak(self, request):
	 	# Get the cached value of the current streak
	 	return StringMessage(message=memcache.get(MEMCACHE_LONGEST_STREAK) or '')


	@staticmethod 
	def _cache_longest_streak():
	 	# Populates memcache with the longest streak
	 	games = Game.query(Game.game_over == True).fetch()
	 	if games:
	 		game_list = [game.streak for game in games]
	 		longest_streak_game = max(game_list)
	 		memcache.set(MEMCACHE_LONGEST_STREAK, 'The longest streak is {} correct guess(es).'.format(longest_streak_game))











api = endpoints.api_server([BetweenTheSheets])