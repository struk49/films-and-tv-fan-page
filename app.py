import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    characters = list(mongo.db.characters.find({"$text": {"$search": query}}))
    return render_template("characters.html", characters=characters)

    
@app.route("/get_characters")
def get_characters():
    characters = mongo.db.characters.find()
    return render_template("characters.html", characters=characters)


@app.route("/get_films")
def get_films():
    films = list(mongo.db.films.find())
    return render_template("films.html", films=films)


@app.route("/get_shows")
def get_shows():
    shows = list(mongo.db.shows.find())
    return render_template("tv.html", shows=shows)


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("category.html", categories=categories)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("signin"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("signin"))

    return render_template("signin.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("signin"))


@app.route("/signout")
def signout():
    # remove user from session cookie
    flash("You have been signed out")
    session.pop("user")
    return redirect(url_for("signin"))


@app.route("/add_show", methods=["GET", "POST"])
def add_show():
    if request.method == "POST":
        show = {
            "category_name": request.form.get("category_name"),
            "show_name": request.form.get("show_name"),
            "show_description": request.form.get("show_description"),
            "show_producer": request.form.get("show_producer"),
            "based_on": request.form.get("based_on"),
            "posted_by": session["user"]
        }
        mongo.db.shows.insert_one(show)
        flash("show successfully added")
        return redirect(url_for('get_shows'))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_show.html", categories=categories)


@app.route("/add_film", methods=["GET", "POST"])
def add_film():
    if request.method == "POST":
        show = {
            "category_name": request.form.get("category_name"),
            "film_name": request.form.get("film_name"),
            "film_description": request.form.get("film_description"),
            "film_creator": request.form.get("film_creator"),
        }
        mongo.db.films.insert_one(film)
        flash("film successfully added")
        return redirect(url_for('get_films'))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_film.html", categories=categories)


@app.route("/add_character", methods=["GET", "POST"])
def add_character():
    if request.method == "POST":
        show = {
            "category_name": request.form.get("category_name"),
            "character_name": request.form.get("character_name"),
            "character_description": request.form.get("character_description"),
            "character_film": request.form.get("character_film"),
            "character_actor": request.form.get("character_actor"),
            "film_creator": request.form.get("film_creator"),
        }
        mongo.db.characters.insert_one(character)
        flash("character successfully added")
        return redirect(url_for('get_character'))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_characters.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New category added")
        return redirect(url_for("get_categories"))
        
    return render_template("add_category.html")



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)