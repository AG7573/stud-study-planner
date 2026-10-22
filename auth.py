from flask import Blueprint
from flask import render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User
from functools import wraps

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash("The email is already registered!")
            return redirect(url_for("auth.signup"))
        password_hash = generate_password_hash(password)

        user = User(
            name=name, 
            email=email, 
            password_hash=password_hash
        )
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("auth.login"))
    
    if request.method == "GET":
        return render_template("signup.html")
    
@auth.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        email_exists = User.query.filter_by(email=email).first()
        if not email_exists:
            flash("Invalid email or password")
            return render_template("login.html")

        password_valid = check_password_hash(email_exists.password_hash, password)

        if password_valid == False:
            flash("Incorrect Password!")
            return render_template("login.html")

        session["user_id"] = email_exists.id
        return redirect(url_for("subjects.list_subjects"))    # point to dashboard once built

    if request.method == "GET":
        return render_template("login.html")

@auth.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("user_id", None)
    flash("You've been logged out.")
    return redirect(url_for("auth.login"))

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return decorated_function