import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///uno.db")


@app.route("/")
@login_required
def index():
    """Show welcome page or redirect to current game"""

    # Query database for current games
    game = db.execute("SELECT id FROM players WHERE id = :id", id=session.get("user_id"))

    # If no game currently being played
    if not game:
        return render_template("index.html")

    else:
        # Redirect user to current game
        return redirect("/current")


@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    """Start new game of UNO"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        return render_template("players.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Query database for current games
        game = db.execute("SELECT id FROM players WHERE id = :id", id=session.get("user_id"))

        # If no game currently being played
        if not game:
            return render_template("new.html")

        # If already playing a game
        else:
            return render_template("continue.html")


@app.route("/restart", methods=["GET", "POST"])
@login_required
def restart():
    """Restart game"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # If "yes" button clicked
        if "yes" in request.form:

            # Delete user's player data from database
            db.execute("DELETE FROM players WHERE id = :id", id=session.get("user_id"))

            # Delete user's scores data from database
            db.execute("DELETE FROM scores WHERE id = :id", id=session.get("user_id"))

            # Delete user's total score data from database
            db.execute("DELETE FROM total WHERE id = :id", id=session.get("user_id"))

            # Redirect user to new page
            return redirect("/new")

        # If "no" button clicked
        elif "no" in request.form:

            # Redirect user to current page
            return redirect("/current")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("restart.html")


@app.route("/players", methods=["GET", "POST"])
@login_required
def players():
    """Enter players' names"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure name for player 1 was submitted
        if not request.form.get("player1"):
            return apology("must provide name for player 1")

        # Ensure name for player 2 was submitted
        if not request.form.get("player2"):
            return apology("must provide name for player 2")

        # Ensure name for player 3 was submitted
        if not request.form.get("player3"):
            return apology("must provide name for player 3")

        # Ensure name for player 4 was submitted
        if not request.form.get("player4"):
            return apology("must provide name for player 4")

        player1 = request.form.get("player1")
        player2 = request.form.get("player2")
        player3 = request.form.get("player3")
        player4 = request.form.get("player4")

        # Insert players' names into database
        db.execute("INSERT INTO players (id, player1, player2, player3, player4) VALUES (:id, :player1, :player2, :player3, :player4)",
                   id=session.get("user_id"), player1=player1, player2=player2, player3=player3, player4=player4)

        # Initialize total score to 0
        db.execute("INSERT INTO total (id, total1, total2, total3, total4) VALUES (:id, :total1, :total2, :total3, :total4)",
                   id=session.get("user_id"), total1=0, total2=0, total3=0, total4=0)

        # Redirect user to current page
        return redirect("/current")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("players.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # HTTP parameter via GET called username
    username = request.args.get("username")

    # Query database for usernames
    usernames = db.execute("SELECT * FROM users WHERE username = :username", username=username)

    # If value of username is at least 1 and not already in database
    if len(username) >= 1 and not usernames:
        return jsonify(True)

    else:
        return jsonify(False)


@app.route("/history")
@login_required
def history():
    """Show history of played games"""

    # Query database for user's game history
    histories = db.execute("SELECT game, name, total, date FROM history WHERE id = :id", id=session.get("user_id"))

    return render_template("history.html", histories=histories)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/rules")
@login_required
def rules():
    """UNO rules."""

    return render_template("rules.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation")

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")

        # Hash password
        hash_pw = generate_password_hash(request.form.get("password"))

        # Store user into users
        user = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                          username=request.form.get("username"), hash=hash_pw)

        # If user already in databse
        if not user:
            return apology("user already exists")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Flash registered alert
        flash('Registered!')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Account settings (change password)"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure old password was submitted
        if not request.form.get("oldpassword"):
            return apology("must provide old password")

        # Ensure new password was submitted
        elif not request.form.get("newpassword"):
            return apology("must provide new password")

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation")

        # Ensure passwords match
        elif request.form.get("newpassword") != request.form.get("confirmation"):
            return apology("passwords do not match")

        # Query database for username
        pw = db.execute("SELECT hash FROM users WHERE id = :id", id=session.get("user_id"))

        # Ensure old password is correct
        if not check_password_hash(pw[0]["hash"], request.form.get("oldpassword")):
            return apology("password is not correct")

        # Hash password
        hash_pw = generate_password_hash(request.form.get("newpassword"))

        # Update user's password
        db.execute("UPDATE users SET hash = :hash WHERE id = :id", hash=hash_pw, id=session.get("user_id"))

        # Flash password changed alert
        flash('Password changed!')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("password.html")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Account settings (delete account)"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure old password was submitted
        if not request.form.get("password"):
            return apology("must password")

        # Query database for username
        pw = db.execute("SELECT hash FROM users WHERE id = :id", id=session.get("user_id"))

        # Ensure old password is correct
        if not check_password_hash(pw[0]["hash"], request.form.get("password")):
            return apology("password is not correct")

        # Query database for current games
        game = db.execute("SELECT id FROM players WHERE id = :id", id=session.get("user_id"))

        # If game currently being played
        if game:

            # Delete user's player data from database
            db.execute("DELETE FROM players WHERE id = :id", id=session.get("user_id"))

            # Delete user's scores data from database
            db.execute("DELETE FROM scores WHERE id = :id", id=session.get("user_id"))

            # Delete user's total score data from database
            db.execute("DELETE FROM total WHERE id = :id", id=session.get("user_id"))

        # Delete user's history data from database
        db.execute("DELETE FROM history WHERE id = :id", id=session.get("user_id"))

        # Delete user account from database
        db.execute("DELETE FROM users WHERE id = :id", id=session.get("user_id"))

        # Forget any user_id
        session.clear()

        # Redirect user to login form
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("delete.html")


@app.route("/current", methods=["GET", "POST"])
@login_required
def current():
    """Current game of UNO"""

    # Query database for user's names
    players = db.execute("SELECT player1, player2, player3, player4 FROM players WHERE id = :id", id=session.get("user_id"))

    # Query database for user's scores
    scores = db.execute("SELECT score1, score2, score3, score4 FROM scores WHERE id = :id", id=session.get("user_id"))

    # Query database for user's total score
    totals = db.execute("SELECT total1, total2, total3, total4 FROM total WHERE id = :id", id=session.get("user_id"))

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # If "update" button clicked
        if "update" in request.form:

            # Redirect user to update page
            return redirect("/update")

        # If "restart" button clicked
        elif "restart" in request.form:

            # Redirect user to restart page
            return redirect("/restart")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Query database for current games
        game = db.execute("SELECT id FROM players WHERE id = :id", id=session.get("user_id"))

        # If no game currently being played
        if not game:
            return redirect("/new")

        # Check user's current total scores
        total = db.execute("SELECT total1, total2, total3, total4 FROM total WHERE id = :id", id=session.get("user_id"))

        # If any player has reached 500 points
        if total[0]["total1"] >= 500 or total[0]["total2"] >= 500 or total[0]["total3"] >= 500 or total[0]["total4"] >= 500:

            # Redirect user to winner page
            return redirect("/winner")

        else:
            return render_template("current.html", players=players, scores=scores, totals=totals)


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """Update scores"""

    # Query database for user's names
    players = db.execute("SELECT player1, player2, player3, player4 FROM players WHERE id = :id", id=session.get("user_id"))

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure positive score was submitted
        try:
            if int(request.form.get("score1")) < 0 or int(request.form.get("score2")) < 0 or int(request.form.get("score3")) < 0 or int(request.form.get("score4")) < 0:
                return apology("must provide positive score")
        except ValueError:
            return apology("must provide positive score")

        score1 = int(request.form.get("score1"))
        score2 = int(request.form.get("score2"))
        score3 = int(request.form.get("score3"))
        score4 = int(request.form.get("score4"))

        # Insert players' scores into database
        db.execute("INSERT INTO scores (id, score1, score2, score3, score4) VALUES (:id, :score1, :score2, :score3, :score4)",
                   id=session.get("user_id"), score1=score1, score2=score2, score3=score3, score4=score4)

        # Check user's current total score
        check1 = db.execute("SELECT total1 FROM total WHERE id = :id", id=session.get("user_id"))
        check2 = db.execute("SELECT total2 FROM total WHERE id = :id", id=session.get("user_id"))
        check3 = db.execute("SELECT total3 FROM total WHERE id = :id", id=session.get("user_id"))
        check4 = db.execute("SELECT total4 FROM total WHERE id = :id", id=session.get("user_id"))

        # Calculate new total scores
        total1 = check1[0]["total1"] + score1
        total2 = check2[0]["total2"] + score2
        total3 = check3[0]["total3"] + score3
        total4 = check4[0]["total4"] + score4

        # Update players' total score in database
        db.execute("UPDATE total SET total1 = :total1, total2 = :total2, total3 = :total3, total4 = :total4 WHERE id = :id",
                   total1=total1, total2=total2, total3=total3, total4=total4, id=session.get("user_id"))

        # If maximum score of 500 has been reached
        if total1 >= 500 or total2 >= 500 or total3 >= 500 or total4 >= 500:
            return redirect("winner")

        # Flash scores updated alert
        flash('Scores updated!')

        # Redirect user to current page
        return redirect("/current")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("update.html", players=players)


@app.route("/winner", methods=["GET", "POST"])
@login_required
def winner():
    """Winner of the game (500 points reached)"""

    # Query database for user's names
    players = db.execute("SELECT player1, player2, player3, player4 FROM players WHERE id = :id", id=session.get("user_id"))

    # Query database for user's scores
    scores = db.execute("SELECT score1, score2, score3, score4 FROM scores WHERE id = :id", id=session.get("user_id"))

    # Query database for user's total score
    totals = db.execute("SELECT total1, total2, total3, total4 FROM total WHERE id = :id", id=session.get("user_id"))

    # Determine winner of game
    if totals[0]["total1"] >= 500:
        winner = players[0]["player1"]
    if totals[0]["total2"] >= 500:
        winner = players[0]["player2"]
    if totals[0]["total3"] >= 500:
        winner = players[0]["player3"]
    if totals[0]["total4"] >= 500:
        winner = players[0]["player4"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # If "save" button clicked
        if "save" in request.form:

            # If player1 has won:
            if totals[0]["total1"] >= 500:
                db.execute("INSERT INTO history (id, name, total) VALUES (:id, :name, :total)",
                           id=session.get("user_id"), name=players[0]["player1"], total=totals[0]["total1"])

            # If player2 has won:
            if totals[0]["total2"] >= 500:
                db.execute("INSERT INTO history (id, name, total) VALUES (:id, :name, :total)",
                           id=session.get("user_id"), name=players[0]["player2"], total=totals[0]["total2"])

            # If player3 has won:
            if totals[0]["total3"] >= 500:
                db.execute("INSERT INTO history (id, name, total) VALUES (:id, :name, :total)",
                           id=session.get("user_id"), name=players[0]["player3"], total=totals[0]["total3"])

            # If player4 has won:
            if totals[0]["total4"] >= 500:
                db.execute("INSERT INTO history (id, name, total) VALUES (:id, :name, :total)",
                           id=session.get("user_id"), name=players[0]["player4"], total=totals[0]["total4"])

            # Delete user's player data from database
            db.execute("DELETE FROM players WHERE id = :id", id=session.get("user_id"))

            # Delete user's scores data from database
            db.execute("DELETE FROM scores WHERE id = :id", id=session.get("user_id"))

            # Delete user's total score data from database
            db.execute("DELETE FROM total WHERE id = :id", id=session.get("user_id"))

            # Redirect user to history page
            return redirect("/history")

        # If "delete" button clicked
        elif "delete" in request.form:

            # Delete user's player data from database
            db.execute("DELETE FROM players WHERE id = :id", id=session.get("user_id"))

            # Delete user's scores data from database
            db.execute("DELETE FROM scores WHERE id = :id", id=session.get("user_id"))

            # Delete user's total score data from database
            db.execute("DELETE FROM total WHERE id = :id", id=session.get("user_id"))

            # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("winner.html", players=players, scores=scores, totals=totals, winner=winner)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
