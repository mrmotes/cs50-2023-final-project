import ast
import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from categories.category_routes import categories_bp
from submissions.submission_routes import submissions_bp
from events.event_routes import events_bp
from users.user_routes import users_bp
from evaluations.evaluation_routes import evaluations_bp
from criteria.criteria_routes import criteria_bp

from helpers import *


app = Flask(__name__)
app.jinja_env.filters['zip'] = zip

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///film.db")

app.register_blueprint(categories_bp, url_prefix="/film-festival-manager/categories")
app.register_blueprint(criteria_bp, url_prefix="/film-festival-manager/criteria")
app.register_blueprint(submissions_bp, url_prefix="/film-festival-manager/submissions")
app.register_blueprint(events_bp, url_prefix="/film-festival-manager/events")
app.register_blueprint(users_bp, url_prefix="/film-festival-manager/users")

app.register_blueprint(evaluations_bp, url_prefix="/film-evaluator/")



@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
@login_required
def index():
    if session["user_type"] == "Admin":
        return redirect("/film-festival-manager")
    elif session["user_type"] == "Evaluator":
        return redirect("/film-evaluator")


@app.route("/film-festival-manager", methods=["GET"])
@login_required
def film_festival_manager():
    return render_template("film-festival-manager/film-festival-manager.html")

@app.route("/film-evaluator", methods=["GET"])
@login_required
def film_evaluator():
    return render_template("film-evaluator/film-evaluator.html")


@app.route("/login", methods=["GET", "POST"])
def login():
        if request.method == "GET":
            return render_template("login.html")
        elif request.method == "POST":
            session.clear()
            username = request.form.get("username")
            password = request.form.get("user-password")

            if not username:
                return apology("you must provide username")
            elif not password:
                return apology("you must provide password")

            user_list = db.execute("SELECT id, password_hash, type FROM users WHERE username = :username", username=username)

            if not user_list:
                return apology("invalid username")

            user = user_list[0]

            if not check_password_hash(user["password_hash"], password):
                return apology("invalid password")

            session["user_id"] = user["id"]
            session["user_type"] = user["type"]
            return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("/register.html")

    username = request.form.get("username")
    password = request.form.get("user-password")
    confirmation = request.form.get("user-password-confirmation")

    if not username:
        return apology("you must provide a valid username")
    elif not password or not confirmation:
        return apology("you must provide a password and confirmation")
    elif password != confirmation:
        return apology("password and confirmation must match")

    user_search = db.execute("SELECT * FROM users WHERE username = :username", username=username)

    if len(user_search) != 0:
        return apology("username already exists")

    password_hash = generate_password_hash(password)
    db.execute("INSERT INTO users (username, password_hash, type) VALUES(:username, :password_hash, :type)", username=username, password_hash=password_hash, type="Evaluator")
    registered_user = db.execute("SELECT id FROM users WHERE username = :username", username=username)[0]
    session["user_id"] = registered_user["id"]
    session["user_type"] = "Evaluator"

    return redirect("/")

