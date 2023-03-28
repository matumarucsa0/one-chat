# Live chat app
#### Video demo: https://youtu.be/ojD2EIe8ai8
#### Description:

The Flask SocketIO chat app is a real-time chat application that allows multiple users to communicate in a single chat room. The application is built using vanilla HTML, CSS, and JavaScript, and utilizes SQLite as its database.

Users can join the chat room by creating an account or signing in with their existing credentials. Once logged in, users can send live messages, share photos, and use emotes to express themselves. If an emote is sent as a standalone message, it is displayed in a larger size.

The app has a feature that, if a allows users sends multiple messages in a short period of time without being interrupted by another user, each message will be displayed without a profile picture, time stamp, and other details but is instead displayed one after another to create a streamlined conversation experience.

Users can customize their profile by adding a profile picture, a banner, and an "About Me" description. This allows users to showcase their personality and interests to other members of the chat room.

The app is built on Flask, a micro web framework in Python, and SocketIO, a library for real-time, event-based communication between the server and the client. The use of Flask and SocketIO allows for efficient, high-performance communication between the client and server.