from flask import Flask, g, render_template, request, redirect, url_for
import logging, sqlite3, datetime
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = 'database.db'
#sets the variable DATABASE as the file database.db

app = Flask(__name__)


def get_db():
    #try to get the database connection in flasks g object
    db = getattr(g, '_database', None)
    if db is None:
        #if the database isn't connected
        db = g._database = sqlite3.connect(DATABASE)
        #create a new connection to the database
    return db


@app.teardown_appcontext
def close_connection(exception):
    #get the database connection from g
    db = getattr(g, '_database', None)
    if db is not None:
        #if a connection exists
        db.close()
        #close db connection when request finishes


def query_db(query, args=(), one=False):
    #execute the sql query with optional arguments
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    #fetch all results from the query
    cur.close()
    #closes the cursor after the query
    return (rv[0] if rv else None) if one else rv
    #if first argument == True return only the first result, otherwise return all results

@app.route("/") #creates the home route for the flask app
def home():
    sql = """
        SELECT posts.title, posts.content, posts.name, posts.imageurl, cat.name, posts.time, posts.id, posts.reply
        FROM posts
        JOIN cat ON posts.categoryid = cat.id
        ORDER BY posts.time DESC; 
        """ 
        #sql statement to return all posts from the database
    results = query_db(sql)
    return render_template("home.html", results=results, today=datetime.now().strftime("%Y-%m-%d")) #sends the results to home.html, rendering the html file with the info from the database


@app.route("/newpost", methods=["GET", "POST"]) #app route if just a new post
@app.route("/newpost/<int:id>", methods=["GET", "POST"]) #app route if replying to another post
def newpost(id=None):

    if request.method == "POST":
        title = request.form["title"]
        name = request.form["name"]
        content = request.form["content"]
        imageurl = request.form["imageurl"]
        categoryid = request.form["categoryid"]

        # if replying, use the id from the URL
        reply = id if id else None

        time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        db = get_db()
        db.execute(
            "INSERT INTO posts (title, name, content, imageurl, categoryid, time, reply) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, name, content, imageurl, categoryid, time, reply)
        )
        db.commit()
        #put post info into database
        return redirect(url_for("home"))
        #send user back to homepage after posting
    else:
        sql = "SELECT * FROM cat"
        #sql statement to get all info from categories table
        categories = query_db(sql)

        return render_template(
            "newpost.html",
            categories=categories,
            reply_id=id
        )

@app.route("/category/<int:id>") #flask app route for the page that shows posts only from a certain category
def category(id):
    sql = """
    SELECT posts.title, posts.content, posts.name, posts.imageurl, cat.name, posts.id, posts.time, posts.reply  
        FROM posts
        JOIN cat ON posts.categoryid = cat.id
        WHERE posts.categoryid = ?
        ORDER BY posts.time DESC;
        """
        #sql statement to return posts info where category id is selected by the user
    result = query_db(sql, (id,))
    return render_template("category.html", results=result)

@app.route("/post/<int:id>") #app route for looking at an individual post
def post(id):
    sql = """
    SELECT posts.title, posts.content, posts.name, posts.imageurl, cat.name, posts.id, posts.time
        FROM posts
        JOIN cat ON posts.categoryid = cat.id
        WHERE posts.id = ?;
        """
        #sql statement to return posts info where category id is selected by the user
    result = query_db(sql, (id,), True)
    return render_template("post.html", results=result)

@app.route("/allposts")
def allposts():
    sql = """    
    SELECT posts.title, posts.content, posts.name, posts.imageurl, cat.name, posts.id, posts.time, posts.reply
    FROM posts
    JOIN cat ON posts.categoryid = cat.id
    ORDER BY posts.time DESC;
    """
    #sql statement to return all relevant info from posts table
    results = query_db(sql)
    return render_template(
        "allposts.html", results=results, today=datetime.now().strftime("%Y-%m-%d"))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True) #run the app