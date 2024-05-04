from flask import Flask, render_template, request, redirect, url_for, session
import random
from datetime import date
import psycopg2

app = Flask(__name__)
# Dictionary to store player scores and choices
player_data = {}
app.secret_key = 'your_secret_key'

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="RPS",
    user="postgres",
    password="postgres",
    host="localhost"
)
cur = conn.cursor()

# Function to get winner in single-player mode
def get_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return "It's a tie!"
    elif player_choice == 'rock':
        return "You win!" if computer_choice == 'scissors' else "Computer wins!"
    elif player_choice == 'paper':
        return "You win!" if computer_choice == 'rock' else "Computer wins!"
    elif player_choice == 'scissors':
        return "You win!" if computer_choice == 'paper' else "Computer wins!"

# Function to get score from database
def get_score(username):
    cur.execute("SELECT score FROM game_results WHERE username = %s", (username,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return 0

# Function to update score in database
def update_score(username, score_change, game_mode, date_played):
    cur.execute("INSERT INTO game_results (username, score, game_mode, date_played) VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (username) DO UPDATE SET score = game_results.score + %s",
                (username, score_change, game_mode, date_played, score_change))
    conn.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('options'))

    return render_template('index.html')

@app.route('/options', methods=['GET', 'POST'])
def options():
    if request.method == 'POST':
        mode = request.form['mode']
        if mode == 'single':
            return redirect(url_for('get_username', mode='single'))
        elif mode == 'multi':
            return redirect(url_for('multiplayer_stage'))
        elif mode == 'leaderboard':
            return redirect(url_for('leaderboard'))

    return render_template('options.html')

@app.route('/get_username', methods=['GET', 'POST'])
def get_username():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('single_player'))

    return render_template('get_username.html', message=message)

@app.route('/single_player', methods=['GET','POST'])
def single_player():
    if 'username' not in session:
        return redirect(url_for('get_username'))

    player_score = get_score(session['username'])
    result = None
    player_choice = None
    computer_choice = None

    if request.method == 'POST':
        player_choice = request.form['choice']
        if player_choice:
            computer_choice = random.choice(['rock', 'paper', 'scissors'])
            result = get_winner(player_choice, computer_choice)
            print(result)
            if result == 'You win!':
                player_score = 1
                update_score(session['username'], 1, 'single', date.today())
                return redirect(url_for('win'))
            elif result == 'Computer wins!':
                update_score(session['username'], -1, 'single', date.today())
                return redirect(url_for('lose'))
            else:
                return redirect(url_for('tie'))
            

    return render_template('single_player.html', username=session['username'], player_score=player_score,
                           result=result, player_choice=player_choice, computer_choice=computer_choice)

@app.route('/win')
def win():
    if 'username' in session:
        player_score = get_score(session['username'])
        return render_template('win.html', player_score=player_score)
    return redirect(url_for('get_username'))


@app.route('/tie')
def tie():
    if 'username' in session:
        player_score = get_score(session['username'])
        return render_template('tie.html', player_score=player_score)
    return redirect(url_for('get_username'))

@app.route('/lose')
def lose():
    if 'username' in session:
        player_score = get_score(session['username'])
        return render_template('lose.html', player_score=player_score)
    return redirect(url_for('get_username'))

@app.route('/leaderboard')
def leaderboard():
    cur.execute("SELECT username, score FROM game_results ORDER BY score DESC")
    rows = cur.fetchall()
    return render_template('leaderboard.html', rows=rows)


    return render_template('index.html')


@app.route('/multiplayer_stage', methods=['GET', 'POST'])
def multiplayer_stage():
    if request.method == 'POST':
        num_players = int(request.form['num_players'])
        return redirect(url_for('multiplayer_names', num_players=num_players))
    return render_template('multiplayer_stage.html')


@app.route('/multiplayer_names/<int:num_players>', methods=['GET', 'POST'])
def multiplayer_names(num_players):
    global player_data  # Declare player_data as global
    if request.method == 'POST':
        player_names = [request.form[f'player{i + 1}'] for i in range(num_players)]
        player_data.clear()  # Clear previous player data
        for name in player_names:
            player_data[name] = {'score': 0, 'choice': None}
        return redirect(url_for('multiplayer_game', current_player=player_names[0]))

    return render_template('multiplayer_names.html', num_players=num_players)

@app.route('/multiplayer_game', methods=['GET', 'POST'])
def multiplayer_game():
    global player_data  # Declare player_data as global
    current_player = request.args.get('current_player')
    if request.method == 'POST':
        choice = request.form['choice']
        player_data[current_player]['choice'] = choice
        return redirect(url_for('next_player', current_player=current_player))

    return render_template('multiplayer_game.html', current_player=current_player)

@app.route('/next_player', methods=['GET', 'POST'])
def next_player():
    global player_data  # Declare player_data as global
    current_player = request.args.get('current_player')
    player_names = list(player_data.keys())
    current_index = player_names.index(current_player)

    # Check if all players have made their choice
    if all(player_data[name]['choice'] is not None for name in player_data):
        # Calculate results
        for name in player_data:
            other_players = [p for p in player_data.keys() if p != name]
            other_choices = [player_data[p]['choice'] for p in other_players]
            player_choice = player_data[name]['choice']

            if all(player_choice != other_choice for other_choice in other_choices):
                # Player wins
                player_data[name]['score'] += 1
                update_score(name, 1, 'multi', date.today())

        # Redirect to results page
        return redirect(url_for('results'))

    # Move to the next player
    next_index = (current_index + 1) % len(player_names)
    next_player = player_names[next_index]
    return redirect(url_for('multiplayer_game', current_player=next_player))

@app.route('/results')
def results():
    global player_data  # Declare player_data as global
    
    # Sort players by score in descending order
    sorted_players = sorted(player_data.items(), key=lambda x: x[1]['score'], reverse=True)
    
    # Check for tie
    tie = False
    if len(set(data['score'] for player, data in sorted_players)) == 1:
        tie = True
    
    # Determine the winner (if not a tie)
    winner = None
    if not tie:
        winner = sorted_players[0][0]  # First player has the highest score
    
    return render_template('multiplayer_results.html', sorted_players=sorted_players, tie=tie, winner=winner)


if __name__ == '__main__':
    app.run(debug=True)
