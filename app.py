import flask
from flask import Flask, g, render_template, request, redirect, url_for
import logging, sqlite3, datetime
from datetime import datetime

DATABASE = 'database.db'

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


@app.route("/")
def home():
    sql = """
        SELECT posts.title, posts.content, posts.name, posts.imageurl, cat.name
        FROM posts
        JOIN cat ON posts.categoryid = cat.id
        ORDER BY posts.time DESC;
        """
    results = query_db(sql)
    return render_template("home.html", results=results)


@app.route("/newpost", methods=["GET", "POST"])
def newpost():
    if request.method == "POST":
        title = request.form["title"]
        name = request.form["name"]
        content = request.form["content"]
        imageurl = request.form["imageurl"]
        categoryid = request.form["categoryid"]
        current_time = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        db = get_db()
        db.execute(
            "INSERT INTO posts (title, name, content, imageurl, categoryid, time) VALUES (?, ?, ?, ?, ?, ?)",
            (title, name, content, imageurl, categoryid, current_time)
        )
        db.commit()
        return redirect(url_for("home"))
    else:
        sql = "SELECT * FROM cat;"
        categories = query_db(sql)
        return render_template("newpost.html", categories=categories)

@app.route("/category/<int:id>")
def category(id):
    sql = """
    SELECT posts.title, posts.content, posts.name, posts.imageurl, cat.name
        FROM posts
        JOIN cat ON posts.categoryid = cat.id
        WHERE posts.categoryid = ?;"""
    result = query_db(sql, (id,))
    return render_template("category.html", results=result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)