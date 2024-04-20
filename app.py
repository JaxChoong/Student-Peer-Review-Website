from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import sqlite3

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

con = sqlite3.connect("database.db", check_same_thread=False)      # connects to the database
db = con.cursor()   

@app.route("/")
def index():
    return render_template("home.html", name=session.get("name"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
            form_user_id = request.form.get("UserId")
            form_password = request.form.get("password")

            db.execute("SELECT * FROM USERS WHERE username=?", (form_user_id,))
            existingusers = db.fetchall()

            if existingusers:
                 user_record = existingusers[0]
                 print(user_record)
                 if user_record[2] == form_password:
                      session["name"] = form_user_id
                      return redirect("/")
                 else:
                      flash("Incorrect Password.")
                      return render_template("errormsg.html")
            else:
                 flash("User Doesn't Exist.")
                 return render_template("errormsg.html")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")