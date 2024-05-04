# RockPaperScissors

# Features:

Multiplayer Mode:

Players can create accounts and log in to challenge other registered users.
Upon logging in, players can see a list of online players available for a match.
Players can invite others for a match, and upon acceptance, the game begins.
Real-time gameplay where both players make their choices (rock, paper, or scissors) simultaneously.
After both players make their choices, the winner is determined based on the classic rules of Rock Paper Scissors.
The results are displayed to both players, and scores are updated accordingly.
A chat feature allows players to communicate during the game.

Single Player Mode:

Players can choose to play against the computer at various difficulty levels.
The computer AI will make choices based on predetermined probabilities at different difficulty levels.
Players can earn scores based on their wins against the computer.

Global Leaderboard:

A global leaderboard displays the top scores of all registered users.
Scores are stored in a PostgreSQL database, allowing for persistence across sessions.
Users can see their rank on the leaderboard and compare their scores with others.



# Technical Complexity:

Gambit and Python:

Gambit will be used to handle the game logic, rules, and interactions.
Python will be the primary programming language for backend development.
Gambit's extensive libraries will be leveraged to create the game's mechanics and user interface.

Flask for Deployment:

Flask will be used as the web framework for deploying the game.
It will handle routing, requests, and responses between the frontend and backend.
Flask's simplicity and flexibility make it ideal for this project's web deployment needs.

PostgreSQL Database:

PostgreSQL will be used to store user accounts, game scores, and leaderboard data.
The database will ensure data integrity and provide efficient retrieval of scores for the leaderboard.
SQL queries will be used to manage user authentication, game history, and leaderboard updates.

User Authentication:

User authentication will be implemented to allow secure logins, account creation, and profile management.
Flask's authentication libraries will be utilized for this purpose.
