from flask import Flask, render_template, request, jsonify, json, redirect, url_for, session
from flask_cors import CORS, cross_origin
from markupsafe import escape
from models import db, User
from datetime import datetime as date
from passlib.hash import sha256_crypt
from auth import auth as auth_blueprint
from main import main as main_blueprint
from err import err as err_blueprint
from matched import matched as matched_blueprint, safe_message
from profile import profile as profile_blueprint
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO, join_room, emit, leave_room


app = Flask(__name__, template_folder=r"C:\Users\svacek\PycharmProjects\flask_test\templates",
            static_folder=r"C:\Users\svacek\PycharmProjects\flask_test\static")
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = db.get_by_id(user_id)
    if isinstance(user, User):
        return user
    return None

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)
app.register_blueprint(matched_blueprint)
app.register_blueprint(profile_blueprint)
app.register_blueprint(err_blueprint)
socket = SocketIO(app)

CORS(app)

@socket.on("create")
def begin_chat(room):
    join_room(room)


@socket.on("leave")
def stop_chat(room):
    leave_room(room)


@socket.on("message")
def handle_message(message_data):
    safe_message(message_data)

if __name__ == '__main__':
    socket.run(app, debug=True)
