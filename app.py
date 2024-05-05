from flask import Flask, flash, redirect, render_template, session, abort ,request
from flask_session import Session
from functools import wraps

import databaseFunctions as df
import Functions as func
import sqlite3

# initiate flask
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

con = sqlite3.connect("database.db", check_same_thread=False)      # connects to the database
db = con.cursor()

def login_required(function):
    @wraps(function)
    def decorated_function(*args,**kwargs):
        if "username" not in session:
            return redirect("/login")         
        else:
            return function(*args,**kwargs)
    return decorated_function

# landing page
@app.route("/")
@login_required
def index():
    return render_template("index.html", name=session.get("username"))

# login page
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        df.checkEmail(email, password, session)
        return redirect("/")
    else:
        return render_template("login.html")

# logout redirect
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/studentGroup")
def studentGroups():
    return render_template("studentGroup.html")


@app.route("/studentPeerReview")
def studentPeerReview():
    return render_template("studentPeerReview.html", name=session.get("username"))

@app.route("/changePassword", methods=["GET","POST"])
@login_required
def changePassword():
    if request.method == "POST":
        currentPassword = request.form.get("currentPassword")
        newPassword = request.form.get("newPassword")
        confirmPassword = request.form.get("confirmPassword")
        return df.checkPasswords(currentPassword,newPassword,confirmPassword,session)
    else:
        return render_template("changePassword.html")

if __name__ == "__main__":
    app.run(debug=True)   # has auto refresh now 