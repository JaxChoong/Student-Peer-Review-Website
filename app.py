from flask import Flask, flash, redirect, render_template, session, abort ,request, url_for
from flask_session import Session
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
from functools import wraps
from dotenv import load_dotenv
import os
import uuid

import databaseFunctions as df
import Functions as func
import sqlite3

# initiate flask
app = Flask(__name__)
# templating flask stuff
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Load environment variables from .env file
load_dotenv()

# setup mail server for forgot passwords
app.config['MAIL_USE_TLS'] = True
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD

mail = Mail(app)
# setup Oauth stuff
oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id= os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    # userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",  # This is only needed if using openId to fetch user info
    client_kwargs={"scope": "email profile"}
    # server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
)
# connects to the database with cursor
con = sqlite3.connect("database.db", check_same_thread=False)
db = con.cursor()

# sets a functio that forces a new user to login
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
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external= True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    resp.raise_for_status()
    user_info = resp.json()
    # do something with the token and profile
    session['email'] = user_info["email"]
    session['username'] = user_info["name"]
    return redirect('/')

# logout redirect
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")

# studentgroups page
@app.route("/studentGroup")
def studentGroups():
    return render_template("studentGroup.html" ,name=session.get("username"))

# dashboard page
@app.route("/dashboard")
def dashboard():
    courses = df.getCourses()
    return render_template("index.html", name=session.get("username"), courses=courses)

@app.route("/studentPeerReview")
def studentPeerReview():
    return render_template("studentPeerReview.html", name=session.get("username"))

# peer review page

# change password
@app.route("/changePassword", methods=["GET","POST"])
@login_required
def changePassword():
    if request.method == "POST":
        currentPassword = request.form.get("currentPassword")
        newPassword = request.form.get("newPassword")
        confirmPassword = request.form.get("confirmPassword")
        return df.checkPasswords(currentPassword,newPassword,confirmPassword,session.get("email"))
    else:
        return render_template("changePassword.html", name=session.get("username"))
    
@app.route("/addingCourses", methods=["GET", "POST"])
def addingCourses():
    if request.method == "POST":
        courseId = request.form.get("courseId").upper()
        courseName = request.form.get("courseName").upper()
        trimesterCode = request.form.get("trimesterCode")
        lecturerId = request.form.get("lecturerId").upper()
        lectOrTut = request.form.get("lectOrTut").upper()
        numStudents = request.form.get("numStudents")
        numGroups = request.form.get("numGroups")
        Section = request.form.get("sectionCode").upper()
        if df.verifyClassInput(courseId, trimesterCode, lecturerId, lectOrTut, Section) != False:
            if lectOrTut == "L":
                lectOrTut = "Lecture"
            else:
                lectOrTut = "Tutorial"
            df.addingClasses(courseId, courseName, trimesterCode, lecturerId, numStudents, numGroups, lectOrTut, Section)
            return redirect("/dashboard")
        else:
            return render_template("addCourses.html", name=session.get("username"))
    else:
        return render_template("addCourses.html", name=session.get("username"))



@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        email = request.form.get("email")
        
        # Check if the email exists in the database
        db.execute("SELECT email FROM users WHERE email = ?", (email,))
        existing_email = db.fetchone()
        
        if existing_email:
            # Generate a unique token for the password reset link
            token = str(uuid.uuid4())
            # Save the reset token along with the email address
            df.saveResetPasswordToken(email, token)
            # Send the password reset email
            send_password_reset_email(email, token)
            flash('Password reset email sent. Please check your email.')
            return redirect("/")
        else:
            flash('Email address not found.')
    return render_template('forgotPassword.html')

def send_password_reset_email(email, token):
    msg = Message('Password Reset Request', sender='studentpeerreviewsystem@gmail.com', recipients=[email])
    msg.body = f"Click the following link to reset your password: {url_for('resetPassword', token=token, _external=True)}"
    mail.send(msg)

@app.route('/resetPassword/<token>', methods=['GET', 'POST'])
def resetPassword(token):
    # Check if the token is valid (e.g., present in a database)
    if request.method == 'POST':
        email  = df.getResetPasswordEmail(token)
        newPassword = request.form.get('newPassword')
        # Update the password in the database
        if newPassword:
            df.checkDatabasePasswords(newPassword,email)
            df.deleteResetPasswordToken(email,token)
            flash('Your password has been reset successfully.')
            return redirect("/")
    return render_template('resetPassword.html', token = token)

# F5 to run flask and auto refresh
if __name__ == "__main__":
    app.run(debug=True)   # has auto refresh now 
