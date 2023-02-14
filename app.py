from flask import Flask, redirect, render_template, request, session
from flask_session import Session
import sqlite3
from flask_socketio import SocketIO, emit
from datetime import datetime
import os
import base64
import random



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
    time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')

    
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
        x = str(post[stamps[i][0]: (stamps[i][1] + 1)]).removeprefix('<img src="').removesuffix('">')
        r.append(f"img--{x}")
        post = post[:stamps[i][0]]
        i -= 1
    
    while "" in r:
        r.remove("")

    r.reverse()
    r = ";,;".join(r)
    if len(r) == 0:
        r = post

    #checking for attached images
    try:
        
        image_removed_base64 = str(data['attach']).removeprefix("data:image/png;base64,")
        image_id = str(random.randint(100000000, 999999999))

        r = f'[alt--]/{image_id}/' + r

        imgdata = base64.b64decode(image_removed_base64)
        with open(f"C:\\Users\\Matus\\Desktop\\one-chat\\static\\chat_images\\{image_id}.jpg", "wb") as f:
            f.write(imgdata)
    except:
        pass


    # add to post database
    conn.execute(f"INSERT INTO posts (post, date, username, user_id) VALUES ('{str(r)}', '{time}', '{data['username']}', {data['user_id']})")
    conn.commit()

    #emiting the message to connected clients
    u_name = data["username"]
    emit("massage",{'chat':data['chat'], 'user': f"{u_name} - {time}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic']}, broadcast=True)


@app.route("/", methods=["get", "post"])
def index():
    try:
        user_id = session["user_id"]
        username, profile_pic = conn.execute(f"SELECT username, profile_pic FROM users WHERE id={user_id}").fetchall()[0]
        
        messages = conn.execute("SELECT * FROM posts;").fetchall()
        
        r = []
        # !!! LOW EFFICIENCY
        image_id = ""
        for x in messages:
            x = list(x)
            #check if image attachment is present
            if x[0][0:7] == "[alt--]":
                image_id = x[0][8:17]
                x[0] = x[0][18:]
            x[0] = x[0].split(';,;') #splits message for emotes
            z = x + [conn.execute(f"SELECT profile_pic FROM users WHERE id={x[3]}").fetchall()[0][0]] #adds profile picture
            
            if len(image_id) > 1:
                z.append(image_id)
            
            r.append(z) #adds to list ready to be sent
            #normal len = 5 special len 6
            image_id = ""
            

        
        return render_template("index.html",user_id = user_id, username = username,profile_pic = profile_pic,  messages = r)

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
        os.remove(f"C:\\Users\\Matus\\Desktop\\one-chat\\static\\profile-pic\\{current_profile_pic}")
    # handle file
    file = request.files["file"]
    fileext = file.filename.split(".")[1]
    file.save(f"C:\\Users\\Matus\\Desktop\\one-chat\\static\\profile-pic\\{str(session['user_id'])}.{fileext}")
    
    #change path
    conn.execute(f"UPDATE users set profile_pic='{str(session['user_id'])}.{fileext}' WHERE id={user}")
    conn.commit()

    return redirect("/")
    
if __name__ == '__main__':
    socketio.run(app, debug = True)