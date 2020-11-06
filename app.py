from flask import Flask, render_template, session, request, redirect
from flask_session import Session
from tempfile import mkdtemp
import bcrypt
import psycopg2
from dotenv import load_dotenv
load_dotenv()
import os

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/login/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        conn = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = conn.cursor()

        password = request.form.get("password")
        username = request.form.get("username")

        if not username or not password:
            return redirect("/") # Change to actual error

        db.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = db.fetchone()
        conn.close()

        password_hash = user[3]

        if user is not None and bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
            session["user_id"] = user[0]
            return redirect("/")

        return redirect("/") # Change to actual error
    else:
        return render_template("login.html")

@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        conn = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = conn.cursor()

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
            db.execute("INSERT INTO users (username, email, hash) VALUES (%s, %s, %s)", (username, email, hashed,)) # Inserts into db

            db.execute("SELECT id FROM users WHERE username = %s", (username,))
            user_id = db.fetchone()[0]
            
            conn.commit()
            conn.close()

            session["user_id"] = user_id

            return redirect("/")
    else:
        return render_template("register.html")

@app.route("/profile/", methods=["GET"])
def profile():

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    try:
        db.execute("SELECT username FROM users WHERE id = %s", (session["user_id"],)) # Get's username from DB
        username = db.fetchone()[0]
    except:
        return redirect("/")

    conn.close()

    return render_template("profile.html", username=username)

@app.route("/logout/", methods=["GET"])
def logout():
    if session.get('user_id') is not None:
        session.clear()
    else:
        pass
    return redirect("/")
