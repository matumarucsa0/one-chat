from flask import Flask, redirect, render_template, request, session
from flask_session import Session
import sqlite3
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import os
import base64
import random
import time

PATH = os.getcwd()


app = Flask(__name__)

conn = sqlite3.connect("data.db", check_same_thread=False)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['ENGINEIO_PAYLOAD_MAX_NUM'] = 1000
Session(app)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, max_http_buffer_size = 1000000000)
#typing status
@socketio.on("typing")
def typing(data):
    emit("is_typing", {"user": data['user'], "room": data['room'], "user_id": data['user_id']}, room=int(data['room']), broadcast=True)



def validate_room(id, rooms):
    for room in rooms:
        if int(id) == room[0]:
            return True
    return False

is_online = set()
l_time = time.time()
@socketio.on("is-online")
def online(data):
    global l_time
    global is_online
    is_online.add(data['user'])

    if l_time < time.time() - 2:
        emit("users-online", {"users_online": list(is_online)}, broadcast=True)
        l_time = time.time()
        is_online = set()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@socketio.on("onload")
def on_load(data):
    user = data['user_id']
    rooms=  conn.execute(f"SELECT id FROM chat_room WHERE users like '%{user}%'").fetchall()

    for room in rooms:
        join_room(int(room[0]))



@socketio.on("post--")
def handle_(data):
    attach = False
    time_formated = datetime.now().strftime('%m/%d/%Y %H:%M')
    room = int(data['room'])
    
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
            conn.execute(f"INSERT INTO posts (post, date, username, user_id, room, int_date) VALUES ('{attach_text}', '{time_formated}', '{data['username']}', {data['user_id']}, {room}, {time.time()})")
            conn.commit()
            
            emit("massage",{'chat':"", 'user': f"{u_name} {time_formated}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "img_src": f"/static/chat_images/{image_id}.jpg", "room": room}, room=room, broadcast=True)
            if send != "":
                conn.execute(f"INSERT INTO posts (post, date, username, user_id, int_date) VALUES ('{str(r)}', '{time_formated}', '{data['username']}', {data['user_id']}, {time.time()})")
                conn.commit()

                if not letter_ and emote:
                    emit("massage",{'chat':send, 'user': f"{u_name} {time_formated}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "only_emotes": True, "room": room}, room=room, broadcast=True)
                else:
                    emit("massage",{'chat':send, 'user': f"{u_name} {time_formated}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "only_emotes": False, "room": room}, room=room, broadcast=True)  
    elif "gif" in data:
        gif = f"[alt--]/*/*/{data['gif']}/*/*/"
        conn.execute(f"INSERT INTO posts (post, date, username, user_id, room, int_date) VALUES ('{gif}', '{time_formated}', '{data['username']}', {data['user_id']}, {room}, {time.time()})")
        conn.commit()
        emit("massage",{'chat':"", 'user': f"{u_name} {time_formated}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "img_src": data['gif'], "room": room}, room=room, broadcast=True)
    else:
        conn.execute(f"INSERT INTO posts (post, date, username, user_id, room, int_date) VALUES ('{str(r)}', '{time_formated}', '{data['username']}', {data['user_id']}, {room}, {time.time()})")
        conn.commit()
        if not letter_ and emote:
                   emit("massage",{'chat':send, 'user': f"{u_name} {time_formated}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "only_emotes": True, "room": room}, room=room, broadcast=True)
        else:
            emit("massage",{'chat':send, 'user': f"{u_name} {time_formated}", 'user_id': data['user_id'], 'profile_pic' : data['profile_pic'], "only_emotes": False, "room": room}, room=room, broadcast=True) 
        

@app.route("/users", methods=["get", "post"])
def fetch_users():
    users = conn.execute(f"SELECT id, username, profile_pic FROM users WHERE id != {session['user_id']}").fetchall()
    users_ = [list(user) for user in users]
    
    return users_


@app.route("/")
def main():
    return redirect("/room/0")


import json
@app.route("/add-chat", methods=["post"])
def add_chat():
    data = json.loads(request.data)

    #check if chat already exists
    check = set(conn.execute(f"SELECT users FROM chat_room WHERE id IN (SELECT id FROM chat_room WHERE users == {session['user_id']} AND type='direct-chat') AND type ='direct-chat' AND users!={session['user_id']}").fetchall())
    for check_id in check:
        if check_id[0] == int(data['id']):
            return {"status": "error"}
    

    chat_name_requester, chat_name_approver = conn.execute(f"SELECT username, profile_pic FROM users WHERE id={session['user_id']}").fetchall()[0], conn.execute(f"SELECT username, profile_pic FROM users WHERE id={data['id']}").fetchall()[0]
    new_id = random.randint(100000000000, 999999999999)
    conn.execute(f"INSERT INTO chat_room (id, users, name, img, type) VALUES ({new_id}, {session['user_id']}, '{chat_name_approver[0]}', '/static/profile-pic/{chat_name_approver[1]}', 'direct-chat')")
    conn.execute(f"INSERT INTO chat_room (id, users, name, img, type) VALUES ({new_id}, {data['id']}, '{chat_name_requester[0]}', '/static/profile-pic/{chat_name_requester[1]}', 'direct-chat')")
    conn.commit()
    return {"status": "ok"}
    
@app.route("/add-group", methods=['POST'])
def add_group():
    data = json.loads(request.data)['user_id_array'].split(",") + [session['user_id']]
    name = ", ".join([conn.execute(f"SELECT username FROM users WHERE id={id}").fetchall()[0][0] for id in data])

    new_id = conn.execute("SELECT id FROM chat_room ORDER BY rowid DESC LIMIT 1;").fetchall()[0][0] + 1
    for user_id in data:

        conn.execute(f"INSERT INTO chat_room (id, users, name, img, type) VALUES ({new_id}, {int(user_id)}, '{name}', '/static/setup/group.png', 'group')")
        conn.commit()
    return {}

def orderedRooms(rooms: list):
    rooms = rooms[:]
    r = []
    for room in rooms:
        last_message_date = conn.execute(f"SELECT int_date FROM posts WHERE room={room[0]} ORDER BY rowid DESC LIMIT 1").fetchall()
        if len(last_message_date) == 0:
            r.append((room, 9999))
        else:
            r.append((room, last_message_date[0][0]))
    r.sort(key=lambda x: x[1], reverse=True)
    return [room[0] for room in r]
import sys
@app.route("/room/<room>", methods=["get", "post"])
def index(room):
    try:
        user_id = session["user_id"]
    except:
        return redirect("/login")



    rooms_ = conn.execute(f"SELECT id, name, img, type FROM chat_room WHERE users LIKE '%{user_id}%'").fetchall()
    rooms = []

    if not validate_room(room, rooms_):
        return redirect("/room/0")
    
    for rrr in rooms_:
        if rrr[3] == 'direct-chat':
            rooms.append(list(rrr) + [conn.execute(f"SELECT users FROM chat_room WHERE id={rrr[0]} AND users!={session['user_id']}").fetchall()[0][0]])
        else:
            rooms.append(list(rrr))

    rooms = orderedRooms(rooms)
    room_memeber_amount = {}
    for chat in rooms:
        if chat[3] == 'group':
            n = len(conn.execute(f"SELECT type FROM chat_room WHERE id={chat[0]}").fetchall())
            room_memeber_amount[chat[0]] = n
    group = {"group": False}
    if conn.execute(f"SELECT type FROM chat_room WHERE id={room}").fetchall()[0][0] == 'group':
        group_users = conn.execute(f"SELECT id, username, profile_pic FROM users WHERE id IN (SELECT users FROM chat_room WHERE id={room})").fetchall()
        group = {"group": True, "users": group_users}
    username, profile_pic = conn.execute(f"SELECT username, profile_pic FROM users WHERE id={user_id}").fetchall()[0]
    emotes = os.listdir(PATH + "/static/emotes")
    messages = conn.execute(f"SELECT * FROM posts WHERE room={room};").fetchall()
    if len(messages) ==0:
        return render_template("index.html",user_id = user_id, username = username,profile_pic = profile_pic, emotes = emotes, room=room, rooms=rooms, group=group, group_user_amount=room_memeber_amount)

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


    return render_template("index.html",user_id = user_id, username = username,profile_pic = profile_pic,  messages = r, emotes=emotes, room = room, rooms=rooms, group=group, group_user_amount=room_memeber_amount)

    














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
            return redirect("/room/0")
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
    return redirect("/room/0")


@app.route("/register", methods=["get", "post"])
def reg():
    if request.method == "POST":

        username = request.form.get("username")
        

        conn.execute(f"INSERT INTO users (username, password, email, profile_pic, about_me, banner_color) VALUES('{username}', '{request.form.get('password')}', '{request.form.get('email')}', 'default.png', '', '#202225')")
        conn.commit()
        user_id = conn.execute(f"SELECT id FROM users WHERE username='{username}'").fetchall()[0][0]
        conn.execute(f"INSERT INTO chat_room (id, users, name, img, type) VALUES (0, {user_id}, 'main_chat', '/static/setup/group.png', 'group')")
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
        
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)#, 