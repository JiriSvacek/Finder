from flask import Flask
from flask_cors import CORS
from models import db, User
from auth import auth as auth_blueprint
from main import main as main_blueprint
from err import err as err_blueprint
from matched import matched as matched_blueprint, safe_message
from profile import profile as profile_blueprint
from flask_login import LoginManager
from flask_socketio import SocketIO, join_room, leave_room


app = Flask(__name__)
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
socket = SocketIO(app, allow_upgrades=False)

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
