from flask import Blueprint, render_template, redirect, url_for, request, session, flash, Markup
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template("login.html")


def login_check(login_credentials: dict):
    """Checks login credentials"""
    db_answer = db.get_by_email(login_credentials['email'])
    if isinstance(db_answer, User):
        # User found, verifying password:
        if check_password_hash(db_answer.password, login_credentials['password']):
            login_user(db_answer, remember=login_credentials.get('remember', False))
            session["gotLocation"] = False
            session["error"] = None
            session["listOfAvailable"] = []
            session["user"] = current_user.__dict__
            return redirect(url_for('main.index'))
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    elif db_answer is None:
        # User not found id DB:
        flash("Email does not exist, please register.")
        return redirect(url_for('auth.signup'))
    # Redirected error from wrapper:
    return db_answer


@auth.route('/login', methods=['POST'])
def login_post():
    return login_check(request.form.to_dict())


@auth.route('/signup')
def signup():
    return render_template("signup.html")


def user_sing_in(sing_in_credentials: dict):
    """Sing in user if data are ok"""
    email = sing_in_credentials['email']
    db_answer = db.get_by_email(email)
    if isinstance(db_answer, User):
        # User found in DB, pop up above sing up table
        flash(Markup("Email address already exists. Go to <a href=" + '"'
                     + "login" + '"' + ">login page</a>."))
        return redirect(url_for('auth.signup'))
    elif db_answer is None:
        # User is not in DB. Inserting basic info
        db_answer = db.insert_user(email, sing_in_credentials['name'],
                                   generate_password_hash(sing_in_credentials['password'], method='sha256'))
        if isinstance(db_answer, int) and db_answer == 1:
            # DB inserted users info, page is redirected and user can log in
            flash("Account was created, please login.")
            return redirect(url_for('auth.login'))
    # Redirected error from wrapper:
    return db_answer


@auth.route('/signup', methods=['POST'])
def signup_post():
    return user_sing_in(request.form.to_dict())


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
