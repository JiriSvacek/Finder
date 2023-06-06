from flask import Blueprint, render_template


err = Blueprint('err', __name__)

@err.route('/error')
def error():
    return render_template("error.html")
