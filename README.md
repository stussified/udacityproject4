#Between the sheets

Between the sheets is traditionally a card game where a 2 cards are initially dealt, and then guessing on whether the 3rd card will be inside the range of rank of the first 2 cards, outside the rank of of the first 2 cards or a tie.

In this version, the player will be guessing the value between 2 randomly generated numbers between 0 and and a value that they define (I would recommend 10, but the user is required to declare the maximum) and the user will be asked guess the 3rd randomly generated number will be inside or outside.  In the event of the first 2 randomly generated numbers being the same, the user will automatically lose.  The score will be counted on how many consecutive rounds the user can get correctly (called a streak).  Each correct answer will increase the value of the streak.  Getting an incorrect answer will immediately end the game.

##How to run the app:

*Update the application ID inside of app.yaml to the value of your instance of Google App Engine.
*Launch the app either locally and then launch Chrome with the following argument: --args --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:8080
*Run the app locally in order to generate the indexes, and play using the Google API explorer located at: localhost:8080/_ah/api/explorer
* Deploy if you wish to Google App Engine to play it at your applicationId.appspot.com

## Files Included:
*api.py: Contains endpoints and game playing logic.
*app.yaml: App configuration.
*cron.yaml: Cronjob configuration.
*main.py: Handler for taskqueue handler.
*models.py: Entity and message definitions including helper methods.
*utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.


Here is a breakdown of each endpoint:

*cancel_game*
*Path: 'game/{urlsafe_game_key}'
*Method: DELETE 
*Parameters: url safe game key
*Description: Enter a url safe game key in order to delete the game from the datastore.  Will not work on games that are already over (game_over value is True).

*create_user*
*Path: 'user'
*Method: POST
*Parameters: email, user_name
*Description: Enter your email and desired user name in order to create a new user.  

*get_game*
*Path: 'game/{urlsafe_game_key}'
*Method: GET
*Parameters: url safe game key
*Description: This list the streak and username attributed to a url safe game key

*get_game_history*
*Path: 'games/gamehistory'
*Method: GET
*Parameters: url safe game key
*Description: This lists all moves made from start to finish and the message returned by the API after each move.  Turns is calculated with computer counting (starts at 0).

*get_high_scores*
*Path: 'games/get_high_scores'
*Method: GET
*Parameters: number of results (optional)
*Description: This list all high scores of all players with an optional maximum value of number of results.  Defaults to 20.

*get_scores*
*Path: /scores
*Method: GET
*Parameters: None
*Description: Gets the scores of most recent games by date.

*get_user_games*
*Path: 'games/get_user_games'
*Method: GET
*Parameters: user_name
*Description: Gets all url safe keys of all games of a user.

*get_user_rankings*
*Path: 'games/get_user_rankings'
*Method: GET
*Parameters: None
*Description: Shows a leaderboard of all usernames based on streak (highest streak at the top).

*get_user_scores*
*Path: 'scores/user/{user_name}'
*Method: GET
*Parameters: user_name
*Description: Gets scores of a user name sorted by streak (highest streak at the top).

*make_move*
*Path: 'game/{urlsafe_game_key}'
*Method: PUT
*Parameters: url safe game key, guess
*Description: Allows you to make a move.  All guesses *MUST* be the string 'inside' or 'outside' or else will throw an exception.

*new_game*
*Path: 'game'
*Method: POST
*Parameters: user_name, max_guess
*Description: Create a new game. Requires username and largest number you would want to guess to.

##Models:
*User*
Stores unique usernames and email addresses.

*Game*
Stores information related to the status of the game such as whether or not it's over (game_over), the numbers that can be guessed (max_guess, first_random_number, second_random_number, third_random_number) and the current score of the game (streak).  Has Kind relationship with 'User' model.

*Score*
Stores the user's score (streak) and date. Has Kind relationship with 'User' model.

*Game History*
Stores every guess and the response from the game for each turn. Has Kind relationship with the 'Game' model.


## Forms Included:
*GameForm
** Form that holds the state information for the game.

*NewGameForm
** Form to generate a new game.

*MakeMoveForm
** Form to make a guess in the game.

*ScoreForm
** Single instance of score containing the streak, date and username.

*ScoreForms
** Form for multiple ScoreForm objects.

*HistoryForm
**Form containing the current turn, game message from the API and the user's guess.

*GameHistories
**Form for multiple HistoryForm objects.

*StringMessage
**General purpose String container.

*UserGame
**Form containing a url safe key and the user_name it's attributed to.

*UserGames
**Form for multiple UserGame objects.

*HighScore
**Form containing a user_name's streaks (their score).

*HighScores
**Form for multiple HighScore objects.

*Ranking
*Form for holding the maximum score for a user_name.