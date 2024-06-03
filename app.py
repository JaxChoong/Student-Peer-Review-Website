from flask import Flask, flash, redirect, render_template, session, abort ,request, url_for, get_flashed_messages,jsonify
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from functools import wraps
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
import ast

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
@lecturer_only
def studentGroups():
    lecturerId = session.get("id")
    if request.method == "POST":
        courseId = request.form.get("courseId")
        courseId = courseId[1:-1].split(",")
        subjectCode,subjectName = courseId[0][1:-1] ,courseId[1][2:-1]
        currentCourseSection = df.getCurrentLecturerCourse(lecturerId,subjectCode,subjectName)
        studentGroups=[]
        for section in currentCourseSection:
            currentCourseId = df.getCourseId(subjectCode,subjectName,section[7],lecturerId)
            studentGroups.append([section[7],df.getStudentGroups(section[0],section[7]),currentCourseId])
        courseId = df.getCourseId(subjectCode,subjectName,currentCourseSection[0][7],lecturerId)
    return render_template("studentgroup.html" ,name=session.get("username"),studentGroups=studentGroups,courseSection=currentCourseSection,subjectCode=subjectCode,subjectName=subjectName,courseId= courseId,role = session.get("role"))

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
            for question in questions:
                question_id = request.form.get(f"questionId{question[0]}")
                question_text = request.form.get(f"questionText{question_id}")
                answer = request.form.get(f"answer{question_id}")
                message = df.selfAssessmentIntoDatabase(courseId, question_id, question_text, answer, reviewerId)
            flash(f"{message}")
            session.pop("courseId")
            session.pop("sectionId")
            session.pop("groupNum")
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
        courseData = request.form.get("courseId")[1:-1].split(",")
        courseId = courseData[2][2:-1]
        questions = df.getReviewQuestions(courseId)
        session["courseId"] = courseId
        session["sectionId"],session["groupNum"] = df.getReviewCourse(session.get("courseId"),session.get("id"))
        membersId,membersName = df.getMembers(session)
        # placeholder to check if student has been reviewed yet
        df.getStudentRatings(session.get("courseId"),session.get("sectionId"),session.get("groupNum"),session.get("id"))
        return render_template("studentPeerReview.html", name=session.get("username"), members=membersId,questions=questions,role = session.get("role"))

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

            courseId = request.form.get('courseId')
            courseName = request.form.get('courseName')
            lecturerId = session.get('id')

            try:
                sectionIds, lectureOrTutorial = df.extract_section_ids(filepath)
                studentNum = df.extract_student_num(filepath)
                groupNum, membersPerGroup = df.extract_group_num(filepath)
            except ValueError as e:
                return jsonify({'message': str(e), 'category': 'danger'}), 400

            try:
                # Insert course into the database
                for sectionId in sectionIds:
                    df.addCourseToDb(courseId, courseName, lecturerId, sectionId, studentNum, groupNum, lectureOrTutorial, membersPerGroup)

                # Process CSV to add students and groups
                message = df.csvToDatabase(courseId, courseName, lecturerId, sectionId, filepath, lectureOrTutorial)
                if message:
                    return jsonify({'message': message, 'category': 'danger'}), 400
                flash('Course and students successfully added.', 'success')
                return jsonify({'message': 'Course and students successfully added.', 'category': 'success'}), 200
            except Exception as e:
                return jsonify({'message': f'Error adding courses: {str(e)}', 'category': 'danger'}), 500
        else:
            return jsonify({'message': 'Invalid file format. Please upload a CSV file.', 'category': 'danger'}), 400

    return render_template('addCourses.html', name=session.get('username'),role = session.get("role"))




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
        return render_template("addProfile.html", name=session.get("username"),role = session.get("role"))
    
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
        return render_template("addQuestion.html", name=session.get("username"),role = session.get("role"))

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
        return render_template("deleteQuestion.html", name=session.get("username"),role = session.get("role"))

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
        layoutId ,questions = df.getCurrentQuestions(lecturerId, courseCode, courseName)
        return render_template("previewLayout.html", name=session.get("username"), layouts=layouts,questions=questions,courseId=courseId,courseCode=courseCode,courseName=courseName,layoutId=layoutId,role = session.get("role"))

@app.route("/changePreviewQuestion",methods=["GET","POST"])
@login_required
@lecturer_only
def changePreviewQuestion():
    if request.method == "POST":
        lecturerId = session.get("id")
        layoutId = request.form.get("selectedLayout")
        courseCode = request.form.get("courseCode")
        courseName = request.form.get("courseName")
        questions = df.getQuestions(lecturerId, layoutId)
        return render_template("previewLayout.html", name=session.get("username"), questions=questions, layoutId=layoutId,layouts=df.getProfiles(lecturerId),courseId=request.form.get("courseId"),courseCode=courseCode,courseName=courseName,role = session.get("role"))

@app.route("/changeDbLayout",methods=["GET","POST"])
@login_required
@lecturer_only
def changeDbLayout():
    if request.method == "POST":
        lecturerId = session.get("id")
        courseId = request.form.get("courseId")
        courseCode = request.form.get("courseCode")
        courseName = request.form.get("courseName")
        layoutId = request.form.get("layoutId")
        df.changeLayout(layoutId,lecturerId,courseCode,courseName)
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

@app.route("/calculateFinalMark",methods=["GET","POST"])
@login_required
@lecturer_only
def calculateFinalMark():
    if request.method == "POST":
        studentId = request.form.get("studentId")
        studentName = request.form.get("studentName")
        courseId = request.form.get("courseId")
        sectionId = request.form.get("sectionId")
        averageRating = df.getAverageRating(studentId,courseId,sectionId)
        lecturerRating = df.getLecturerRating(studentId,courseId,session.get("id"))
        assignmentMark = request.form.get("assignmentMark")
        finalMark = func.calculateFinalMark(averageRating,lecturerRating,assignmentMark)
        return render_template("finalMarkCalculations.html", name=session.get("username"), studentId=studentId,studentName = studentName, courseId=courseId, sectionId=sectionId,averageRating=averageRating,lecturerRating=lecturerRating,finalMark = finalMark,role = session.get("role"))

@app.route("/lecturerRating", methods=["GET", "POST"])
@login_required
@lecturer_only
def lecturerRating():
    studentId = request.form.get("studentId")
    courseId = request.form.get("courseId")
    sectionId = request.form.get("sectionId")
    lecturerRatingValue = request.form.get("lecturerRating")
    return df.insertLecturerRating(session.get("id"),studentId, courseId, lecturerRatingValue)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

@app.route("/deleteCourse", methods=["GET", "POST"])
@login_required
@lecturer_only
def deleteCourse():
    if request.method == "POST":
        courseName = request.form.get("courseName")
        courseCode = request.form.get("courseCode")
        df.deleteCourse(courseCode,courseName,session.get("id"))
        return redirect("/dashboard")


# F5 to run flask and auto refresh
if __name__ == "__main__":
    app.run(debug=True,host="localhost")
       # has auto refresh now
