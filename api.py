

import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache, taskqueue

from models import User, Game, Score, GameHistory
from models import GameForm, NewGameForm, MakeMoveForm, ScoreForms, StringMessage, UserGames, \
    HighScores, Ranking, GameHistories
from utils import get_by_urlsafe # this is an external py file from the project.  emulate it.
import random

# Resource containers are the objects that hold messages (aka the forms in models.py)
# It's an app engine thing.

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)

DELETE_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
#I think there's a comma at the end because the function that uses it has additional fields to add.
GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),)

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(MakeMoveForm,
                                                urlsafe_game_key=messages.StringField(1),)

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

USER_GAMES_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),)

HIGH_SCORES_REQUEST = endpoints.ResourceContainer(number_of_results=messages.IntegerField(
    1, default=20),)

USER_RANKING_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),)

GAME_HISTORY_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),)

# I think this instantiates this variable hence the value 'CURRENT STREAK'
MEMCACHE_LONGEST_STREAK = 'LONGEST STREAK'

# The API section
@endpoints.api(name='between_the_sheets', version='v1')
class BetweenTheSheets(remote.Service):
    @endpoints.method(
        request_message=USER_REQUEST,
        response_message=StringMessage,
        path='user',
        name='create_user',
        http_method='POST')

    def create_user(self, request):
        """
        This function requires an unique username and email in order to generate a user.
        A user is required in order to make moves inside of the game, as well as other
        various score keeping functions inside of the game.
        """
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
        """
        This function creates a new game.  In order to do this, the user must use an
        already generated user name, as well as list the number of guesses that they
        want to play the game with.  The number they choose will be the maximum number
        that will be generated in the game.
        """
        # Creates a new game.
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                "Username doesn't exist")
        game = Game.new_game(user.key, request.max_guess)

        # Use task queue to update the average streak.
        # Can be performed out of sequence.
        taskqueue.add(url='/tasks/get_longest_streak')
        return game.to_form('Good luck playing Between The Sheets!')

    @endpoints.method(
        request_message=DELETE_GAME_REQUEST,
        response_message=StringMessage,
        path='game/{urlsafe_game_key}',
        name='cancel_game',
        http_method='DELETE')

    def cancel_game(self, request):
        """
        This function will delete a game if it has not been deleted.
        It requires the url safe game key in order to work.
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and game.game_over == False:
            game.key.delete()
            return StringMessage(message='Game deleted.')
        elif game and game.game_over == True:
            raise endpoints.ConflictException("Can't delete completed games!")
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(
        request_message=GET_GAME_REQUEST,
        response_message=GameForm,
        path='game/{urlsafe_game_key}',
        name='get_game',
        http_method='GET')
    def get_game(self, request):
        """
        This function returns the current state of the game.  It requires a url safe game key
        in order to function.
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over != True:
            return game.to_form('Time to make a move!')
        if game.game_over == True:
            return game.to_form('This game is already over!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """ 
        Make a move.  This function requires a url safe game key and allows the user
        to make a guess as to whether the 3rd generated number is inside or outside
        the 1st and 2nd generated number.  The input for this MUST be either 'inside'
        or 'outside' or an error will be thrown.
        """

        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if request.guess != 'inside' and request.guess != 'outside':
            raise endpoints.BadRequestException('Must guess inside or outside')
        if game.game_over:
            return game.to_form('Game already over!')
        sorting_list = [game.first_random_number, game.second_random_number]
        sorting_list = sorted(sorting_list, key=int)
        first_random_number = sorting_list[0]
        second_random_number = sorting_list[1]
        third_random_number = game.third_random_number
        max_guess = game.max_guess
        turn = game.streak


        if first_random_number == second_random_number or \
                third_random_number == second_random_number or \
                third_random_number == first_random_number: # tie is auto lose
            msg = 'tie'

        elif first_random_number < third_random_number < second_random_number:
            msg = 'inside'
        elif third_random_number < first_random_number or \
                third_random_number > second_random_number:
            msg = 'outside'
        if request.guess != msg or msg == 'tie':
            alert = "Sorry, you lost!"
            game.end_game()

        elif request.guess == msg:
            alert = "You're correct!"
            # max + 1 because of computer counting.
            game.first_random_number = random.choice(range(1, max_guess+1))
            game.second_random_number = random.choice(range(1, max_guess+1))
            game.third_random_number = random.choice(range(1, max_guess+1))
            game.streak += 1
            game.put()

        history = GameHistory.new_record(game.key, request.urlsafe_game_key, \
                                            request.guess, turn, alert)
        history.put()

        return game.to_form(alert)


    @endpoints.method(
        request_message=GAME_HISTORY_REQUEST,
        response_message=GameHistories,
        path='games/gamehistory',
        name='get_game_history',
        http_method='GET')

    def get_game_history(self, request):
        """
        This function returns the chronological game history based on a url safe game key.
        The 'turn' value uses computer counting, so the first move done will have a turn value
        of 0.
        """
        histories = GameHistory.query(GameHistory.game_url_safekey ==
                                      request.urlsafe_game_key).order(GameHistory.turn).fetch()
        return GameHistories(items=[history.to_form() for history in histories])

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """
        This function returns the current streak (the score counting system in the game) for
        games of all users in descending order by date.
        """
        # returns streak
        return ScoreForms(items=[score.to_form() for score in Score.query().order(-Score.date)])

    @endpoints.method(request_message=HIGH_SCORES_REQUEST,
                      response_message=HighScores,
                      path='games/get_high_scores',
                      name='get_high_scores',
                      http_method='GET')

    def get_high_scores(self, request):
        """
        This returns the highest streak scores recorded in the game in decending order.
        Users can limit the number of scores returned with an optional value.
        """
        scores = Score.query().order(-Score.streak).fetch(request.number_of_results)
        return HighScores(items=[score.high_scores() for score in scores])

    @endpoints.method(request_message=USER_RANKING_REQUEST,
                      response_message=Ranking,
                      path='games/get_user_rankings',
                      name='get_user_rankings',
                      http_method='GET')

    def get_user_rankings(self, request):
        """
        Shows a leaderboard of all usernames based on streak (highest streak at the top).
        """
        max_streak = Score.query().order(-Score.streak).get()
        return max_streak.ranking()

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """
        This returns the scores of a user sorted from highest to lowest.
        Requires a username in order to work.
        """
        #returns all of an individual's streak
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A user with that name does not exist')
        scores = Score.query(Score.user == user.key).order(-Score.streak)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/longest_streak',
                      name='get_longest_streak',
                      http_method='GET')
    def get_longest_streak(self, request):
        """
        This gets the value of the longest streak from memcache.  Relies on the function
        '_cache_longest_streak()'.
        """
        # Get the cached value of the current streak
        return StringMessage(message=memcache.get(MEMCACHE_LONGEST_STREAK) or '')
    @endpoints.method(request_message=USER_GAMES_REQUEST,
                      response_message=UserGames,
                      path='games/get_user_games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """
        This returns all games of a user in the form of a url safe key.
        """
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A user with that name does not exist')
        games = Game.query(Game.user == user.key)
        return UserGames(items=[game.user_games() for game in games])
    @staticmethod
    def _cache_longest_streak():
        """ 
        This records the longest streak out of all users in completed games
        and stores the value in memcache.
        """
        games = Game.query(Game.game_over == True).fetch()
        if games:
            game_list = [game.streak for game in games]
            longest_streak_game = max(game_list)
            memcache.set(MEMCACHE_LONGEST_STREAK, 'The longest streak is {} correct guess(es).'
                         .format(longest_streak_game))

api = endpoints.api_server([BetweenTheSheets])
