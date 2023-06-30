from flask import Blueprint, session, redirect, url_for, jsonify, render_template
from flask_login import login_required
from models import db, User

profile = Blueprint('profile', __name__)


@profile.route('/profile')
@login_required
def profiles_page():
    return render_template("profile.html", name=session["user"]["name"])


@profile.route('/available', methods=['GET'])
@login_required
def available():
    """Return possible user which is fulfilling the properties (location, age, gender) """
    db_response = get_available_user()
    if isinstance(db_response, User):
        session["availableUserKey"] = db_response.get_id()
        return db_response.get_card_info()
    msg = "No possible matches"
    if db_response == msg:
        return jsonify({'missing_values': msg})
    return db_response


def length_of_list(data: list) -> str or list[str] or None:
    """Depending on the condition of the inputted list, function will return str, list, None"""
    if len(data) == 0:
        return None
    elif len(data) == 1:
        return data[0]
    return data


def check_if_strings(values: (list, tuple)) -> str or list or None:
    """Check inputted list and removes from them numbers"""
    output = list()
    for val in values:
        val = str(val)
        if not val.isdigit():
            output.append(val)
    return length_of_list(output)


def try_db_response(*args) -> bool or str or None:
    """Try to sum variables if there are integers and return True or False depending on the all arguments if are 1. If
    there is numbers and string, catches the error and moves call to sub function """
    try:
        if sum(args) == len(args):
            return True
        return False
    except (TypeError, ValueError):
        return check_if_strings(args)


def action_decision(response: (int or str)) -> int or str or redirect:
    """According to the input return response or redirect"""
    if response:
        return jsonify({"result": response})
    elif not response or response is None:
        msg = "Something went wrong"
        return jsonify({'missing_values': msg})
    return redirect(url_for('err.error'))


@profile.route('/swipe', methods=['GET'])
@login_required
def action_swipe():
    """Decline users in DB or if other user did not get offer yet, it will write user´s key to the other user´s
        declined. """
    curr = session["user"]["key"]
    other = session["availableUserKey"]
    if db.check_in_accepted(other, curr):
        remove = db.remove_from_accepted(other, curr)
    else:
        remove = 1
    match_c = db.add_to_declined(curr, other)
    match_m = db.add_to_declined(other, curr)
    return action_decision(try_db_response(remove, match_c, match_m))


def match_users(current_user_id: int, matched_user_id: int):
    """Moves user key from other user´s accepted to matched. And put other user´s key to the matched field of user """
    remove = db.remove_from_accepted(matched_user_id, current_user_id)
    match_c = db.add_to_matched(current_user_id, matched_user_id)
    match_m = db.add_to_matched(matched_user_id, current_user_id)
    return try_db_response(remove, match_c, match_m)


@profile.route('/match', methods=['GET'])
@login_required
def action_match():
    """Match users in DB or if other user did not get offer yet, it will write user´s key to the other user´s
    accepted. """
    curr = session["user"]["key"]
    other = session["availableUserKey"]
    if db.check_in_accepted(other, curr):
        response = match_users(curr, other)
    else:
        response = try_db_response(db.add_to_accepted(curr, other))
    return action_decision(response)


def format_location(loc: str) -> list[float]:
    """Formats location (point (string)) from MySQL to list of floats"""
    loc = loc.replace("(", " ").replace(")", "")
    loc = loc.split(" ")
    loc.pop(0)
    return [float(x) for x in loc]


def get_available_user() -> (User, redirect, str):
    """Returns user data (name, birthday, gender, image) if the current user is in range, otherwise return string. If
    error occur in DB it will return string with error message """
    if session["listOfAvailable"]:
        array_of_available = session["listOfAvailable"]
    else:
        array_of_available = db.get_by_location(*format_location(session["user"]["location"]), session["user"]["range"],
                                                session["user"]["key"], session["user"]["interested"],
                                                session["user"]["gender"],
                                                session["user"]["agelower"], session["user"]["ageupper"],
                                                session["user"]["birthday"])
    if array_of_available:
        if isinstance(array_of_available, list):
            user = array_of_available.pop(0)
            session["listOfAvailable"] = array_of_available
            return User(user["key"], user["email"], user["name"], user["password"], birthday=user["birthday"],
                        gender=user["gender"], images=user["images"])
        return array_of_available
    return "No possible matches"
