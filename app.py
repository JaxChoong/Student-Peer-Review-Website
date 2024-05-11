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
microsoft = oauth.register(
    name="microsoft",
    client_id= os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    access_token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
    access_token_params=None,
    authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    authorize_params=None,
    api_base_url="https://graph.microsoft.com/v1.0/",
    userinfo_endpoint="https://graph.microsoft.com/v1.0/me",  # This is only needed if using openId to fetch user info
    client_kwargs={"scope": "User.Read"},
)
# connects to the database with cursor
con = sqlite3.connect("database.db", check_same_thread=False)
db = con.cursor()


# sets a function that forces a new user to login
def login_required(function):
    @wraps(function)
    def decorated_function(*args,**kwargs):
        if "username" not in session:
            return redirect("/login")         
        else:
            return function(*args,**kwargs)
    return decorated_function

def logout_required(function):
    @wraps(function)
    def decorated_function(*args,**kwargs):
        if "username" in session:
            return redirect("/")         
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
@logout_required
def login():
    microsoft = oauth.create_client('microsoft')
    redirect_uri = url_for("authorize", _external=True)
    return microsoft.authorize_redirect(redirect_uri)


# authorise page
@app.route("/authorise")
@logout_required
def authorize():
    microsoft = oauth.create_client("microsoft")
    token = microsoft.authorize_access_token()
    resp = microsoft.get("me")
    resp.raise_for_status()
    user_info = resp.json()
    # do something with the token and profile
    if not user_info["mail"].endswith(".mmu.edu.my"):
        flash("Please log in using MMU email only.")
        return redirect("/login")
    session["email"] = user_info["mail"]
    session["username"] = user_info["displayName"]
    df.addUserToDatabase(session.get("email"), session.get("username"))
    return redirect("/")


# logout redirect
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


# dashboard page
@app.route("/dashboard")
def dashboard():
    courses = df.getCourses()
    return render_template("index.html", name=session.get("username"), courses=courses)


# studentgroups page
@app.route("/studentGroup")
def studentGroups():
    return render_template("studentGroup.html" ,name=session.get("username"))


# peer review page
@app.route("/studentPeerReview", methods=["GET", "POST"])
def studentPeerReview():
    members = df.getMembers(session)
    groupNum = members[0]
    membersList = members[1]
    memberCount = len(membersList)

    if request.method == "POST":
        # ratings
        # for i in range(1, memberCount+1):
        #     ratings = request.form.get(f"ratingStudent{i}")

        # comments
        # for i in range(1, memberCount+1):
        #     comments = request.form.get(f"commentStudent{i}")

        # others
        groupSummary = request.form.get("groupSummary")
        challenges = request.form.get("challenges")
        secondChance = request.form.get("secondChance")
        roleLearning = request.form.get("roleLearning")
        feedback = request.form.get("feedback")

        return redirect("/")
    else:
        return render_template("studentPeerReview.html", name=session.get("username"), membersList=membersList)



@app.route("/addingCourses", methods=["GET", "POST"])
def addingCourses():
    if request.method == "POST":
        courseId = request.form.get("courseId").upper()
        courseName = request.form.get("courseName").upper()
        if df.addingClasses(courseId, courseName) == False:
            # flash("Course already exists.")
            return redirect("/addingCourses")
        else:
            return redirect("/dashboard")
    else:
        return render_template("addCourses.html", name=session.get("username") )


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


# forgot password
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


# reset password tokens
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
    app.run(debug=True,host='localhost')   # has auto refresh now 
