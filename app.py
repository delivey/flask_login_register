from flask import Flask, render_template, session, request, redirect
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
import bcrypt
app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    if request.method == "GET":
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        connection = sqlite3.connect('database.db')
        db = connection.cursor()

        password = request.form.get("password")
        username = request.form.get("username")

        if not username or not password:
            return redirect("/") # Change to actual error
        user = db.execute("SELECT * FROM users WHERE username = (?)", (username,)).fetchone()
        connection.close()

        password_hash = user[3]

        if user is not None and bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
            session["user_id"] = user[0]
            return redirect("/")

        return redirect("/") # Change to actual error
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        connection = sqlite3.connect('database.db') # Connects to the DB
        db = connection.cursor()

        username = request.form.get("username")
        email = request.form.get("email")

        password = request.form.get("password").encode("utf-8")
        confirmation = request.form.get("confirmation").encode("utf-8")

        if not confirmation or not password or not email or not username:
            return redirect("/") # Change to actual error
        elif password != confirmation:
            return redirect("/") # Change to actual error
        else:

            hashed = bcrypt.hashpw(password, bcrypt.gensalt(14)).decode("utf-8") # Hashes and salts the password
            db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", (username, email, hashed,)) # Inserts into db

            user = db.execute("SELECT id FROM users WHERE username = (?)", (username,)).fetchone()[0]

            connection.commit()
            connection.close()

            session["user_id"] = user

            return redirect("/")
    else:
        return render_template("register.html")

@app.route("/profile")
def profile():
    connection = sqlite3.connect('database.db')
    db = connection.cursor()

    username = db.execute("SELECT username FROM users WHERE id=(?)", (session["user_id"],)).fetchone()[0] # Get's username from DB

    connection.close()

    return render_template("profile.html", username=username)