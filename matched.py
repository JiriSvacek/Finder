import json
from types import NoneType
from datetime import datetime as date
from flask import Blueprint, render_template, session, request, url_for
from flask_login import login_required
from flask_socketio import emit

from models import db

matched = Blueprint('matched', __name__)


def shorten_message(message: str) -> str:
    if len(message) > 8:
        return message[:8] + "..."
    return message


def join_user_and_last_message(users: list, last_messages: list) -> list:
    """Merges to list of other users last messages"""
    joined_data = list()
    for user in users:
        found_match = False
        #Searching in list of last messages for assignment to the correct other user
        for index, message in enumerate(last_messages):
            if user["key"] == message["from_user"] or user["key"] == message["to_user"]:
                message["body"] = shorten_message(message.get("body"))
                user.update(message)
                joined_data.append(user)
                last_messages.pop(index)
                found_match = True
                break
        if not found_match:
            user["from_user"] = None
            user["to_user"] = None
            joined_data.append(user)
    return joined_data


@matched.route('/matched_page')
@login_required
def matched_page():
    """Return matched page with matched users and last message which was sent between"""
    db_response_users = db.get_matched(session["user"]["key"])
    if isinstance(db_response_users, list):
        db_response_last_messages = db.get_last_messages(session["user"]["key"])
        if isinstance(db_response_last_messages, list):
            session["matched"] = join_user_and_last_message(db_response_users, db_response_last_messages)
            return render_template('matched.html')
        return db_response_last_messages
    elif isinstance(db_response_users, NoneType):
        session["matched"] = db_response_users
        return render_template('matched.html')
    return db_response_users


@matched.route("/get_chat_history")
def chat_history():
    db_response = db.get_chat_history(session["user"]["key"], request.headers.get("Other-User"))
    if isinstance(db_response, list):
        return json.dumps(db_response)
    return db_response


def get_users_from_room_id(room_id: str):
    first_key, second_key = room_id.split("-")
    return int(first_key), int(second_key)


def safe_message(message_data: list):
    """Saves message to DB after that emits to the other user or if saving failed redirects to other page """
    chat_users = get_users_from_room_id(message_data[1])
    if chat_users[0] == session["user"]["key"]:
        db_response = db.insert_message(chat_users[0], chat_users[1], date.now(), message_data[0])
    elif chat_users[1] == session["user"]["key"]:
        db_response = db.insert_message(chat_users[1], chat_users[0], date.now(), message_data[0])
    else:
        session["error"] = "Users in messages were not distinguish"
        redirect_data = {"url": url_for("auth.error"), "id": session["user"]["key"]}
        return emit("redirect", redirect_data, room=message_data[1])
    if isinstance(db_response, int) and db_response == 1:
        return emit("message", message_data, room=message_data[1], skip_sid=request.sid)
    redirect_data = {"url": url_for("err.error"), "id": session["user"]["key"], "sess": session["error"]}
    return emit("redirect", redirect_data, room=message_data[1])
