import sqlite3
import csv
import re # this is regex (regular expression)
import secrets   # generate random string for password initially
from werkzeug.security import check_password_hash, generate_password_hash  #hashes passwords

from flask import flash,redirect

con = sqlite3.connect("database.db", check_same_thread=False)      # connects to the database
db = con.cursor()                         # cursor to go through database (allows db.execute() basically)


# Hard coded KEYS just in case
KEYS = ["id","email","name"]
CSV_KEYS = ["email","name","section-group"]
NEW_USER_KEYS = ["email","name","password"]
ROLES = ["STUDENT","LECTURER"]


# Copy this function into the main code
# writes database data into a csv file
def databaseToCsv():
  users = db.execute("SELECT * FROM users")
  users = db.fetchall()          # gathers all users
  with open("usersInDatabase.txt", "w", newline='') as file:    # opens txt file and newline is empty to prevent "\n"
    writer = csv.writer(file)                               # creates writer to write into file as csv
    
    # Write table headers with hardcoded KEYS
    writer.writerow(KEYS) 
    
    # Write data rows
    for user in users:
      writer.writerow(user[0:3] + (user[4],))
  file.close()


# inputs csv files into the database
def csvToDatabase():
  existingEmails = db.execute("SELECT email FROM users")
  existingEmails = list({email[0] for email in existingEmails})    # turn existing users into a list
  with open("addToDatabase.txt", newline="") as file:
    studentsToGroup = []
    reader = csv.reader(file)
    header =  next(reader)
    if header != CSV_KEYS:                      # checks if header of csv matches database
      flash(f"Invalid CSV format. Header does not match expected format.\n Using: {header} \n Change to : {CSV_KEYS}")
      return
    for row in reader:   # loops through each row in the csv
      foundEmptyValue = False     # flag for empty values
      if len(row) != len(CSV_KEYS):    # check for missing coloumns
        flash(f"Missing coloumn found in row {row}. Skipping...")
        foundEmptyValue = True
        continue
      for data in row:         
        if not data:         #checks if data coloumn is empty      
          foundEmptyValue = True
          flash(f"Empty value found in row {row}. Skipping...")
          break

      if foundEmptyValue == True:
        continue                   # skips this cycle of the loop
      
      # get current userid and name
      userEmail = row[0] 
      name = row[1]
      role = "STUDENT"
      
      # check if user Role exists
      if role not in ROLES:      
        flash(f"Role {role} does not exist.")
        continue
      
      # if user not already existing and not empty row
      elif ( userEmail) not in existingEmails and row:
        db.execute("INSERT INTO users (email,name,role) VALUES(?,?,?)",(userEmail,name,role))
        con.commit()
      userId = db.execute("SELECT id FROM users WHERE email = ?", (userEmail,)).fetchone()[0]
      sectionId = row[2].split("-")[0]
      groupNum = row[2].split("-")[1]
      addIntoGroups(sectionId,groupNum,userId)


  file.close()


# verifies incoming user
def checkUser(email, password, session):
  existingEmails = db.execute("SELECT email FROM users")
  existingEmails = list({email[0] for email in existingEmails})    # turn existing users into a list
  if email not in existingEmails:
    flash("Not inside database, consult with your lecturer")
  else:
    verifiedPasword = db.execute("SELECT password FROM users WHERE email=?", (email,))
    verifiedPasword = db.fetchone()
    if check_password_hash(verifiedPasword[0], password) == True:
      user = db.execute("SELECT * FROM users WHERE email =?", (email,))
      user = db.fetchone()
      session["username"] = user[2]
      session["role"] = user[4]
      session["email"] = email
    else:
      flash("Wrong Password")


# add students to class (if not there)
def addIntoClasses():
  courses = db.execute("SELECT * FROM courses")  # change this to integrate into website(select from user input)
  courses = db.fetchall()
  course = courses[0] #courseID

  students = db.execute("SELECT * FROM users WHERE role = ?",("STUDENT",))
  students = db.fetchall()
  maxStudents = int(course[4])

  # sets the other headers
  courseId ,lecturerId, lectureOrTutorial,sectionId = course[0],course[2],course[5],course[6]
  studentsInClass = db.execute("SELECT studentId FROM classes WHERE courseId = ? AND lectureOrTutorial = ? AND sectionId = ?" ,(courseId,lectureOrTutorial,sectionId))
  studentsInClass = [row[0] for row in studentsInClass.fetchall()]
  if len(students) < maxStudents:
    for student in students:
      studentId = student[0]
      studentName = student[1]
      if studentId not in studentsInClass:
        db.execute('INSERT INTO classes (courseId,lecturerId,studentId,lectureOrTutorial,sectionId) VALUES(?,?,?,?,?)', (courseId,lecturerId,studentId,lectureOrTutorial,sectionId))
        con.commit()
        flash("Added to classes")
      else:
        flash("Student already exists")


# checks if user is in a group
def isUserInGroup(studentId, courseId, sectionId):
  # Query the database to check if the student is already in any group for the specified course, trimester, and section
  existing_group = db.execute("SELECT * FROM studentGroups WHERE courseId = ? AND sectionId = ? AND membersStudentId LIKE ?", (courseId, sectionId, f"%{studentId}%"))
  existing_group = db.fetchone()
  return existing_group is not None


def addIntoGroups(studentSectionId,groupNumber,userId):
  groupNumber = int(groupNumber)
  courses = db.execute("SELECT * FROM courses")  # Assuming this fetches courses based on user input
  courses = db.fetchall()
  course = courses[0]
  courseId,groupNum, sectionId, memberLimit = course[0],course[5],course[7],int(course[8])
  if studentSectionId == sectionId and groupNumber<=groupNum and groupNumber>0 and isUserInGroup(userId, courseId, studentSectionId) == False:
    db.execute("INSERT into studentGroups (courseId,sectionId,groupNum,membersStudentId) VALUES(?,?,?,?)",(courseId,studentSectionId,groupNumber,userId))
    con.commit()
    flash("Added to group")


# gets the courses the current user's is registered in
def getRegisteredCourses(studentId):
  classes = db.execute("SELECT courseId FROM classes WHERE studentId = ?", (studentId,))
  classes = db.fetchall()
  coursesId = [row[0] for row in classes]
  registeredClasses = []
  for course in coursesId:
    db.execute("SELECT courseName,courseCode FROM courses WHERE id = ?", (course,))
    courseName = db.fetchone()
    wholeCourseName = courseName[1],courseName[0],course
    registeredClasses.append(wholeCourseName)
  return registeredClasses

def getRegisteredCourseData(studentId):
  group = db.execute("SELECT courseId,sectionId,groupNum FROM studentGroups WHERE membersStudentId LIKE ?", (studentId,)).fetchall()[0]
  return group

# adds a course to the database
def addingClasses(courseCode, courseName,session):
  currentcourses = db.execute("SELECT courseCode,courseName FROM courses")
  currentcourses = db.fetchall()
  courseExists = False
  for currentcourse in currentcourses:
    if str(courseCode) == currentcourse[0]:
      courseExists = True
    else:
      courseExists = False
  if courseExists == False:
    db.execute('INSERT INTO courses (courseCode,courseName,lecturerId,studentNum,groupNum,lectureOrTutorial,sessionCode,membersPerGroup) VALUES(?,?,?,?,?,?,?,?)', (courseCode,courseName,session.get("id"),30,10,"LECTURE","TT3L",3))
    con.commit()
    flash("Successfully added course.")
    return redirect("/dashboard")
  else: 
    flash("Course already exists.")
    return redirect("/dashboard")



#adds user to database
def addUserToDatabase(email, username):
  existingEmails = db.execute("SELECT email FROM users")
  existingEmails = list({email[0] for email in existingEmails})    # turn existing users into a list
  if email in existingEmails:
    return db.execute("SELECT role FROM users WHERE email = ?", (email,)).fetchone()[0]
  userId = email.split("@")[0]
  if userId.startswith("MU"):
    role = "LECTURER"
  else:
    role = "STUDENT"
  db.execute("INSERT INTO users (email,name,role) VALUES(?,?,?)",(email,username,role))
  con.commit()
  return role

def getRole(email):
  return db.execute("SELECT role FROM users WHERE email = ?", (email,)).fetchone()[0]

# gets number and members of the group
def getMembers(session):
  # Get the current user's details
  currentStudentId = session.get("id")
  # Get the class details for the current student
  # make it so that it understands the current student's class on button clicked
  courseId = session.get("courseId")
  sectionId,groupNum = getReviewCourse(session.get("courseId"),currentStudentId)
  classes = db.execute("SELECT membersStudentId FROM studentGroups WHERE courseId=? AND sectionId =? AND groupNum =? ", (courseId,sectionId,groupNum))
  classes = db.fetchall()
  # grabs Ids of the members
  memberIdList = [member[0] for member in classes ]
  for memberId in memberIdList:
    member = db.execute("SELECT name FROM users WHERE id = ?", (memberId,))
    memberIdList[memberIdList.index(memberId)] = member.fetchone()[0]
  return memberIdList,classes

def reviewIntoDatabase(courseId,sectionId,groupNum,reviewerId,revieweeId,reviewScore,reviewComment):
  reviewExists = db.execute("SELECT * FROM reviews WHERE courseId = ? AND sectionId = ? AND groupNum = ? AND reviewerId = ? AND revieweeId = ?",(courseId,sectionId,groupNum,reviewerId,revieweeId)).fetchone()
  if reviewExists:
    db.execute("UPDATE reviews SET reviewScore = ?, reviewComment = ? WHERE courseId = ? AND sectionId = ? AND groupNum = ? AND reviewerId = ? AND revieweeId = ?",(reviewScore,reviewComment,courseId,sectionId,groupNum,reviewerId,revieweeId))
    message = "Review updated in database"
  else:
    db.execute("INSERT INTO reviews (courseId,sectionId,groupNum,reviewerId,revieweeId,reviewScore,reviewComment) VALUES(?,?,?,?,?,?,?)",(courseId,sectionId,groupNum,reviewerId,revieweeId,reviewScore,reviewComment))
    message  = "Review added to database"
  con.commit()
  return message

# db.execute("CREATE TABLE IF NOT EXISTS selfAssessment (courseId TEXT NOT NULL,sectionId TEXT NOT NULL,groupNum TEXT NOT NULL,reviewerId INTEGER NOT NULL,)")
def getUserId(userEmail):
  return db.execute("SELECT id FROM users WHERE email = ?", (userEmail,)).fetchone()[0]

def selfAssessmentIntoDatabase(courseId,sectionId,groupNum,reviewerId,groupSummary,challenges,secondChance,roleLearning,feedback):
  selfAssessmentExists = db.execute("SELECT * FROM selfAssessment WHERE courseId = ? AND sectionId = ? AND groupNum = ? AND reviewerId = ?",(courseId,sectionId,groupNum,reviewerId)).fetchone()
  if selfAssessmentExists:
    db.execute("UPDATE selfAssessment SET groupSummary = ?, challenges = ?, secondChance = ?, roleLearning = ?, feedback = ? WHERE courseId = ? AND sectionId = ? AND groupNum = ? AND reviewerId = ?",(groupSummary,challenges,secondChance,roleLearning,feedback,courseId,sectionId,groupNum,reviewerId))
    message = "Self Assessment updated in database"
  else:
    db.execute("INSERT INTO selfAssessment (courseId,sectionId,groupNum,reviewerId,groupSummary,challenges,secondChance,roleLearning,feedback) VALUES(?,?,?,?,?,?,?,?,?)",(courseId,sectionId,groupNum,reviewerId,groupSummary,challenges,secondChance,roleLearning,feedback))
    message = "Self Assessment added to database"
  con.commit()
  flash(f"{message}")

def getReviewCourse(courseId,reviewerId):
  course = db.execute("SELECT * FROM studentGroups WHERE membersStudentId =?",(reviewerId,)).fetchall()
  if course:
    course = course[0]
  else:
    flash("No course found")
    return redirect("/dashboard")
  return course[1],course[2]


def getStudentRatings(courseId,sectionId,groupNum,studentId):
  studentRatings = db.execute("SELECT * FROM reviews WHERE courseId =? AND sectionId = ? AND groupNum = ? revieweeId = ?",(courseId,sectionId,groupNum,studentId,)).fetchall()
  # put function here to adjust the ratings
  return studentRatings