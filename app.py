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
    return render_template("layout.html", name=session.get("username"))

# login page
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(username)
        print(password)
        df.checkEmail(username, password, session)
        return redirect("/")
    else:
        return render_template("login.html")

# logout redirect
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/studentgroups")
def studentGroups():
    return render_template("studentgroup.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", name=session.get("name"))