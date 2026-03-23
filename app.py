from flask import Flask, g, render_template, request, redirect, url_for, session, jsonify
import logging, sqlite3, datetime, random
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

DATABASE = 'database.db'
#sets the variable DATABASE as the file database.db

app = Flask(__name__)
app.secret_key = "serendipitous"

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
        SELECT posts.title, posts.content, posts.name, posts.imageurl, cat.name, posts.time, posts.id, posts.reply, cat.id
        FROM posts
        JOIN cat ON posts.categoryid = cat.id
        ORDER BY posts.time DESC; 
        """ 
        #sql statement to return all posts from the database
    userssql = """
        SELECT users.id, users.username
        FROM users
        ORDER BY users.id ASC;
        """
    comments = """
        SELECT * FROM comments;
        """
    likes = """
        SELECT * FROM likes;
        """
    likes = query_db(likes)
    users = query_db(userssql)
    results = query_db(sql)
    comments = query_db(comments)
    return render_template("home.html", results=results, users=users, comments=comments, likes=likes, today=datetime.now().strftime("%Y-%m-%d")) #sends the results to home.html, rendering the html file with the info from the database

@app.route("/like/<int:id>", methods=["POST"])
def like(id):
    db = get_db()
    liker = session.get('username')
    sql = "SELECT * FROM likes;"
    likes = query_db(sql)
    for row in likes:
        if row[1] == id:
            if row[0] == liker:
                return redirect(request.referrer or url_for('index'))
    db.execute(            
        "INSERT INTO likes (liker, postid) VALUES (?, ?)",
        (liker, id)
    )
    db.commit()
    return redirect(request.referrer or url_for('index'))

@app.route("/register", methods=["GET","POST"])
def register():
    failed = request.args.get("failed") == "True"

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        imageurl = request.form["imageurl"]
        email = request.form["email"]

        hashed_password = generate_password_hash(password)

        users = query_db("SELECT email, username FROM users")

        for row in users:
            if row[1] == username or row[0] == email:
                return redirect(url_for("register", failed=True))

        db = get_db()
        db.execute(
            "INSERT INTO users (username, password, imageurl, email) VALUES (?, ?, ?, ?)",
            (username, hashed_password, imageurl, email)
        )
        db.commit()

        user = query_db(
            "SELECT * FROM users WHERE username = ?",
            (username,),
            one=True
        )

        session["user_id"] = user[0]
        session["username"] = user[1]

        return redirect(url_for("home"))

    return render_template("register.html", failed=failed)

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = query_db(
            "SELECT * FROM users WHERE username = ?",
            (username,),
            one=True
        )

        if user and check_password_hash(user[2], password):

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/newpost", methods=["GET", "POST"]) #app route if just a new post
@app.route("/newpost/<int:id>", methods=["GET", "POST"]) #app route if replying to another post
def newpost(id=None):
    sql = """
    SELECT posts.title, posts.content, posts.name, posts.imageurl, cat.name, posts.id, posts.time, posts.reply
    FROM posts
    JOIN cat ON posts.categoryid = cat.id
    ORDER BY posts.time DESC;
    """
    #sql statement to get all relevant info from posts table
    results = query_db(sql)
    
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form["title"]
        name = session["username"]
        content = request.form["content"]
        imageurl = request.form["imageurl"]
        if not imageurl:
            imageurl = "https://operaparallele.org/wp-content/uploads/2023/09/Placeholder_Image.png"
        categoryid = request.form["categoryid"]
        with open("profanity.txt", "r") as profanity: #open profanity.txt as profanity so the code can read it
            badwords = [line.strip() for line in profanity]
        for word in badwords:
            stars = "*" * len(word) #sets the *s of the censored word to its length
            content = content.replace(word, stars)
            title = title.replace(word, stars)
        
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
            reply_id=id,
            results=results
        )

@app.route("/admin")
def admin():
    users = """SELECT users.username, users.type 
            FROM users;"""
    users = query_db(users)
    for row in users:
        if row[0] == session.get('username'):
            if row[1] == 'admin':
                return render_template("admin.html", users=users)
    return redirect(url_for("home"))
    
            

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

@app.route("/allposts")
def allposts():
    sql = """    
    SELECT posts.title, posts.content, posts.name, posts.imageurl, cat.name, posts.id, posts.time, posts.reply  
    FROM posts
    JOIN cat ON posts.categoryid = cat.id
    ORDER BY posts.time DESC;
    """
    #sql statement to return all relevant info from posts table
    likes = """
        SELECT * FROM likes;
        """
    likes = query_db(likes)
    results = query_db(sql)
    return render_template(
        "allposts.html", results=results, likes=likes, today=datetime.now().strftime("%Y-%m-%d"))

@app.route("/userposts/<username>")
def userposts(username):
    sql = """    
    SELECT posts.title, posts.content, posts.name, posts.imageurl, cat.name, posts.id, posts.time, posts.reply
    FROM posts
    JOIN cat ON posts.categoryid = cat.id
    WHERE posts.name = ?
    ORDER BY posts.time DESC;
    """
    userdb = """
    SELECT users.id, users.imageurl, users.username
    FROM users
    WHERE users.username = ?;
    """
    userdb = query_db(userdb, (username,))
    results = query_db(sql, (username,))
    profilepic = userdb[0][1]
    
    return render_template("userposts.html", results=results, profilepic=profilepic, username=username)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True) #run the app