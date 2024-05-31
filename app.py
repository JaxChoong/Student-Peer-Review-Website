from flask import Flask, flash, redirect, render_template, session, abort ,request, url_for, get_flashed_messages
from flask_session import Session
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
from functools import wraps
from dotenv import load_dotenv
import os
import uuid
from werkzeug.utils import secure_filename

import databaseFunctions as df
import Functions as func
import sqlite3

# initiate flask
app = Flask(__name__)
# templating flask stuff
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            return redirect("/dashboard")                 
        else:
            return function(*args,**kwargs)
    return decorated_function

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("No file part", "error")
        print("No file part")
    file = request.files['file']

    if file.filename == '':
        flash("No selected file", "error")
        print("No selected file")
    
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        flash("File uploaded successfully", "success")
        print("File uploaded successfully")
        print(file.filename)
        df.csvToDatabase(f"./uploads/{file.filename}")
    return redirect("/dashboard")

# landing page
@app.route("/")
def index():
    # if request.method == "POST":
    #     return redirect("/login")
    return render_template("landing.html")


@app.route("/dashboard")
@login_required
def dashboard():
    if session.get("role") == "STUDENT":
        # student view
        registeredCourses = df.getRegisteredCourses(session.get("id"))
        return render_template("dashboard.html", name=session.get("username"), courses=registeredCourses,role = session.get("role"))
    elif session.get("role") == "LECTURER":
        # lecturer view
        registeredCourses = df.getLecturerCourses(session.get("id"))
        return render_template("dashboard.html", name=session.get("username"), courses=registeredCourses,role = session.get("role"))

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
    session["role"] = df.addUserToDatabase(session.get("email"), session.get("username"))
    session["id"] = df.getUserId(user_info["mail"])
    return redirect("/dashboard")


# logout redirect
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


# studentgroups page
@app.route("/studentGroup", methods=["GET", "POST"])
@login_required
def studentGroups():
    lecturerId = session.get("id")
    if request.method == "POST":
        courseId = request.form.get("courseId")
        courseId = courseId[1:-1].split(",")
        courseId,subjectCode,subjectName = courseId[0],courseId[1][2:-1],courseId[2][2:-1]
        currentCourseSection = df.getCurrentLecturerCourse(lecturerId,courseId)
    return render_template("studentgroup.html" ,name=session.get("username"),studentGroups=df.getStudentGroups(courseId,currentCourseSection),courseSection=currentCourseSection,subjectCode=subjectCode,subjectName=subjectName)

# about us page
@app.route("/aboutUs")
@login_required
def aboutUs():
    return render_template("aboutUs.html" ,name=session.get("username"))

# peer review page
@app.route("/studentPeerReview", methods=["GET", "POST"])
@login_required
def studentPeerReview():
    membersId,membersName = df.getMembers(session)
    memberCounts = len(membersId)
    if session.get("role") == "STUDENT":
        if request.method == "POST":
            reviewerId = session.get("id")
            # ratings
            totalRatings = 0
            ratings_data = []
            courseId = session.get("courseId")
            sectionId,groupNum, = df.getReviewCourse(courseId,reviewerId)
            for i, member in enumerate(membersId):
                ratings = float(request.form.get(f"rating{member}"))
                comments = request.form.get(f"comment{member}")
                revieweeId = membersName[i][0]      
                            
                totalRatings += ratings  # Add rating to total
                
                # Store data for later use
                ratings_data.append((ratings, revieweeId, comments))

            for ratings, revieweeId, comments in ratings_data:
                AdjR = func.adjustedRatings(ratings, totalRatings, memberCounts)
                print(AdjR)
                message = df.reviewIntoDatabase(courseId,sectionId,groupNum,reviewerId,revieweeId,AdjR,comments)


            flash(f"{message}")
            groupSummary = request.form.get("groupSummary")
            challenges = request.form.get("challenges")
            secondChance = request.form.get("secondChance")
            roleLearning = request.form.get("roleLearning")
            feedback = request.form.get("feedback")
            df.selfAssessmentIntoDatabase(courseId,sectionId,groupNum,reviewerId,groupSummary,challenges,secondChance,roleLearning,feedback)
            session.pop("courseId")
            session.pop("sectionId")
            session.pop("groupNum")
            return redirect("/dashboard")
    else:
        if request.method == "POST":
            return redirect("/dashboard")
        return render_template("studentPeerReview.html", name=session.get("username"), members=membersId)

@app.route("/studentPeerReviewPage", methods=["GET", "POST"])
@login_required
def studentPeerReviewPage():
    if request.method == "POST":
        session["courseId"] = request.form.get("courseId")
        session["sectionId"],session["groupNum"] = df.getReviewCourse(session.get("courseId"),session.get("id"))
        membersId,membersName = df.getMembers(session)
        # placeholder to check if student has been reviewed yet
        df.getStudentRatings(session.get("courseId"),session.get("sectionId"),session.get("groupNum"),session.get("id"))
        return render_template("studentPeerReview.html", name=session.get("username"), members=membersId)

@app.route('/addingCourses', methods=['GET','POST'])
def addingCourses():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            courseId = request.form['courseId']
            courseName = request.form['courseName']
            lecturerId = session.get('id')
            
            sectionIds,lectureOrTutorial = df.extract_section_ids(filepath)
            studentNum = df.extract_student_num(filepath)
            groupNum,membersPerGroup = df.extract_group_num(filepath)
            # Insert course into the database
            for sectionId in sectionIds:
                df.addCourseToDb(courseId, courseName, lecturerId, sectionId,studentNum,groupNum,lectureOrTutorial,membersPerGroup)
            
            # Process CSV to add students and groups
            df.csvToDatabase(courseId, courseName, lecturerId, sectionId,filepath)
            
            flash('Course and students successfully added.')
            return redirect('/dashboard')
        else:
            flash('Invalid file format. Please upload a CSV file.')
            return redirect(request.url)
    return render_template('addCourses.html', name=session.get('username'))

@app.route("/customizations", methods=["GET", "POST"])
def customizingQuestions():
    lecturerId = session.get("id")
    return render_template("customizingQuestions.html", name=session.get("username") )

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
            return redirect("/dashboard")
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
            return redirect("/dashboard")
    return render_template('resetPassword.html', token = token)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

# F5 to run flask and auto refresh
if __name__ == "__main__":
    app.run(debug=True,host="localhost")
       # has auto refresh now
