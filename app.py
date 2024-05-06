from flask import Flask, flash, redirect, render_template, session, abort ,request, url_for
from flask_session import Session
from flask_mail import Mail, Message
from functools import wraps
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

# setup mail server for forgot passwords
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '1221106177@student.mmu.edu.my'
app.config['MAIL_PASSWORD'] = 'sxrh rlwk nump hxbg'

mail = Mail(app)

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
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        df.checkUser(email, password, session)
        return redirect("/")
    else:
        return render_template("login.html")

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
        return df.checkPasswords(currentPassword,newPassword,confirmPassword,session)
    else:
        return render_template("changePassword.html", name=session.get("username"))
    
@app.route("/addingCourses", methods=["GET", "POST"])
def addingCourses():
    if request.method == "POST":
        courseId = request.form.get("courseId")
        courseName = request.form.get("courseName").upper()
        trimesterCode = request.form.get("trimesterCode")
        lecturerId = request.form.get("lecturerId")
        lectOrTut = request.form.get("lectOrTut").upper()
        numStudents = request.form.get("numStudents")
        numGroups = request.form.get("numGroups")
        Section = request.form.get("sectionCode")
        df.addingClasses(courseId, courseName, trimesterCode, lecturerId, numStudents, numGroups, lectOrTut, Section)
        return redirect("/dashboard")
    else:
        return render_template("addCourses.html", name=session.get("username"))



@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        email = request.form.get("email")
        db.execute("SELECT * FROM users")
        users = db.fetchall()
        users = users[0]
        if email in users:
            # Generate a unique token for the password reset link
            token = str(uuid.uuid4())
            # Send the password reset email
            send_password_reset_email(email, token)
            flash('Password reset email sent. Please check your email.')
            return redirect("/")
        else:
            flash('Email address not found.')
    return render_template('forgotPassword.html')

def send_password_reset_email(email, token):
    msg = Message('Password Reset Request', sender='1221106177@student.mmu.edu.my', recipients=[email])
    msg.body = f"Click the following link to reset your password: {url_for('resetPassword', token=token, _external=True)}"
    mail.send(msg)

@app.route('/resetPassword/<token>', methods=['GET', 'POST'])
def resetPassword(token):
    # Check if the token is valid (e.g., present in a database)
    if request.method == 'POST':
        new_password = request.form['password']
        # Update the password in the database
        flash('Your password has been reset successfully.')
        return redirect("/")
    return render_template('reset_password.html')

# F5 to run flask and auto refresh
if __name__ == "__main__":
    app.run(debug=True)   # has auto refresh now 
