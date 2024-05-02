import os
import pathlib
from flask import Flask, flash, redirect, render_template, session, abort ,request
from flask_session import Session
from google_auth_oauthlib.flow import Flow
import requests
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests
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

# landing page
@app.route("/")
def index():
    return render_template("layout.html", name=session.get("name"))

# login page
@app.route("/login", methods=["GET","POST"])
def login():
    session["name"] = request.form.get("UserId")
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