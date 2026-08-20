<img src="static/images.jpg" alt="README image" width="500">

# Message

A Flask-based social platform with user accounts, posts, comments, likes, following, categories, administration tools, and real-time live chat.

## Overview

**Message** is a web-based social platform built using Python and Flask.

The application allows users to create accounts, interact with other users, create and reply to posts, comment on content, like posts, follow other users, browse posts by category, and communicate through a real-time live chat.

The project uses SQLite to store application data and Flask-SocketIO to provide real-time communication in the live chat.

## Features

### User Accounts

* User registration
* User login and logout
* Password hashing
* User sessions
* User profiles
* Profile pictures
* Email addresses associated with accounts
* Protection against duplicate usernames and email addresses

### Posts

* Create posts
* Add titles and content
* Add images to posts
* Assign posts to categories
* Reply to existing posts
* View all posts
* View posts from individual users
* View posts belonging to specific categories

### Social Features

* Follow other users
* Unfollow users
* Like posts
* Unlike posts
* Comment on posts
* View user profiles and their posts

### Live Chat

The application includes a real-time chat system using **Flask-SocketIO**.

Messages are:

* Sent without refreshing the page
* Broadcast to users currently connected to the chat
* Stored in the SQLite database
* Displayed with the sender's username and timestamp
* Limited to 100 characters in the chat input

### Administration

The application includes an administration system with features such as:

* Admin accounts
* Viewing users
* Viewing following relationships
* Managing administrators
* Blocking users
* Unblocking users
* Blacklisted users being prevented from logging in

### Error Handling

Custom error pages are included for errors such as:

* 403 Forbidden
* 404 Not Found
* 405 Method Not Allowed
* 505 HTTP Version Not Supported

## Technologies Used

| Technology         | Purpose                               |
| ------------------ | ------------------------------------- |
| **Python**         | Main programming language             |
| **Flask**          | Web application framework             |
| **SQLite**         | Database                              |
| **Flask-SocketIO** | Real-time live chat                   |
| **Werkzeug**       | Password hashing                      |
| **HTML**           | Page structure                        |
| **CSS**            | Styling and layout                    |
| **JavaScript**     | Client-side interaction and live chat |

## Project Structure

```text
message/
├── app.py
├── database.db
├── requirements.txt
├── README.md
├── templates/
│   ├── admin.html
│   ├── allposts.html
│   ├── category.html
│   ├── error.html
│   ├── home.html
│   ├── layout.html
│   ├── livechat.html
│   ├── login.html
│   ├── newpost.html
│   ├── register.html
│   └── userposts.html
└── static/
    ├── conversation.png
    └── style.css
```

### `app.py`

Contains the main Flask application, routes, database queries, authentication, post functionality, social features, administration functionality and live chat functionality.

### `database.db`

The SQLite database used to store information such as users, posts, comments, likes, following relationships, administrators, blacklisted users, categories and chat messages.

### `templates/`

Contains the HTML templates used to display the different pages of the application.

### `static/`

Contains static resources such as the website stylesheet and images.

### `requirements.txt`

Contains the Python dependencies required to run the application.

## How It Works

The application runs as a Flask web server.

When a user interacts with the website, their browser sends a request to the Flask application. Flask processes the request and either retrieves information from the database, modifies the database, or displays the appropriate template.

For example, when a user creates a post:

1. The user fills in the new post form.
2. Flask receives the submitted information.
3. The application gets the user's ID from their session.
4. The post information is inserted into the SQLite database.
5. The database changes are committed.
6. The user is redirected back to the home page.
7. The new post can then be displayed with the other posts.

## Database

The application uses **SQLite** for persistent data storage.

The database is used for several parts of the application, including:

* Users
* Posts
* Comments
* Likes
* Categories
* Following relationships
* Administrators
* Blacklisted users
* Live chat messages

SQL queries are used to retrieve and modify the stored information.

Where user-provided values are inserted into SQL queries, parameterised queries are used to reduce the risk of SQL injection.

## Authentication

User passwords are not stored as plain text.

When a user registers, their password is processed using Werkzeug's password hashing functionality before being stored in the database.

When logging in, the entered password is checked against the stored password hash.

User sessions are then used to keep track of the currently logged-in user.

## Real-Time Chat

The live chat uses **Flask-SocketIO** to allow messages to be sent and received without requiring the page to reload.

When a user sends a message:

1. JavaScript sends the message to the Socket.IO server.
2. Flask receives the message.
3. The message is saved to the database.
4. The server broadcasts the message to connected users.
5. The connected browsers display the new message.

This allows the chat to behave in real time.

## Installation

### Requirements

You will need:

* Python 3
* pip

### 1. Clone the repository

```bash
git clone https://github.com/MooseZ690/message.git
cd message
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

The application will start using Flask-SocketIO.

Open the local address shown by the application in a web browser.

## Development

The project was developed iteratively, with functionality being added and improved throughout development.

The Git repository contains the development history of the project through multiple commits.

The application has been developed as a larger project rather than a single simple program, with separate HTML templates, static resources, database functionality and server-side Python code.

## Security Considerations

The application includes several security-related features, including password hashing, login sessions, authentication checks and parameterised database queries.

However, this project is primarily a development/learning project and should not be considered production-ready without further security testing and improvements.

For example, sensitive configuration such as the Flask secret key should be stored outside the source code rather than being hard-coded.

## Future Improvements

Possible future improvements include:

* Moving sensitive configuration into environment variables
* Improving the security of administrative routes
* Adding more comprehensive input validation
* Improving error handling
* Adding automated tests
* Separating the Flask application into multiple Python modules
* Improving the user interface
* Adding more real-time features
* Adding notifications for new activity
* Improving database structure and efficiency
* Adding more advanced moderation tools

## Purpose

This project was developed to demonstrate practical programming and web-development skills, including:

* Python programming
* Flask web development
* Database management
* SQL
* User authentication
* Password hashing
* Session management
* HTML and CSS
* JavaScript
* Real-time communication
* Debugging and problem solving
* Software development and iteration

## Author

**MooseZ690**

GitHub: https://github.com/MooseZ690
