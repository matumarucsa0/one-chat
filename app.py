from flask import Flask, redirect, render_template, request, session
from flask_session import Session
import sqlite3
from flask_socketio import SocketIO, emit
from datetime import datetime
import os
import base64
import random

PATH = "C:\\Users\\admin\\OneDrive\\Počítač\\one-chat"

app = Flask(__name__)

conn = sqlite3.connect("data.db", check_same_thread=False)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, max_http_buffer_size = 1000000000)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response





@socketio.on("post--")
def handle_(data):
    attach = False
    time = datetime.now().strftime('%m/%d/%Y %H:%M')

    
    post = str(data['chat'])

    #remove &nbsp;
    
    while True:
        post = post.replace("&nbsp;", " ")

        if "&nbsp;" not in post:
            break


    #DOESNT WORK UNTIL EMOTES ARE ADDED
    #image algorithm
    i = 0
    stamps = []
    while i < (len(data['chat'])-4):
        if post[i:(i+4)] == "<img":
            z = i
            while post[z] != ">" and z < len(data['chat']):
                z += 1
            stamps.append((i, z))
            i = z
        i += 1

    print(stamps)
    i = len(stamps) - 1
    r = []

    

    while i >= 0:
        r.append(post[(stamps[i][1] + 1):])
        x = str(post[stamps[i][0]: (stamps[i][1] + 1)]).removeprefix('<img src="/static/emotes/').removesuffix('">')
        r.append(f"img--{x}")
        post = post[:stamps[i][0]]
        i -= 1
    
    if len(post) > 0:
        r.append(post)

    while "" in r:
        r.remove("")

    r.reverse()

    send = r

    r = ";,;".join(r)
    if len(r) == 0:
        r = post
        send = post

    #checking for attached images
    try:
        
        image_removed_base64 = str(data['attach']).removeprefix("data:image/png;base64,")
        image_id = str(random.randint(100000000, 999999999))

        attach_text = f'[alt--]/{image_id}/'

        imgdata = base64.b64decode(image_removed_base64)
        with open(PATH + f"\\static\\chat_images\\{image_id}.jpg", "wb") as f:
            f.write(imgdata)
        
        attach = True
    except:
        pass


    # add to post database


    #emiting the message to connected clients
    u_name = data["username"]



    if attach:
            conn.execute(f"INSERT INTO posts (post, date, username, user_id) VALUES ('{attach_text}', '{time}', '{data['username']}', {data['user_id']})")
            conn.commit()
            
            emit("massage",{'chat':"", 'user': f"{u_name} {time}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "img_id": image_id}, broadcast=True)
            if send != "":
                conn.execute(f"INSERT INTO posts (post, date, username, user_id) VALUES ('{str(r)}', '{time}', '{data['username']}', {data['user_id']})")
                conn.commit()
                emit("massage",{'chat':send, 'user': f"{u_name} {time}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic']}, broadcast=True)
            
    else:
        conn.execute(f"INSERT INTO posts (post, date, username, user_id) VALUES ('{str(r)}', '{time}', '{data['username']}', {data['user_id']})")
        conn.commit()
        emit("massage",{'chat':send, 'user': f"{u_name} {time}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic']}, broadcast=True)


@app.route("/", methods=["get", "post"])
def index():
    try:
        user_id = session["user_id"]
    except:
        return redirect("/login")

    username, profile_pic = conn.execute(f"SELECT username, profile_pic FROM users WHERE id={user_id}").fetchall()[0]
    emotes = os.listdir(PATH + "\\static\\emotes")
    messages = conn.execute("SELECT * FROM posts;").fetchall()
    if len(messages) ==0:
        return render_template("index.html",user_id = user_id, username = username,profile_pic = profile_pic, emotes = emotes)

    r = []
    # !!! LOW EFFICIENCY
    image_id = ""
    tmp = ""
    for x in messages:
        ver = False
        x = list(x)
        if tmp == "":
            pass
        else:
            date_old = tmp[1].split(" ")
            date_new = x[1].split(" ")
            
            if date_old[0] == date_new[0] and date_old[1][:5] == date_new[1][:5] and tmp[2] == x[2]: # and x[0][0:7] != "[alt--]"
                ver =True
                if r[-1]["status"] != "child":
                    r[-1]["status"] = "parent"
        
        #check if image attachment is present
        if x[0][0:7] == "[alt--]":
            image_id = x[0][8:17]
            x[0] = x[0][18:]

        tmp = x[:]

        data = {
            "message_content": x[0].split(';,;'),
            "date": x[1],
            "username": x[2],
            "user_id": x[3],
            "profile_picture": conn.execute(f"SELECT profile_pic FROM users WHERE id={x[3]}").fetchall()[0][0],
        }

        if len(image_id) > 1:
            data["image_id"] = image_id

        if ver:
            data["status"] = "child"
        else:
            data["status"] = ""
        r.append(data) 
        
        image_id = ""

    return render_template("index.html",user_id = user_id, username = username,profile_pic = profile_pic,  messages = r, emotes=emotes)

    














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

        conn.execute(f"INSERT INTO users (username, password, email, profile_pic) VALUES('{username}', '{request.form.get('password')}', '{request.form.get('email')}', 'default.png')")
        conn.commit()
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/t", methods=["GET"])
def f():

    user_data = conn.execute(f"SELECT * FROM users WHERE id={session['user_id']}").fetchall()[0]
    return render_template("profile.html", user_data = user_data)

@app.route("/profile-change", methods=["POST"])
def upload():

    user = session['user_id']
    current_profile_pic = conn.execute(f"SELECT profile_pic FROM users WHERE id={user}").fetchall()[0][0]
    
    #check if default png
    if current_profile_pic != "default.png":
        os.remove(PATH + f"\\static\\profile-pic\\{current_profile_pic}")
    # handle file
    file = request.files["file"]
    fileext = file.filename.split(".")[1]
    file.save(PATH + f"\\static\\profile-pic\\{str(session['user_id'])}.{fileext}")
    
    #change path
    conn.execute(f"UPDATE users set profile_pic='{str(session['user_id'])}.{fileext}' WHERE id={user}")
    conn.commit()

    return redirect("/")
    
if __name__ == '__main__':
    socketio.run(app, debug = True, allow_unsafe_werkzeug=True)