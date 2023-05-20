from flask import Flask, redirect, render_template, request, session
from flask_session import Session
import sqlite3
from flask_socketio import SocketIO, emit
from datetime import datetime
import os
import base64
import random

PATH = os.getcwd()

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
        x = str(post[stamps[i][0]: (stamps[i][1] + 1)]).removeprefix('<img src="/static/emotes').removesuffix('">')
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

        attach_text = f'[alt--]/*/*//static/chat_images/{image_id}.jpg/*/*/'

        imgdata = base64.b64decode(image_removed_base64)
        with open(PATH + f"/static/chat_images/{image_id}.jpg", "wb") as f:
            f.write(imgdata)
        
        attach = True
    except:
        pass


    # add to post database

    #chesk if only emotes
    letter_ = False
    emote = False
    for cont in send:
        if "img--" in cont:
            emote = True
        else:
            for letter in cont:
                if letter != " " and letter != "":
                    letter_ = True

    if not letter_ and emote:
            data["only-emote"] = "yes"

    #emiting the message to connected clients
    u_name = data["username"]



    if attach:
            conn.execute(f"INSERT INTO posts (post, date, username, user_id) VALUES ('{attach_text}', '{time}', '{data['username']}', {data['user_id']})")
            conn.commit()
            
            emit("massage",{'chat':"", 'user': f"{u_name} {time}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "img_src": f"/static/chat_images/{image_id}.jpg"}, broadcast=True)
            if send != "":
                conn.execute(f"INSERT INTO posts (post, date, username, user_id) VALUES ('{str(r)}', '{time}', '{data['username']}', {data['user_id']})")
                conn.commit()

                if not letter_ and emote:
                    emit("massage",{'chat':send, 'user': f"{u_name} {time}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "only_emotes": True}, broadcast=True)
                else:
                    emit("massage",{'chat':send, 'user': f"{u_name} {time}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "only_emotes": False}, broadcast=True)  
    elif "gif" in data:
        gif = f"[alt--]/*/*/{data['gif']}/*/*/"
        conn.execute(f"INSERT INTO posts (post, date, username, user_id) VALUES ('{gif}', '{time}', '{data['username']}', {data['user_id']})")
        conn.commit()
        emit("massage",{'chat':"", 'user': f"{u_name} {time}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "img_src": data['gif']}, broadcast=True)
    else:
        conn.execute(f"INSERT INTO posts (post, date, username, user_id) VALUES ('{str(r)}', '{time}', '{data['username']}', {data['user_id']})")
        conn.commit()
        if not letter_ and emote:
                   emit("massage",{'chat':send, 'user': f"{u_name} {time}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "only_emotes": True}, broadcast=True)
        else:
            emit("massage",{'chat':send, 'user': f"{u_name} {time}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "only_emotes": False}, broadcast=True) 
        


@app.route("/", methods=["get", "post"])
def index():
    try:
        user_id = session["user_id"]
    except:
        return redirect("/login")

    username, profile_pic = conn.execute(f"SELECT username, profile_pic FROM users WHERE id={user_id}").fetchall()[0]
    emotes = os.listdir(PATH + "/static/emotes")
    messages = conn.execute("SELECT * FROM posts;").fetchall()
    if len(messages) ==0:
        return render_template("index.html",user_id = user_id, username = username,profile_pic = profile_pic, emotes = emotes)

    r = []
    # !!! LOW EFFICIENCY
    image_src = ""
    tmp = ""
    for x in messages:
        ver = False
        x = list(x)
        if tmp != "":
            date_old = tmp[1].split(" ")
            date_new = x[1].split(" ")
            
            if date_old[0] == date_new[0] and date_old[1][:5] == date_new[1][:5] and tmp[2] == x[2]: # and x[0][0:7] != "[alt--]"
                ver =True
                if r[-1]["status"] != "child":
                    r[-1]["status"] = "parent"
        
        #check if image attachment is present
        if x[0][0:7] == "[alt--]":
            alt, src, text = x[0][:].split("/*/*/")
            image_src = src
            x[0] = text

        tmp = x[:]


        message_content = x[0].split(';,;')


        letter_ = False
        emote = False
        for cont in message_content:
            if "img--" in cont:
                emote = True
            else:
                for letter in cont:
                    if letter != " " and letter != "":
                        letter_ = True

        
        data = {
            "message_content": message_content,
            "date": x[1],
            "username": x[2],
            "user_id": x[3],
            "profile_picture": conn.execute(f"SELECT profile_pic FROM users WHERE id={x[3]}").fetchall()[0][0],
        }

        if not letter_ and emote:
            data["only-emote"] = "yes"

        if len(image_src) > 1:
            data["image_src"] = image_src

        if ver:
            data["status"] = "child"
        else:
            data["status"] = ""
        r.append(data) 
        
        image_src = ""

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
        

        conn.execute(f"INSERT INTO users (username, password, email, profile_pic, about_me, banner_color) VALUES('{username}', '{request.form.get('password')}', '{request.form.get('email')}', 'default.png', '', '#202225')")
        conn.commit()
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/t", methods=["GET"])
def f():

    user_data = conn.execute(f"SELECT * FROM users WHERE id={session['user_id']}").fetchall()[0] # (id integer primary key, username, password, email, profile_pic, about_me, banner_color)
    return render_template("profile.html", user_data = user_data)

@app.route("/profile-change", methods=["POST"])
def upload():

    user_id = session["user_id"]

    file_name  = request.files["file"].filename.strip()
    if file_name != "":
        current_profile_pic = conn.execute(f"SELECT profile_pic FROM users WHERE id={user_id}").fetchall()[0][0]
        if current_profile_pic != "default.png":
            os.remove(PATH + f"/static/profile-pic/{current_profile_pic}")

        file = request.files["file"]
        fileext = file.filename.split(".")[1]
        file.save(PATH + f"/static/profile-pic/{str(session['user_id'])}.{fileext}")

        #change path
        conn.execute(f"UPDATE users set profile_pic='{str(session['user_id'])}.{fileext}' WHERE id={user_id}")
        conn.commit()

    
    about_me = request.form.get("about-me")
    banner_color = request.form.get("color")
    conn.execute(f"UPDATE users SET about_me='{about_me}', banner_color='{banner_color}' WHERE id={user_id}")
    conn.commit()

    return redirect("/t")

@app.route("/user_profile/<id>")
def user_data(id):
    data = conn.execute(f"SELECT username, profile_pic, about_me, banner_color FROM users WHERE id={id}").fetchall()[0]
    data_j = {
        "username": data[0],
        "profile_pic": data[1],
        "about_me": data[2],
        "banner_color": data[3]
    }
    return data_j

if __name__ == '__main__':
        
        socketio.run(app, debug=True)#, allow_unsafe_werkzeug=True