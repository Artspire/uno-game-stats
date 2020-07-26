# Uno Game Stats

UNO Game Stats is a website that allows registered users to keep track of the scores of their game(s) of UNO.

It can replace a piece of paper that might get lost or damaged.

# Built with

Flask (https://www.palletsprojects.com/p/flask/)

## Functionality

Users can create an account and log in.

After logging in, the user is presented with a welcome page with a button to start a new game of UNO.

When the "Start new game" button on the home page or the "New Game" button in the navbar is clicked, the user is redirected to the /new page and asked to select the number of players.

After clicking on the "Next" button, the user is asked to enter the names for each player on the /players page and start the game by clicking on the "Start game" button.

A table is then displayed on the /current page that shows the players' names and their initial total score of 0.

On this page, the user has the option to update the scores by clicking on "Update scores" or restart the game by clicking on "Restart".

Clicking on "Restart" redirects the user to the /restart page and allows the user to start over.

Clicking on "Update scores" redirects the user to the /update page and allows the user to update the scores for each player.

When the user clicks the "Update" button, the user is redirected back to the /current page which now shows the points each user scored in that round and an updated total score.

When the maximum score of 500 points is reached, the user is redirected to the /winner page.

Above the table, a congratulatory message is displayed with the name of the winner.

Moreover, the user has the option to save the game or delete.

Clicking on "Save game" redirects the user to the /history page displaying a table with the number of the game, the name of the winner, the total score with which the winner won the game and the date the game was finished.

Clicking on "Delete" redirects the user back to the home page.

Lastly, the user has the ability to change their password or delete their account by clicking on "Account Settings" in the navbar.

## Additional information

It is not possible to play more than 1 game at a time.

The user's 'current game' data is saved in three seperate tables (players, scores and total)

If the user is already playing a game and clicks the "New Game" button in the navbar, the user is redirected to the /continue page and reminded that a game is already being played.

On this page, the user is asked if he/she wants to continue or restart. If the "Restart" button is clicked, the user needs to confirm his/her choice on the /restart page by clicking "Yes".

The /restart page can also be accessed by clicking on "Restart" on the /current page.

Clicking on "Current Game" in the navbar redirects to the /new page when the user is not playing a game yet.

Clicking on the UNO logo or the 'Game Stats' text in the left corner of the navbar redirects to the /current page when the user is already playing a game.

If the user decides to restart the game, all the user's 'current game' data is deleted from the database.

When the maximum score of 500 points is reached and the user clicks on the "Save game" button on the /winner page, the name of the winner, the total score with which the winner won the game and the date the game was finished is saved in a fourth table (history).

Clicking on "Delete" does not save any data in the 'history' table.

If the user decides to delete his/her account, all data linked to that user's id is deleted from the database.

## Potential future functionality

At the moment, UNO Game Stats is limited to a maximum of 4 players.

In a future update, I would like to add the ability to first select the number of players from a range (between 2 and 10) and then keep track of only the selected number (without having to add dummy players, for instance).

Unfortunately, I don't know yet how to implement that kind of functionality.

# References

Official UNO website (https://www.mattelgames.com/en-us/cards/uno?utm_source=mattel.com)

Official UNO rules (https://service.mattel.com/instruction_sheets/42001pr.pdf)