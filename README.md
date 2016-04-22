Between the sheets

Between the sheets is traditionally a card game where a 2 cards are initially dealt, and then guessing on whether the 3rd card will be inside the range of rank of the first 2 cards, outside the rank of of the first 2 cards or a tie.

In this version, the player will be guessing the value between 2 randomly generated numbers between 0 and and a value that they define (I would recommend 10, but the user is required to declare the maximum) and the user will be asked guess the 3rd randomly generated number will be inside or outside.  In the event of the first 2 randomly generated numbers being the same, the user will automatically lose.  The score will be counted on how many consecutive rounds the user can get correctly (called a streak).

Here is a breakdown of each endpoint:

* *cancel_game*
Enter a url safe game key in order to delete the game from the datastore.  Will not work on games that are already over (game_over value is True).

* *create_user*
Enter your email and desired user name in order to create a new user.  

* *get_game*
This list the streak and username attributed to a url safe game key

* *get_game_history*
This lists all moves made from start to finish and the message returned by the API after each move.  Turns is calculated with computer counting (starts at 0).

* *get_high_scores*
This list all high scores of all players with an optional maximum value of number of results.  Defaults to 20.

* *get_scores*
Gets the scores of most recent games by date.

* *get_user_games*

Gets all url safe keys of all games of a user.

* *get_user_rankings*
Shows a leaderboard of all usernames based on streak (highest streak at the top).

* *get_user_scores*
Gets scores of a user name sorted by streak (highest streak at the top).

* *make_move*
Allows you to make a move.  All guesses *MUST* be the string 'inside' or 'outside' or else will throw an exception.

* *new_game*
Create a new game. Requires username and largest number you would want to guess to.

