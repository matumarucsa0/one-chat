from flask import Flask, redirect, render_template, request, session
from flask_session import Session
import sqlite3
from flask_socketio import SocketIO, emit
from datetime import datetime


app = Flask(__name__)

conn = sqlite3.connect("data.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response





@socketio.on("post--")
def handle_(data):
    time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')

    conn.execute(f"INSERT INTO posts (post, date, username, user_id) VALUES ('{data['chat']}', '{time}', '{data['username']}', {data['user_id']})")
    conn.commit()
    u_name = data["username"]
    emit("massage",{'chat':data['chat'], 'user': f"{u_name} - {time}"}, broadcast=True)


@app.route("/", methods=["get", "post"])
def index():
    try:
        user_id = session["user_id"]
        username = conn.execute(f"SELECT username FROM users WHERE id={user_id}").fetchall()[0][0]
        messages = conn.execute("SELECT * FROM posts;").fetchall()
        print(messages) 
        return render_template("index.html",user_id = user_id, username = username, messages = messages)

    except:
        return redirect("/login")














################
# LOGIN SYSTEM #
################

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any
    #  user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        
        username = request.form.get("username")
        password = request.form.get("password")
        # Query database for username\
        try:
            r = conn.execute(f"SELECT * FROM users WHERE username = '{username}'").fetchall()[0] # (id integer primary key, username, password, email)
        except:
            print("Incorect username or password")
            return render_template("login.html", error="Incorect username or password")
        if str(r[2]) == str(password):

        # Remember which user has logged in
            session["user_id"] = r[0]
            return redirect("/")
        else:
            print("Incorect username or password")
            return render_template("login.html", error="Incorect username or password")
            
        # Redirect user to home page
            
        

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["get", "post"])
def reg():
    if request.method == "POST":
        username = request.form.get("username")
        x = conn.execute(f"SELECT * FROM users WHERE username = '{username}';").fetchall()
        x.append(0)

        y = conn.execute(f"SELECT * FROM users WHERE email = '{request.form.get('email')}'").fetchall()
        y.append(0)

        if len(x) >= 2:
            return render_template("register.html", error = "This username is already used")

        elif len(request.form.get("password")) ==0:
            return render_template("register.html", error = "Not log enough")
        elif len(y) >= 2:
            return render_template("register.html", error = "This email is already used")

        conn.execute(f"INSERT INTO users (username, password, email) VALUES('{username}', '{request.form.get('password')}', '{request.form.get('email')}')")
        conn.commit()
        return redirect("/login")
    else:
        return render_template("register.html")


    
if __name__ == '__main__':
    socketio.run(app)