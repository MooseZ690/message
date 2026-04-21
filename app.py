#-----------------#
#-----MODULES-----#
#-----------------#

from flask import Flask, g, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
import sqlite3, datetime
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

#-----------------------------------------#
#-----CONNECTING/CONFIGURING DATABASE-----#
#-----------------------------------------#

DATABASE = 'database.db'
#sets the variable DATABASE as the file database.db

app = Flask(__name__)
app.secret_key = "serendipitous" #base of the password hashing
socketio = SocketIO(app)


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

#------------------------#
#-----SQL STATEMENTS-----#
#------------------------#

all = """
        SELECT posts.title, posts.content, users.name, posts.imageurl, cat.name, posts.time, posts.id, posts.reply, cat.id
        FROM posts
        JOIN cat ON posts.categoryid = cat.id
        JOIN users on posts.user_id = users.id
        ORDER BY posts.time DESC; 
    """ 
        #return all posts from the posts table

likes = """
        SELECT liker_id, postid FROM likes;
    """
        #return all relevant data from the likes table

#--------------------#
#-----APP ROUTES-----#
#--------------------#

@app.route("/") #creates the home route for the flask app
def home():
    userssql = """
        SELECT users.id, users.name
        FROM users
        ORDER BY users.id ASC;
        """
        #get user info
    comments = """
        SELECT * FROM comments;
        """
        #get comments on posts
    likes = """
        SELECT liker_id, postid FROM likes;
        """
        #get all info from likes table
    categories = """
        SELECT * FROM cat;
        """
        #get all info from category table
    likes = query_db(likes)
    users = query_db(userssql)
    results = query_db(all)
    comments = query_db(comments)
    categories = query_db(categories)
    return render_template("home.html", results=results, users=users, comments=comments, likes=likes, categories=categories, today=datetime.now().strftime("%Y-%m-%d")) #sends the results to home.html, rendering the html file with the info from the database

@app.route("/admin")
def admin():
    followers = """
    SELECT followed.name AS followed_name,
        follower.name AS follower_name
    FROM following
    JOIN users AS followed ON following.followed_id = followed.id
    JOIN users AS follower ON following.follower_id = follower.id;
    """    
    admins = """SELECT users.id, users.name, users.email, users.imageurl
    FROM admins
    JOIN users ON admins.userid = users.id
    ORDER BY admins.id DESC;
    """
    users = """SELECT users.name, users.email, users.imageurl, users.id
                FROM users;
            """
    #return all relevant data from the follower, admin, and users tables
    blacklist = "SELECT * FROM blacklist;"
    
    admins = query_db(admins)
    users = query_db(users)
    followers = query_db(followers)
    blacklist = query_db(blacklist)
    for row in admins:
        if row[0] == session.get('user_id'):
        #if the user is an admin, load the template
            return render_template("admin.html", users=users, followers=followers, admins=admins)
    session.pop("user_id", None)
    session.pop("username", None)
    return render_template("login.html", notadmin=True)
    #if the user isn't an admin, redirect to the homepage. 

@app.route("/makeadmin/<int:id>")
def makeadmin(id):
    admin = query_db("SELECT 1 FROM admins WHERE userid = ? LIMIT 1;", (id,))
    if admin:
        return redirect(request.referrer or "/")
    db = get_db()
    db.execute(
        "INSERT INTO admins (userid) VALUES (?);",
        (id,)
    )
    db.commit()
    return redirect(request.referrer or "/")
    
@app.route("/allposts")
def allposts():    
    likes = """
        SELECT liker_id, postid FROM likes;
        """
    #get all info from likes table
    likes = query_db(likes)
    results = query_db(all)
    return render_template("allposts.html", results=results, likes=likes, today=datetime.now().strftime("%Y-%m-%d"))

@app.route("/like/<int:id>", methods=["POST"])
def like(id):
    db = get_db()
    liker_id = session.get('user_id')
    #sets gets the current user, also the one liking the post
    sql = "SELECT * FROM likes;"
    #get all info from likes table
    likes = query_db(sql)
    for row in likes:
        if row[2] == id and row[1] == liker_id:
                return redirect(request.referrer or url_for('index'))
    #if the intended like has already occured, redirect back to the page the user came from
    db.execute(            
        "INSERT INTO likes (liker_id, postid) VALUES (?, ?)",
        (liker_id, id)
    )
    db.commit()
    #otherwise, commit the into to the likes database
    return redirect(request.referrer or url_for('index'))

@app.route("/unlike/<int:id>", methods=["POST"])
def unlike(id):
    db = get_db()
    liker_id = session.get('user_id')

    # Delete the like if it exists
    db.execute(
        "DELETE FROM likes WHERE liker_id = ? AND postid = ?",
        (liker_id, id)
    )
    db.commit()

    return redirect(request.referrer or url_for('index'))


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]
        imageurl = request.form["imageurl"]
        email = request.form["email"]
        #get all info from the register page

        hashed_password = generate_password_hash(password)
        #hashes the password with werkzeug
        users = query_db("SELECT email, name FROM users;")
        for row in users:
            if row[1] == name or row[0] == email:
                return render_template("register.html", inuse=True)
        #if the user is already registered, go back to register page with an error message
        db = get_db()
        db.execute(
            "INSERT INTO users (name, password, imageurl, email) VALUES (?, ?, ?, ?)",
            (name, hashed_password, imageurl, email)
        )
        db.commit()
        #otherwise, commit new account to the users database
        user = query_db(
            "SELECT * FROM users WHERE name = ?",
            (name,),
            one=True
        )
        session["user_id"] = user[0]
        session["username"] = user[1]
        return redirect(url_for("home"))
        #log the user in
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.pop("user_id", None)
        session.pop("username", None)
        #clear any existing session
        username = request.form["username"]
        password = request.form["password"]
        #gets the username and password from the login page
        user = query_db(
            "SELECT * FROM users WHERE name = ?",
            (username,),
            one=True
        )
        #finds the user with that username
        if not user:
            return render_template("login.html", incorrectuser=True, faileduser=username)
        #if there is none
        blacklisted = query_db(
            "SELECT 1 FROM blacklist WHERE userid = ?",
            (user[0],),
            one=True
        )
        if blacklisted:
            return render_template("login.html", blacklisted=True)
        #if the user has been blacklisted, return them to the login page
        if not check_password_hash(user[2], password):
            return render_template("login.html", incorrectpw=True)
        session["user_id"] = user[0]
        session["username"] = user[1]
        return redirect(url_for("home"))
        #if all is successful, add the user to session and redirect to homepage

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
    SELECT posts.title, posts.content, users.name, posts.imageurl, cat.name, posts.id, posts.time, posts.reply
    FROM posts
    JOIN cat ON posts.categoryid = cat.id
    JOIN users ON posts.user_id = users.id
    ORDER BY posts.time DESC;
    """
    #get all relevant info from posts table
    results = query_db(sql)
    
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form["title"]
        userid = session["user_id"]
        content = request.form["content"]
        imageurl = request.form["imageurl"]
        if not imageurl:
            imageurl = "https://operaparallele.org/wp-content/uploads/2023/09/Placeholder_Image.png"
        categoryid = request.form["categoryid"]
        # if replying, use the id from the URL
        reply = id if id else None
        time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db = get_db()
        db.execute(
            "INSERT INTO posts (title, user_id, content, imageurl, categoryid, time, reply) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, userid, content, imageurl, categoryid, time, reply)
        )
        db.commit()
        #put post info into database
        return redirect(url_for("home"))
        #send user back to homepage after posting
    else:
        sql = "SELECT * FROM cat"
        #get all info from categories table
        categories = query_db(sql)

        return render_template(
            "newpost.html",
            categories=categories,
            reply_id=id,
            results=results
        )

@app.route("/category/<int:id>") #flask app route for the page that shows posts only from a certain category
def category(id):
    sql = """
    SELECT posts.title, posts.content, users.name, posts.imageurl, cat.name, posts.id, posts.time, posts.reply
    FROM posts
    JOIN cat ON posts.categoryid = cat.id
    JOIN users ON posts.user_id = users.id
    WHERE posts.categoryid = ?
    ORDER BY posts.time DESC;
        """
    #get all posts with a specific category ID
    cat = """
        SELECT cat.name FROM cat WHERE cat.id = ?
    """
        #return posts info where category id is selected by the user
    likes = """
        SELECT liker_id, postid FROM likes;
        """
    allposts = """SELECT * FROM posts"""
    #all posts so replied posts from other categories can be shown
    allposts = query_db(allposts)
    cat = query_db(cat, (id,))
    result = query_db(sql, (id,))
    likes = query_db(likes)
    return render_template("category.html", results=result, allposts=allposts, cat=cat, likes=likes)

@app.route("/post/<int:id>")
def post(id):
    sql = """
        SELECT posts.title, posts.content, posts.imageurl, cat.name, posts.id, posts.time, posts.reply
        """
    #make a singular post view page here
    

@app.route("/userposts/<username>")
def userposts(username):
    sql = """
        SELECT posts.title, posts.content, users.name, posts.imageurl, cat.name, posts.id, posts.time, posts.reply
        FROM posts
        JOIN cat ON posts.categoryid = cat.id
        JOIN users on posts.user_id = users.id
        WHERE users.name = ?
        ORDER BY posts.time DESC;
    """
    user_sql = """
        SELECT users.id, users.imageurl, users.name
        FROM users
        WHERE users.name = ?;
    """
    followers_sql = """
        SELECT follower_id, followed_id
        FROM following;
    """
    followers = query_db(followers_sql)
    userdb = query_db(user_sql, (username,))
    results = query_db(sql, (username,))
    if not userdb:
        return "User not found"
    profilepic = userdb[0][1]
    userid = userdb[0][0]
    following = False
    for row in followers:
        if row[0] == session.get('user_id') and row[1] == userid:
            following = True
            break
    return render_template( "userposts.html", results=results, profilepic=profilepic, username=username, userid=userid, following=following)
    
@app.route("/follow/<followed_id>")
def follow(followed_id):
    if "user_id" not in session: #if you're not logged in
        return redirect(url_for("login")) #go to login page
    follower_id = session.get('user_id')
    results = query_db("SELECT * FROM following;")
    for row in results:
        if row[0] == follower_id and row[1] == followed_id:
            return render_template('userposts')
        elif followed_id == follower_id:
            return render_template('userposts')
    db = get_db()
    db.execute(            
    "INSERT INTO following (follower_id, followed_id) VALUES (?, ?)",
    (follower_id, followed_id)
    )
    db.commit()
    return redirect(request.referrer)
    
#ADMIN ACTIONS

@app.route("/block/<int:id>")
def block(id):
    admin_check = query_db("SELECT userid FROM admins")
    for row in admin_check:
        if session.get('user_id') == row[0]:
            db = get_db()
            existing = query_db(
                "SELECT * FROM blacklist WHERE userid = ?",
                (id,),
                one=True
            )
            if existing:
                return redirect(url_for("admin"))
            db.execute(
                "INSERT INTO blacklist (userid) VALUES (?)",
                (id,)
            )
            db.commit()
            return redirect(url_for("admin"))

@app.route("/unfollow/<int:id>")
def unfollow(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    follower_id = session.get('user_id')
    db = get_db()
    db.execute(
        "DELETE FROM following WHERE follower_id = ? AND followed_id = ?",
        (follower_id, id)
    )
    db.commit()
    return redirect(request.referrer)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#---------------------#
#------LIVE-CHAT------#
#---------------------#

@app.route("/livechat")
def livechat():
    if "user_id" not in session:
        return redirect(url_for("login"))
    sql = """
        SELECT chat.message, chat.time, users.name
        FROM chat
        JOIN users ON chat.user_id = users.id
        ORDER BY chat.id ASC;
    """
    #
    messages = query_db(sql)

    return render_template("livechat.html", messages=messages)

@socketio.on("send_message")
def handle_send_message(data):
    #run the function when the browser sends a "send_message" event
    if "user_id" not in session:
        #if the user isn't logged in, they can't send messages
        return
    message = data.get("message", "").strip()
    #get the message text sent from javascript and remove extra spaces
    if not message:
        #if the message is empty, do nothing
        return
    userid = session["user_id"]
    username = session["username"]
    #get the logged in user's id and username from session
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #save the time when the message was sent
    db = get_db()
    #connect to the database
    db.execute(
        "INSERT INTO chat (user_id, message, time) VALUES (?, ?, ?)",
        (userid, message, time)
    )
    #insert the new chat message into the chat table
    db.commit()
    #save the new message to the database
    emit("receive_message", {
        "username": username,
        "message": message,
        "time": time
    }, broadcast=True)
    #send the new message out live to everyone currently connected to the chat
    
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)
#runs the app
