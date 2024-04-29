import os
import pathlib
from flask import Flask, flash, redirect, render_template, session, abort ,request
from flask_session import Session
from google_auth_oauthlib.flow import Flow
import requests
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests

import databaseFunctions as df
import Functions as func
import sqlite3

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "713939446938-bnel24iohi6clskjameibirdqdd2533h.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
    )


def login_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return redirect("/login")         # google authorization required
        else:
            return function()
    return wrapper

    
con = sqlite3.connect("database.db", check_same_thread=False)      # connects to the database
db = con.cursor()   

@app.route("/")
@login_required
def index():
    return render_template("layout.html", name=session.get("name"))

@app.route("/login", methods=["GET","POST"])
def login():
    session["name"] = request.form.get("UserId")
    session["google_id"] = "foo"
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort[500]         # states does not match
    
    credentials = flow.credentials
    request_session = requests.Session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session = cached_session)

    #using this var
    id_info = id_token.verify_oauth2_token(
        id_token= credentials._id_token,
        request= token_request,
        audience=GOOGLE_CLIENT_ID
    )

    if func.VerifyEmail(id_info, session) == True:
        df.checkEmail(session)
    else:
        return redirect("/login")
    return redirect("/")