from flask import Flask, redirect, render_template, request, session
from flask_session import Session
import sqlite3
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import os
import base64
import random
import time
import json
import sys
import re


PATH = os.getcwd()

app = Flask(__name__)

conn = sqlite3.connect("data.db", check_same_thread=False)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["ENGINEIO_PAYLOAD_MAX_NUM"] = 1000
Session(app)

app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, max_http_buffer_size=1000000000)


# typing status
@socketio.on("typing")
def typing(data):
    """
        Reidrects the is typing status to connected clients
    """
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
    is_online.add(data["user"])

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
    """
        After user joins and sends a scoket message it will go over the rooms in which he is and connects him so that he will recieve the messages
    """
    user = data['user_id']
    rooms=  conn.execute(f"SELECT id FROM chat_room WHERE users like '%{user}%'").fetchall()

    for room in rooms:
        join_room(int(room[0]))



def replace_html_space(message: str):
    """
        Input: str message Output: str messae with replaced '&nbsp;' => ' '
    """
    while "&nbsp;" in message:
        message = message.replace("&nbsp;", " ")

    return message
        
def get_emote_data_message(message: str):
    """
        returns message parsed for emotes in the following format:
            "hey <img src='EMOTE_NAME'> how you doin <img> <img>" => "hey you doin ;,;img--EMOTE-NAME;,; ;,;img--EMOTE-NAME"
        and if the message contains only emotes and no text
            only_emotes: bool

    
    """
    message_default = message[:]
    #go over the string and record the indexes of start and end of the img element
    i = 0
    stamps = []
    while i < (len(message_default) - 4):
        if message[i : (i + 4)] == "<img":
            z = i
            while message[z] != ">" and z < len(message_default):
                z += 1
            stamps.append((i, z))
            i = z
        i += 1

    #if emote in message set only emotes to true
    only_emotes = bool(len(stamps))

    #take out the emotes based on the index stamps
    """
    loops from the back and adds the text and than the emote 
    "hello <img src='/1.jpg'> lol" => [" lol", "img--/1.jpg", "hello "]
    """
    i = len(stamps) - 1
    message_list = []
    while i >= 0:
        message_list.append(message[(stamps[i][1] + 1):]) # text without emote

        #check if the message contains text if there wasnt text found yet
        if only_emotes:
            for letter in message[(stamps[i][1] + 1):]:
                if letter != " " and letter != "":
                    only_emotes = False
                    break

        src = str(message[stamps[i][0]: (stamps[i][1] + 1)]).removeprefix('<img src="/static/emotes').removesuffix('">')
        message_list.append(f"img--{src}")
        message = message[:stamps[i][0]] # rest of the message
        i -= 1

    if len(message) > 0:
        message_list.append(message)

    message_list.reverse()

    #convert to storing format
    message = ";,;".join(message_list)
    if len(message) == 0:
        message = message_default

    return message.strip(), only_emotes

def handle_attachment(path, attachment):
    
    image_removed_base64 = str(attachment).removeprefix("data:image/png;base64,")
    image_id = str(random.randint(100000000, 999999999))


    imgdata = base64.b64decode(image_removed_base64)
    with open(path + f"/static/chat_images/{image_id}.jpg", "wb") as f:
        f.write(imgdata)

    return f"/static/chat_images/{image_id}.jpg"

def process_message(user_id, username, message, formated_time, profile_pic, room, only_emotes, attach_source=None):

    if attach_source != None:
        attach_message = f"[alt--]/*/*/{attach_source}/*/*/"

        #attach
        conn.execute(f"INSERT INTO posts (post, date, username, user_id, room, int_date) VALUES ('{attach_message}', '{formated_time}', '{username}', {user_id}, {room}, {time.time()})")
        emit("massage",{'chat':"", 'user': f"{username} {formated_time}", 'user_id': user_id, 'profile_pic' : profile_pic, "room": room, "img_src": attach_source}, room=room, broadcast=True)
        conn.commit()

    if len(message) > 0:
        conn.execute(f"INSERT INTO posts (post, date, username, user_id, room, int_date) VALUES ('{message}', '{formated_time}', '{username}', {user_id}, {room}, {time.time()})")
        conn.commit()
        message = message.split(';,;')
        emit("massage",{'chat':message, 'user': f"{username} {formated_time}", 'user_id': user_id, 'profile_pic' : profile_pic, "only_emotes": only_emotes, "room": room}, room=room, broadcast=True)

@socketio.on("post--")
def handle_(data):
    time_formated = datetime.now().strftime('%m/%d/%Y %H:%M')
    room = int(data['room'])
    post = str(data["chat"])
    attach_source = None

    #FORMAT MESSAGE
    # remove &nbsp;
    post = replace_html_space(post)

    #get emotes
    post, only_emotes = get_emote_data_message(post) # => parsed_message: str, only_emotes_status: bool

    # checking for attached images
    if "attach" in data:
        attach_source = handle_attachment(PATH, data['attach'])

    if "gif" in data:
        attach_source = data['gif']
    # emiting the message to connected clients
    process_message(data['user_id'], data['username'], post, time_formated, data['profile_pic'], room, only_emotes, attach_source)


@app.route("/users", methods=["get", "post"])
def fetch_users():
    users = conn.execute(f"SELECT id, username, profile_pic FROM users WHERE id != {session['user_id']}").fetchall()
    users_ = [list(user) for user in users]

    return users_


@app.route("/")
def main():
    return redirect("/room/0")


@app.route("/add-chat", methods=["post"])
def add_chat():
    data = json.loads(request.data)

    #check if chat already exists
    check = set(conn.execute(f"SELECT users FROM chat_room WHERE id IN (SELECT id FROM chat_room WHERE users == {session['user_id']} AND type='direct-chat') AND type ='direct-chat' AND users!={session['user_id']}").fetchall())
    for check_id in check:
        if check_id[0] == int(data["id"]):
            return {"status": "error"}

    chat_name_requester, chat_name_approver = conn.execute(f"SELECT username, profile_pic FROM users WHERE id={session['user_id']}").fetchall()[0], conn.execute(f"SELECT username, profile_pic FROM users WHERE id={data['id']}").fetchall()[0]
    new_id = random.randint(100000000000, 999999999999)
    conn.execute(f"INSERT INTO chat_room (id, users, name, img, type) VALUES ({new_id}, {session['user_id']}, '{chat_name_approver[0]}', '/static/profile-pic/{chat_name_approver[1]}', 'direct-chat')")
    conn.execute(f"INSERT INTO chat_room (id, users, name, img, type) VALUES ({new_id}, {data['id']}, '{chat_name_requester[0]}', '/static/profile-pic/{chat_name_requester[1]}', 'direct-chat')")
    conn.commit()
    return {"status": "ok"}


@app.route("/add-group", methods=["POST"])
def add_group():
    data = json.loads(request.data)['user_id_array'].split(",") + [session['user_id']]
    name = ", ".join([conn.execute(f"SELECT username FROM users WHERE id={id}").fetchall()[0][0] for id in data])

    new_id = conn.execute("SELECT id FROM chat_room ORDER BY rowid DESC LIMIT 1;").fetchall()[0][0] + 1
    for user_id in data:

        conn.execute(f"INSERT INTO chat_room (id, users, name, img, type) VALUES ({new_id}, {int(user_id)}, '{name}', '/static/setup/group.png', 'group')")
        conn.commit()
    return {}


def ordered_rooms(rooms: list):
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


@app.route("/room/<room>", methods=["get", "post"])
def index(room):
    try:
        user_id = session["user_id"]
    except:
        return redirect("/login")

    room = int(room)
    unread_messages = conn.execute(f"SELECT room, amount FROM unread_messages WHERE user_id={user_id}").fetchall()
    for unread_message in unread_messages:
        if int(unread_message[0]) == room:
            conn.execute(f"DELETE FROM unread_messages WHERE user_id={user_id} AND room={room}")
            conn.commit()
            unread_messages.remove(unread_message)

    rooms_ = conn.execute(f"SELECT id, name, img, type FROM chat_room WHERE users LIKE '%{user_id}%'").fetchall()
    rooms = []

    if not validate_room(room, rooms_):
        return redirect("/room/0")

    for rrr in rooms_:
        if rrr[3] == 'direct-chat':
            rooms.append(list(rrr) + [conn.execute(f"SELECT users FROM chat_room WHERE id={rrr[0]} AND users!={session['user_id']}").fetchall()[0][0]])
        else:
            rooms.append(list(rrr))

    rooms = ordered_rooms(rooms)
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
        return render_template("index.html",user_id = user_id, username = username,profile_pic = profile_pic, emotes = emotes, room=room, rooms=rooms, group=group, group_user_amount=room_memeber_amount, unread_messages=unread_messages)

    r = []
    # !!! LOW EFFICIENCY
    image_src = ""
    tmp = ""
    for x in messages:
        if x[0][:9] == '[admin--]':
            img__ = x[0].split("/*/*/")[1]
            message = x[0].split("/*/*/")[2]
            admin_message = {
                'type': 'admin',
                'img': img__,
                'content': message
            }
            r.append(admin_message)
        else:
            ver = False
            x = list(x)
            if tmp != "":
                date_old = tmp[1].split(" ")
                date_new = x[1].split(" ")

                if date_old[0] == date_new[0] and date_old[1][:5] == date_new[1][:5] and tmp[2] == x[2]: # and x[0][0:7] != "[alt--]"
                    ver =True                       
                    if r[-1]["status"] != "child":
                        r[-1]["status"] = "parent"

            # check if image attachment is present
            if x[0][0:7] == "[alt--]":
                alt, src, text = x[0][:].split("/*/*/")
                image_src = src
                x[0] = text

            tmp = x[:]

            message_content = x[0].split(";,;")

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
                "type": "default"
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

    
    return render_template("index.html",user_id = user_id, username = username,profile_pic = profile_pic,  messages = r, emotes=emotes, room = room, rooms=rooms, group=group, group_user_amount=room_memeber_amount, unread_messages=unread_messages)


@app.route("/change-group-name", methods=["POST"])
def change_group_name():
    json_data = json.loads(request.data)
    newName = replace_html_space(json_data['newName']) 
    
    conn.execute(f"UPDATE chat_room SET name='{newName}' WHERE id={int(json_data['room'])}")
    conn.commit()

    message = f"{json_data['username']} changed the channel name: {json_data['originalName']} => {newName}"
    admin_message(message, int(json_data["room"]), "/static/setup/edit2.svg")

    return 1


def admin_message(message, room, image="none"):
    post = f"[admin--]/*/*/{image}/*/*/{message}"
    time_formated = datetime.now().strftime("%m/%d/%Y %H:%M")

    conn.execute(f"INSERT INTO posts (post, date, username, user_id, room, int_date) VALUES('{post}', '{time_formated}', 'admin', '6969696', {room}, {time.time()}) ")
    conn.commit()


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
        data = json.loads(request.data)

        username = data['username']
        password = data['password']
        # Query database for username\
        
        try:
            r = conn.execute(f"SELECT * FROM users WHERE username = '{username}'").fetchall()[0] # (id integer primary key, username, password, email)
        except:
            return {"status": "invalid"}
        if str(r[2]) == str(password):
            # Remember which user has logged in
            session["user_id"] = r[0]
            return {"status": "valid"}
        else:
            return {"status": "invalid"}

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html",error=False)



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
        data = json.loads(request.data)
        username = data['username']
        email = data['email']
        password = data['password']

        invalid = False
        
        status = {
            "username": True,
            "email": True,
            "password": True 
        }

        username_status = validate_username(username)
        if type(username_status) == str:
            status['username'] = username_status
            invalid = True

        email_status = validate_email(email)
        if type(email_status) == str:
            status['email'] = email_status
            invalid = True

        password_stauts = validate_password(password)
        if type(password_stauts) == str:
            status['password'] = password_stauts
            invalid = True

        if not invalid:
            conn.execute(f"INSERT INTO users (username, password, email, profile_pic, about_me, banner_color) VALUES('{username}', '{password}', '{email}', 'default.png', '', '#202225')")
            conn.commit()
            user_id = conn.execute(f"SELECT id FROM users WHERE username='{username}'").fetchall()[0][0]
            conn.execute(f"INSERT INTO chat_room (id, users, name, img, type) VALUES (0, {user_id}, 'main_chat', '/static/setup/group.png', 'group')")
            
        return status
    else:
        return render_template("register.html")

def validate_username(username: str):
    username = username.strip()

    if len(username) < 3 or len(username) > 16:
        return "Must be between 3 and 16 in length"

    
    #exists check
    existing_user = conn.execute(f"SELECT * FROM users WHERE username='{username}'").fetchall()
    if len(existing_user) > 0:
        return "This username is already being used"
    
    return True

def validate_email(email: str):
    if not re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email):
        return "incorrect format"
    return True

def validate_password(password: str):
    if len(password) < 8:
        return "The password is too short"
    
    if not re.search(r'[A-Z]', password) and not re.search(r'[a-z]', password):
        return "The password must contain a letter"

    # Check for at least one digit
    if not re.search(r'\d', password):
        return "The password must contain a digit"
    
    return True
        

@app.route("/t", methods=["GET"])
def f():
    user_data = conn.execute(f"SELECT * FROM users WHERE id={session['user_id']}").fetchall()[0]  # (id integer primary key, username, password, email, profile_pic, about_me, banner_color)
    return render_template("profile.html", user_data=user_data)


@app.route("/profile-change", methods=["POST"])
def upload():
    user_id = session["user_id"]

    file_name = request.files["file"].filename.strip()
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

#read messages
@app.route("/unread-messages-update", methods=["POST"])
def unread_messages():
    data = json.loads(request.data)
    user_id = data['user_id']
    recieving_room = data['recieving_room']

    number_of_unread_messages = conn.execute(f"SELECT amount FROM unread_messages WHERE user_id={user_id} AND room={recieving_room}").fetchall()

    if len(number_of_unread_messages) == 0:
        number_of_unread_messages = 1
        conn.execute(f"INSERT INTO unread_messages (user_id, room, amount) VALUES ({user_id}, {recieving_room}, 1)")
        conn.commit()
    else:
        number_of_unread_messages = number_of_unread_messages[0][0] + 1
        conn.execute(f"UPDATE unread_messages SET amount={number_of_unread_messages} WHERE user_id={user_id} AND room={recieving_room}")
        conn.commit()

    response = {
        "user_id": user_id,
        "recieving_room": recieving_room,
        "amount": number_of_unread_messages
    }
    return response

if __name__ == '__main__':
    try:
        socketio.run(app, debug=True)
    except RuntimeError:
        socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
