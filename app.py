from flask import Flask, flash, redirect, render_template, session, abort ,request, url_for,jsonify,send_file,make_response,after_this_request
from flask_session import Session
from flask_mail import Mail,Message
import uuid
from authlib.integrations.flask_client import OAuth
from functools import wraps
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
import ast
import io
import csv

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

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load environment variables from .env file
load_dotenv()


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

def lecturer_only(function):
    @wraps(function)
    def decorated_function(*args,**kwargs):
        if session.get("role") != "LECTURER":
            return redirect("/dashboard")         
        else:
            return function(*args,**kwargs)
    return decorated_function

def student_only(function):
    @wraps(function)
    def decorated_function(*args,**kwargs):
        if session.get("role") != "STUDENT":
            return redirect("/dashboard")         
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
    file = request.files['file']

    if file.filename == '':
        flash("No selected file", "error")
    
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        flash("File uploaded successfully", "success")
        df.csvToDatabase(f"./uploads/{file.filename}")
    return redirect("/addingCourses")

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


@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")
        if password != confirmPassword:
            flash("Passwords do not match")
            return redirect("/register")
        else:
            message = df.registerUser(email,username,password)
            if message == "success":
                flash("User has been registered")
                return redirect("/login")
            else:
                flash(f"{message}")
                return redirect("/register")
    else:
        return render_template("register.html")
    
# login page
@app.route("/login", methods=["GET","POST"])
@logout_required
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = df.checkUser(email, password)
        if isinstance(user, tuple):
            session["email"] = user[1]
            session["username"] = user[3]
            session["role"] = user[4]
            session["id"] = user[0]
            return redirect("/dashboard")
        else:
            flash(user)
            return redirect("/login")
    else:
        return render_template("login.html")

# change password
@app.route("/changePassword", methods=["GET","POST"])
@login_required
def changePassword():
    if request.method == "POST":
        currentPassword = request.form.get("currentPassword")
        newPassword = request.form.get("newPassword")
        confirmPassword = request.form.get("confirmPassword")
        if newPassword != confirmPassword:
            flash("Passwords do not match")
            return redirect("/changePassword")
        return df.checkPasswords(currentPassword,newPassword,confirmPassword,session.get("id"))
    else:
        return render_template("changePassword.html", name=session.get("username"),role = session.get("role"))
    

@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        email = request.form.get("email")
        
        # Check if the email exists in the database
        db.execute("SELECT email FROM users WHERE email = ?", (email,))
        existing_email = db.fetchone()
        
        if db.execute("SELECT email FROM users WHERE email = ?", (email,)).fetchone():
            # Generate a unique token for the password reset link
            token = str(uuid.uuid4())
            # Save the reset token along with the email address
            df.saveResetPasswordToken(email, token)
            # Send the password reset email
            send_password_reset_email(email, token)
            flash('Password reset email sent. Please check your email. (Check spam/junk folder if not found)')
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
            changed=df.checkDatabasePasswords(newPassword,email)
            df.deleteResetPasswordToken(email,token)
            return changed
    return render_template('resetPassword.html', token = token)

# logout redirect
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


# studentgroups page
@app.route("/studentGroup", methods=["GET", "POST"])
@login_required
@lecturer_only
def studentGroups():
    lecturerId = session.get("id")
    if request.method == "POST":
        courseId = request.form.get("courseId")
        courseCode = request.form.get("courseCode")
        courseName = request.form.get("courseName")
        currentCourseSection = df.getCourseSection(courseId)
        courseDates = df.getReviewDateForCourse(courseId)
        studentGroups=[]
        for section in currentCourseSection:
            groups = df.getGroups(courseId,section[0])
            studentsInGroup = []  
            # courseId,sectionId,groupNum,studentId
            students = df.getStudentGroups(courseId,section[0],groups)
            # currentLecturerRating = df.getLecturerRating(currentCourseId)
            startDate,endDate = df.getReviewDate(section[0])
            studentGroups.append([section[0],section[1],students,courseId,startDate,endDate])
    else:
        return redirect("/dashboard")
    return render_template("studentgroup.html" ,name=session.get("username"),studentGroups=studentGroups,courseSection=currentCourseSection,subjectCode=courseCode,courseName=courseName,courseId=courseId,courseDates=courseDates,role = session.get("role"))

# about us page
@app.route("/aboutUs")
@login_required
def aboutUs():
    return render_template("aboutUs.html" ,name=session.get("username"),role = session.get("role"))

# peer review page
@app.route("/studentPeerReview", methods=["GET", "POST"])
@login_required
@student_only
def studentPeerReview():
    membersId,membersName = df.getMembers(session)
    memberCounts = len(membersId)
    questions = ast.literal_eval(request.form.get("questions"))
    if session.get("role") == "STUDENT":
        if request.method == "POST":
            reviewerId = session.get("id")
            sectionId = session.get("sectionId")
            dateValid = df.checkDates(sectionId)
            # check if currently in review period
            if dateValid == True:
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
                    message = df.reviewIntoDatabase(courseId,sectionId,groupNum,reviewerId,revieweeId,AdjR,comments)


                for question in questions:
                    question_id = request.form.get(f"questionId{question[0]}")
                    question_text = request.form.get(f"questionText{question_id}")
                    answer = request.form.get(f"answer{question_id}")
                    message = df.selfAssessmentIntoDatabase(courseId, question_id, question_text, answer, reviewerId)
                if message == "update":
                    flash("Review has been updated")
                else:
                    flash("Review has been submitted")
                session.pop("courseId")
                session.pop("sectionId")
                session.pop("groupId")
                return redirect("/dashboard")
            else:
                session.pop("courseId")
                session.pop("sectionId")
                session.pop("groupId")
                flash(f"{dateValid}")
                return redirect("/dashboard")
        else:
            return redirect("/dashboard")
    else:
        if request.method == "POST":
            return redirect("/dashboard")
        return render_template("studentPeerReview.html", name=session.get("username"), members=membersId,role = session.get("role"))

@app.route("/studentPeerReviewPage", methods=["GET", "POST"])
@login_required
@student_only
def studentPeerReviewPage():
    if request.method == "POST":
        courseData = ast.literal_eval((request.form.get("courseId")))
        courseId = courseData[-1]
        courseName = courseData[0],courseData[1]
        intro = df.getIntro(courseId)
        questions = df.getReviewQuestions(courseId)
        session["courseId"] = courseId
        session["sectionId"],session["groupId"] = df.getReviewCourse(session.get("courseId"),session.get("id"))
        sectionId = session.get("sectionId")
        dateValid,message = df.checkDates(sectionId)
        if dateValid == True:
            membersId,membersName = df.getMembers(session)
            flash(f"{message}")
            return render_template("studentPeerReview.html", name=session.get("username"), members=membersId,questions=questions,role = session.get("role"),courseName = courseName,introduction = intro)
        elif dateValid == False:
            flash(f"{message}")
            return redirect("/dashboard")
        else:
            flash(f"{message}")
            return redirect("/dashboard")
    else:
        return redirect("/dashboard")

@app.route('/addingCourses', methods=['GET', 'POST'])
@login_required
@lecturer_only
def addingCourses():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'message': 'No file part', 'category': 'danger'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file', 'category': 'danger'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            courseCode = request.form.get('courseId')
            courseName = request.form.get('courseName')
            lecturerId = session.get('id')
            startDate = request.form.get("startDate")
            endDate = request.form.get("endDate")
            intro = request.form.get("intro")
            NEW_USER_KEYS = ["email", "name", "password"]

            try:
                sectionIds = df.extract_section_ids(filepath)
            except ValueError as e:
                return jsonify({'message': str(e), 'category': 'danger'}), 400

            try:
                for sectionId in sectionIds:
                    message, courseId = df.addCourseToDb(courseCode, courseName, lecturerId, sectionId)

                message, collectTempUserCreds = df.csvToDatabase(courseId, lecturerId, filepath)
                if message:
                    return jsonify({'message': message, 'category': 'danger'}), 400
                df.changeReviewDateForCourse(courseId, startDate, endDate)
                if intro:
                    df.changeIntro(courseId, intro)

                # Create CSV data in memory for temporary user credentials
                csv_data = io.StringIO()
                csv_writer = csv.writer(csv_data)
                csv_writer.writerow(NEW_USER_KEYS)
                for creds in collectTempUserCreds:
                    csv_writer.writerow(creds)

                response = make_response(csv_data.getvalue())
                response.headers["Content-Disposition"] = "attachment; filename=temp_user_creds.csv"
                response.headers["Content-Type"] = "text/csv"

                flash('Course and students successfully added.', 'success')
                return response

            except Exception as e:
                return jsonify({'message': f'Error adding courses: {str(e)}', 'category': 'error'}), 500
        else:
            return jsonify({'message': 'Invalid file format. Please upload a CSV file.', 'category': 'error'}), 400

    introduction = df.getDefaultIntro()
    return render_template('addCourses.html', name=session.get('username'), role=session.get("role"), introduction=introduction)
@app.route("/importAssignmentMarks", methods=["GET", "POST"])
@login_required
@lecturer_only
def importAssignmentMarks():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'message': 'No file part', 'category': 'danger'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file', 'category': 'danger'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            courseId = request.form.get('courseId')
            courseCode = request.form.get('courseCode')
            lecturerId = session.get('id')

            try:
                # Process the file and generate the final marks data
                finalMarksHeaders, finalMarksData = df.importAssignmentMarks(lecturerId, courseId, filepath)
                # Create CSV data in memory
                csv_data = io.StringIO()
                csv_writer = csv.writer(csv_data)
                csv_writer.writerow(finalMarksHeaders)
                for row in finalMarksData:
                    csv_writer.writerow(row)

                # Create response
                response = make_response(csv_data.getvalue())
                response.headers["Content-Disposition"] = f"attachment; filename={courseCode}_final_marks.csv"
                response.headers["Content-Type"] = "text/csv"
                return response
            except ValueError as e:
                return jsonify({'message': f'{str(e)}', 'category': 'danger'}), 500
            except Exception as e:
                flash(f'Error processing assignment marks: {str(e)}', 'danger')
                return redirect("/dashboard")
            finally:
                # delete file after passing it back
                if os.path.exists(filepath):
                    os.remove(filepath)
            
        else:
            flash('Invalid file format. Please upload a CSV file.', 'danger')
            return redirect("/dashboard")

    return redirect("/dashboard")

        

@app.route("/downloadFMTemplate", methods=["GET", "POST"])
@login_required
@lecturer_only
def downloadFMTemplate():
    if request.method == "POST":
        courseId = request.form.get("courseId")
        courseCode = request.form.get("courseCode")
        sectionAndGroups = df.getSectionAndGroup(courseId)
        # Create CSV data
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        csv_writer.writerow(["Sections", "Groups", "Marks"])
        for section, group in sectionAndGroups:
            csv_writer.writerow([section, group, 0])
        # Create response
        response = make_response(csv_data.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename={courseCode}final_marks_template.csv"
        response.headers["Content-type"] = "text/csv"
        return response
    else:
        return redirect("/dashboard")


@app.route("/customizations", methods=["GET", "POST"])
@login_required
@lecturer_only
def customizingQuestions():
    lecturerId = session.get("id")
    layouts = df.getProfiles(lecturerId)
    return render_template("customizingQuestions.html", name=session.get("username"), layouts=layouts,role = session.get("role"))

@app.route("/addProfiles", methods=["GET", "POST"])
@login_required
@lecturer_only
def addProfiles():
    if request.method == "POST":
        lecturerId = session.get("id")
        profileName = request.form.get("profileName")
        df.addProfile(profileName, lecturerId)
        return redirect("/customizations")
    else:
        return redirect("/dashboard")
    
@app.route("/deleteProfile", methods=["GET", "POST"])
@login_required
@lecturer_only
def deleteProfile():
    if request.method == "POST":
        lecturerId = session.get("id")
        layoutId = request.form.get("layoutId")
        df.deleteProfile(layoutId, lecturerId)
        return redirect("/customizations")
    else:
        return redirect("/dashboard")
    
@app.route("/addQuestion", methods=["GET", "POST"])
@login_required
@lecturer_only
def addQuestion():
    if request.method == "POST":
        lecturerId = session.get("id")
        layoutId = request.form.get("layoutId")
        question = request.form.get("question")
        df.addQuestions(question, lecturerId, layoutId)
        return redirect("/customizations")
    else:
        return redirect("/dashboard")

@app.route("/deleteQuestion", methods=["GET", "POST"])
@login_required
@lecturer_only
def deleteQuestion():
    if request.method == "POST":
        lecturerId = session.get("id")
        layoutId = request.form.get("layoutId")
        questionId = request.form.get("questionId")
        df.deleteQuestion(questionId, layoutId, lecturerId)
        return redirect("/customizations")
    else:
        return redirect("/dashboard")

@app.route("/previewLayout", methods=["GET", "POST"])
@login_required
@lecturer_only
def previewLayout():
    if request.method == "POST":
        lecturerId = session.get("id")
        courseId = request.form.get("courseId")
        courseCode = request.form.get("courseCode")
        courseName = request.form.get("courseName")
        layouts = df.getProfiles(lecturerId)
        layoutId ,questions = df.getCurrentQuestions(courseId)
        intro = df.getIntro(courseId)
        return render_template("previewLayout.html", name=session.get("username"), layouts=layouts,questions=questions,courseId=courseId,courseCode=courseCode,courseName=courseName,layoutId=layoutId,role = session.get("role"),introduction = intro)
    else:
        return redirect("/dashboard")

@app.route("/changePreviewQuestion",methods=["GET","POST"])
@login_required
@lecturer_only
def changePreviewQuestion():
    if request.method == "POST":
        courseId = request.form.get("courseId")
        lecturerId = session.get("id")
        layoutId = request.form.get("selectedLayout")
        courseCode = request.form.get("courseCode")
        courseName = request.form.get("courseName")
        intro = df.getIntro(courseId)
        questions = df.getQuestions(lecturerId, layoutId)
        return render_template("previewLayout.html", name=session.get("username"), questions=questions, layoutId=layoutId,layouts=df.getProfiles(lecturerId),courseId=courseId,courseCode=courseCode,courseName=courseName,role = session.get("role"),introduction = intro)
    else:
        return redirect("/dashboard")

@app.route("/changeDbLayout",methods=["GET","POST"])
@login_required
@lecturer_only
def changeDbLayout():
    if request.method == "POST":
        courseId = request.form.get("courseId")
        layoutId = request.form.get("layoutId")
        df.changeLayout(layoutId,courseId)
        return redirect("/dashboard")
    else:
        return redirect("/dashboard")


@app.route("/finalMarkCalculations",methods=["GET","POST"])
@login_required
@lecturer_only
def finalMarkCalculations():
    if request.method == "POST":
        studentId = request.form.get("studentId")
        studentName = request.form.get("studentName")
        courseId = request.form.get("courseId")
        sectionId = request.form.get("sectionId")
        return render_template("finalMarkCalculations.html", name=session.get("username"), studentId=studentId,studentName = studentName, courseId=courseId, sectionId=sectionId,role = session.get("role"))
    else:
        return redirect("/dashboard")

@app.route("/lecturerRating", methods=["GET", "POST"])
@login_required
@lecturer_only
def lecturerRating():
    if request.method == "POST":
        studentId = request.form.get("studentId")
        sectionId = request.form.get("sectionId")
        lecturerRatingValue = request.form.get("lecturerRating")
        return df.insertLecturerRating(session.get("id"),studentId, sectionId, lecturerRatingValue)
    else:
        return redirect("/dashboard")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

@app.route("/deleteCourse", methods=["GET", "POST"])
@login_required
@lecturer_only
def deleteCourse():
    if request.method == "POST":
        courseId = request.form.get("courseId")
        df.deleteCourse(courseId,session.get("id"))
        return redirect("/dashboard")

@app.route("/changeIntro",methods = ["GET","POST"])
@login_required
@lecturer_only
def changeIntro():
    if request.method == "POST":
        courseId = request.form.get("courseId")
        intro = request.form.get("introChangeText")
        df.changeIntro(courseId,intro)
        return redirect("/dashboard")


@app.route("/downloadFile")
@login_required
@lecturer_only
def downloadFile():
    csv_path = './example.csv'
    return send_file(csv_path,as_attachment=True,download_name="example.csv")

@app.route("/changeReviewDate",methods=["GET","POST"])
@login_required
@lecturer_only
def changeReviewDate():
    if request.method == "POST":
        courseId = request.form.get("courseId")
        sectionId = request.form.get("sectionId")
        startDate = request.form.get("startDate")
        endDate = request.form.get("endDate")
        df.changeReviewDate(courseId,sectionId,startDate,endDate)
        flash("Review date has been set")
        return redirect("/dashboard")
    else:
        return redirect("/dashboard")


@app.route("/changeReviewDateForCourse",methods=["GET","POST"])
@login_required
@lecturer_only
def changeReviewDateForCourse():
    if request.method == "POST":
        courseId = request.form.get("courseId")
        startDate = request.form.get("startDate")
        endDate = request.form.get("endDate")
        df.changeReviewDateForCourse(courseId,startDate,endDate)
        flash("Review date has been set")
        return redirect("/dashboard")
    else:
        return redirect("/dashboard")
    
def send_password_reset_email(email, token):
    msg = Message('Password Reset Request', sender='studentpeerreviewsystem@gmail.com', recipients=[email])
    msg.body = f"Click the following link to reset your password: {url_for('resetPassword', token=token, _external=True)}"
    mail.send(msg)

# F5 to run flask and auto refresh
if __name__ == "__main__":
    app.run(debug=True,host="localhost")
       # has auto refresh now
