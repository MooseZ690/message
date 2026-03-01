import flask
from flask import Flask, g, render_template, request, redirect, url_for
import logging, sqlite3, datetime
from datetime import datetime #imports the required packages for working with flask and databases

DATABASE = 'database.db' #sets the variable DATABASE as the file database.db

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/") #creates the home route for the flask app
def home():
    sql = """
        SELECT posts.title, posts.content, posts.name, posts.imageurl, cat.name
        FROM posts
        JOIN cat ON posts.categoryid = cat.id
        ORDER BY posts.time DESC; 
        """ #sql statement to show all posts sorted by time posted
    results = query_db(sql)
    return render_template("home.html", results=results) #sends the results to home.html, rendering the html file with the info from the database


@app.route("/newpost", methods=["GET", "POST"]) #defines function to add info into the database
def newpost():
    if request.method == "POST": #fetches all the necessary info from the newpost page
        title = request.form["title"]
        name = request.form["name"]
        content = request.form["content"]
        imageurl = request.form["imageurl"]
        categoryid = request.form["categoryid"]
        time = str(datetime.now().strftime("%Y/%m/%D %H:%M:%S"))
        db = get_db()
        db.execute(
            "INSERT INTO posts (title, name, content, imageurl, categoryid, time) VALUES (?, ?, ?, ?, ?, ?)",
            (title, name, content, imageurl, categoryid, time)
        ) #adds info from newpost.html into the database
        db.commit()
        return redirect(url_for("home"))
    else:
        sql = "SELECT * FROM cat;"
        categories = query_db(sql)
        return render_template("newpost.html", categories=categories) #gives the page the list of categories for the dropdown

@app.route("/category/<int:id>") #flask app route for the page that shows posts only from a certain category
def category(id):
    sql = """
    SELECT posts.title, posts.content, posts.name, posts.imageurl, cat.name
        FROM posts
        JOIN cat ON posts.categoryid = cat.id
        WHERE posts.categoryid = ?;""" #sql statement to get posts info where category id is selected by the user
    result = query_db(sql, (id,))
    return render_template("category.html", results=result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True) #run the app