from flask import Blueprint, render_template, request, flash, redirect, url_for, session, json, Response
from flask_login import login_required, current_user, login_user
from datetime import datetime
from models import db
import requests

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile_info')
@login_required
def profile_info():
    return render_template("profile.html", name=session["user"]["name"])


def sendRequest(url: str) -> bool or Exception:
    """Checks if input string is url and if we can ping it."""
    extension = ["jpg", "jpeg", "png", "gif"]
    try:
        if "http" in url or "https" in url and any(ex in url for ex in extension):
            page = requests.get(url, stream=True, timeout=1, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/51.0.2704.103 Safari/537.36"})
    except Exception as e:
        return [e]
    else:
        if "page" in locals() and page.status_code == 200:
            return page
    return False


def post_advance_info(request_values):
    """Updates user's info to DB and sends responses back to the user"""
    flash_string = str()
    request_values[0] = datetime.strptime(request_values[0], '%m/%d/%Y')
    # Picture url verification, if not available, replaced with string:"not valid url from internet"
    verification = sendRequest(request_values[-2])
    if not verification:
        request_values[-2] = "not a valid image url from internet"
        flash("Picture has not valid url!")
    elif isinstance(verification, list):
        request_values[-2] = "not a valid image url from internet"
    # Load new data to DB and return response
    return flash_string, db.profile_info(request_values, session["user"]["key"])


@main.route('/settings', methods=["GET", 'POST'])
@login_required
def settings():
    """Refresh settings of user or just displays them"""
    if request.method == 'POST':
        flash_string, db_response = post_advance_info(list(request.get_json().values()))
        #Possible error with redirect
        if not isinstance(db_response, int):
            return db_response
        #Return affected rows from DB
        if db_response == 0:
            flash("Nothing was changed")
        elif db_response > 0:
            flash("Changes were saved")
        #Refresh of user in session
        login_user(db.get_by_id(current_user.get_id()))
        session["user"] = current_user.__dict__
        return Response(status=200)
    return render_template("settings.html", data=(current_user.get_advanced_info()), usr=current_user)


@main.route('/cords', methods=['POST'])
@login_required
def cords():
    """Writes new location of user to the DB"""
    data = request.get_json()
    lat, long = list(data.values())
    db_response = db.update_location(long, lat, session["user"]["key"])
    if 1 == db_response:
        session["gotLocation"] = True
        return redirect(url_for('profile.profiles_page'))
    elif isinstance(db_response, int):
        flash('Something wrong with DB, upload your location was not successful!')
        return redirect(url_for('main.index'))
    return db_response
