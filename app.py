import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
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


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)