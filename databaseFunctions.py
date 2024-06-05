import sqlite3
import csv
from flask import flash,redirect

from flask import flash,redirect

con = sqlite3.connect("database.db", check_same_thread=False)      # connects to the database
db = con.cursor()                         # cursor to go through database (allows db.execute() basically)


# Hard coded KEYS just in case
KEYS = ["id","email","name"]
CSV_KEYS = ["ï»¿email","name","section-group"]
CSV_CLEAN = ["email","name","section-group"]
ROLES = ["STUDENT","LECTURER"]

# inputs csv files into the database
def csvToDatabase(courseId, lecturerId,filename):
    existingEmails = db.execute("SELECT email FROM users").fetchall()
    existingEmails = list({email[0] for email in existingEmails})
    message= None
    with open(filename, newline="") as file:
        studentsToGroup = []
        reader = csv.reader(file)
        i = 0
        for row in reader:
            if i == 0:
                if row != CSV_KEYS:
                    message=f"Incorrect CSV file format. Please use the following format: {CSV_CLEAN}"
                    deleteFromCourses(courseId,lecturerId,message)
                    return message
                i += 1
                continue
            foundEmptyValue = False
            if len(row) != len(CSV_KEYS):
                message=f"Missing column found in row {row}. Skipping..."
                deleteFromCourses(courseId,lecturerId,message)
                return message
            for data in row:
                if not data:
                    foundEmptyValue = True
                    message=f"Empty value found in row {row}. Skipping..."
                    deleteFromCourses(courseId,lecturerId,message)
                    return message
            if foundEmptyValue:
                continue
            userEmail = row[0]
            name = row[1]
            role = "STUDENT"
            if (userEmail) not in existingEmails and row:
                db.execute("INSERT INTO users (email,name,role) VALUES(?,?,?)", (userEmail, name, role))
                con.commit()
            userId = db.execute("SELECT id FROM users WHERE email = ?", (userEmail,)).fetchone()[0]
            sectionCode = row[2].split("-")[0]
            groupNum = row[2].split("-")[1]
            groupId = addIntoGroups(groupNum,courseId,sectionCode)
            addIntoStudentGroups(groupId,userId)
    file.close()
    return message

def addIntoGroups(groupNum,courseId,sectionCode):
    sectionId = db.execute("SELECT id FROM sections WHERE sectionCode = ? AND courseId = ?",(sectionCode,courseId)).fetchone()[0]
    existingGroup = db.execute("SELECT * FROM groups WHERE groupName =? AND courseId =? AND sectionId =?", (groupNum,courseId, sectionId)).fetchone()
    if existingGroup is None:
        db.execute("INSERT INTO groups (courseId, sectionId, groupName) VALUES(?,?,?)", (courseId, sectionId, groupNum))
        con.commit()
    groupId = db.execute("SELECT id FROM groups WHERE groupName = ? AND courseId = ? AND sectionId = ?", (groupNum,courseId, sectionId)).fetchone()[0]
    return groupId

def addIntoStudentGroups(groupId,userId):
    existingStudentGroup = db.execute("SELECT * FROM studentGroups WHERE groupId =? AND studentId LIKE ?", (groupId, f"%{userId}%")).fetchone()
    if existingStudentGroup is None:
        db.execute("INSERT INTO studentGroups (groupId, studentId) VALUES(?,?)", (groupId, userId))
        con.commit()


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
def addingClasses(courseId, courseName,session):
  currentcourses = db.execute("SELECT * FROM courses WHERE courseCode =?",courseId).fetchall()
  currentcourses = db.fetchall()
  courseExists = False
  for currentcourse in currentcourses:
    if str(courseId) == currentcourse[0]:
      courseExists = True
    else:
      courseExists = False
  if courseExists == False:
    db.execute('INSERT INTO courses (courseId, courseName,lecturerEmail,studentNum,groupNum,lectureOrTutorial,sessionCode,membersPerGroup) VALUES(?,?,?,?,?,?,?,?)', (courseId, courseName,session.get("email"),30,10,"LECTURE","TT3L",3))
    con.commit()
    flash("Successfully added course.")
    return redirect("/")
  else: 
    flash("Course already exists.")
    return redirect("/addingCourses")

  # make function for add class groups button



#adds user to database
def addUserToDatabase(email, username):
  existingEmails = db.execute("SELECT email FROM users")
  existingEmails = list({email[0] for email in existingEmails})    # turn existing users into a list
  if email in existingEmails:
    return db.execute("SELECT role FROM users WHERE email = ?", (email,)).fetchone()[0]
  mailEnding = email.split("@")[1]
  if mailEnding.startswith("student"):
    role = "STUDENT"
  else:
    role = "LECTURER"
  db.execute("INSERT INTO users (email,name,role) VALUES(?,?,?)",(email,username,role))
  con.commit()
  return role



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
    message = "update"
  else:
    db.execute("INSERT INTO reviews (courseId,sectionId,groupNum,reviewerId,revieweeId,reviewScore,reviewComment) VALUES(?,?,?,?,?,?,?)",(courseId,sectionId,groupNum,reviewerId,revieweeId,reviewScore,reviewComment))
    message  = "add"
  con.commit()
  insertFinalRating(courseId,sectionId,groupNum,revieweeId)
  return message

# db.execute("CREATE TABLE IF NOT EXISTS selfAssessment (courseId TEXT NOT NULL,sectionId TEXT NOT NULL,groupNum TEXT NOT NULL,reviewerId INTEGER NOT NULL,)")
def getUserId(userEmail):
  return db.execute("SELECT id FROM users WHERE email = ?", (userEmail,)).fetchone()[0]

def selfAssessmentIntoDatabase(courseId,questionId,question,answer,reviewerId):
  selfAssessmentExists = db.execute("SELECT * FROM selfAssessment WHERE courseId = ? AND questionId=? AND reviewerId =?",(courseId,questionId,reviewerId)).fetchone()
  if selfAssessmentExists:
    db.execute("UPDATE selfAssessment SET answer=? WHERE courseId = ? AND questionId=? AND reviewerId = ?",(answer,courseId,questionId,reviewerId))
    message = "update"
  else:
    db.execute("INSERT INTO selfAssessment (courseId,questionId,question,answer,reviewerId) VALUES(?,?,?,?,?)",(courseId,questionId,question,answer,reviewerId))
    message = "add"
  con.commit()
  return message

def getReviewCourse(courseId,reviewerId):
  course = db.execute("SELECT * FROM studentGroups WHERE membersStudentId =?",(reviewerId,)).fetchall()
  if course:
    course = course[0]
  else:
    flash("No course found")
    return redirect("/dashboard")
  return course[1],course[2]

def getLecturerCourses(lecturerId):
  courses = db.execute("SELECT DISTINCT courseName FROM courses WHERE lecturerId = ?",(lecturerId,)).fetchall()
  registeredClasses = []
  for course in courses:
    db.execute("SELECT DISTINCT courseCode FROM courses WHERE lecturerId = ? AND courseName =?", (lecturerId,course[0]))
    courseName = db.fetchone()[0]
    wholeCourseName = courseName,course[0]
    registeredClasses.append(wholeCourseName)
  return registeredClasses

def getStudentGroups(courseId,sectionId):
  groups = db.execute("SELECT DISTINCT groupNum FROM studentGroups WHERE courseId = ? AND sectionId = ?",(courseId,sectionId)).fetchall()
  studentGroups = db.execute("SELECT groupNum,membersStudentId FROM studentGroups WHERE courseId = ? AND sectionId = ?",(courseId,sectionId)).fetchall()
  groupedStudents = []
  for group in groups:
    students = [group[0]]
    for studentGroup in studentGroups:
      if group[0] == studentGroup[0]:
        name = db.execute("SELECT name FROM users WHERE id = ?",(studentGroup[1],)).fetchone()[0]
        data = studentGroup[1],name,getStudentRatings(courseId,sectionId,group[0],studentGroup[1]),getStudentReview(courseId,sectionId,group[0],studentGroup[1]),getSelfAssessment(courseId,studentGroup[1]),getLecturerRating(courseId,studentGroup[1])
        students.append(data)
    groupedStudents.append(students)
  return(groupedStudents)

def getLecturerRating(courseId,studentId):
  rating = db.execute("SELECT lecturerFinalRating FROM lecturerRatings WHERE courseId = ? AND studentId = ?",(courseId,studentId)).fetchone()
  if rating:
    return rating[0]
  else:
    return None
      

# Use this function for the lecturer to get the ratings for students
def insertFinalRating(courseId,sectionId,groupNum,studentId):
  studentRatings = db.execute("SELECT * FROM reviews WHERE courseId =? AND sectionId = ? AND groupNum = ? AND revieweeId = ?",(courseId,sectionId,groupNum,studentId,)).fetchall()
  totalRating = 0  # keep track of total rating
  studentNum = db.execute("SELECT membersPerGroup FROM courses WHERE id = ?",(courseId,)).fetchone()[0]
  if len(studentRatings) < studentNum:
    return "Not reviewed by all students yet"
  for rating in studentRatings:
    totalRating += rating[5]
  # put function here to adjust the ratings
  totalRating = totalRating/len(studentRatings)
  if db.execute("SELECT * FROM finalRatings WHERE courseId = ? AND sectionId = ? AND groupNum = ? AND studentId = ?",(courseId,sectionId,groupNum,studentId)).fetchone():
    db.execute("UPDATE finalRatings SET finalRating = ? WHERE courseId = ? AND sectionId = ? AND groupNum = ? AND studentId = ?",(round(totalRating,2),courseId,sectionId,groupNum,studentId))
  else:
    db.execute("INSERT INTO finalRatings (courseId,sectionId,groupNum,studentId,finalRating) VALUES(?,?,?,?,?)",(courseId,sectionId,groupNum,studentId,round(totalRating,2)))
  con.commit()

def getCurrentLecturerCourse(lecturerId,subjectCode,subjectName):
  course = db.execute("SELECT * FROM courses WHERE lecturerId = ? AND courseCode = ? AND courseName =?",(lecturerId,subjectCode,subjectName)).fetchall()
  return(course)

def getStudentRatings(courseId,sectionId,groupNum,studentId):
  finalRating = db.execute("SELECT finalRating FROM finalRatings WHERE courseId = ? AND sectionId = ? AND groupNum = ? AND studentId = ?",(courseId,sectionId,groupNum,studentId)).fetchone()
  if finalRating:
    return finalRating[0]
  else:
    return "Not reviewed by all students yet"

def getStudentReview(courseId,sectionId,groupNum,studentId):
  studentRatings = db.execute("SELECT * FROM reviews WHERE courseId =? AND sectionId = ? AND groupNum = ? AND revieweeId = ?",(courseId,sectionId,groupNum,studentId,)).fetchall()
  totalRating = 0  # keep track of total rating
  studentNum = db.execute("SELECT membersPerGroup FROM courses WHERE id = ?",(courseId,)).fetchone()[0]
  if len(studentRatings) < studentNum:
    return None
  reviews = db.execute("SELECT revieweeId,reviewScore,reviewComment FROM reviews WHERE courseId = ? AND sectionId = ? AND groupNum = ? AND reviewerId = ?",(courseId,sectionId,groupNum,studentId)).fetchall()
  listReviews = []
  for review in reviews:
    student = [review[0],review[1],review[2]]
    listReviews.append(student)
  return listReviews

def getSelfAssessment(courseId,studentId):
  selfAssessment = db.execute("SELECT * FROM selfAssessment WHERE courseId = ? AND reviewerId = ?",(courseId,studentId)).fetchall()
  if selfAssessment:
    return selfAssessment
  else:
    return None


def getProfiles(lecturerId):
  default = db.execute("SELECT id, layoutName FROM questionLayouts WHERE lecturerId = 0").fetchall()
  profiles = db.execute("SELECT id, layoutName FROM questionLayouts WHERE lecturerId = ?",(lecturerId,)).fetchall()

  profiles = default + profiles

  result = []
  for profile in profiles:
    layoutId = profile[0]
    layoutName = profile[1]

    layoutQuestions = db.execute("SELECT id,question FROM questions WHERE layoutId = ?",(layoutId,)).fetchall()

    questions = []
    for q in layoutQuestions:
      questionId = q[0]
      question = q[1]
      questions.append({"id": questionId,"question": question})

    result.append({"id": layoutId,"layoutName": layoutName,"layoutQuestions": questions} )
  return result

def addProfile(layoutName,lecturerId):
  db.execute("INSERT INTO questionLayouts (layoutName, lecturerId) VALUES(?,?)",(layoutName,lecturerId,)).fetchall()
  con.commit()
  flash("Profile added")

def deleteProfile(layoutId,lecturerId):
  db.execute("DELETE FROM questionLayouts WHERE id = ? AND lecturerId = ?",(layoutId,lecturerId,)).fetchall()
  db.execute("DELETE FROM questions WHERE layoutId = ?",(layoutId,))
  con.commit()
  flash("Profile deleted")

def addQuestions(question,lecturerId,layoutId):
  db.execute("INSERT INTO questions (question,lecturerId,layoutId) VALUES(?,?,?)",(question,lecturerId,layoutId)).fetchall()
  con.commit()
  flash("Question added")
   
def deleteQuestion(questionId,layoutId,lecturerId):
  question = db.execute("SELECT question FROM questions WHERE id = ? AND lecturerId = ? AND layoutId = ?",(questionId,lecturerId,layoutId,)).fetchone()

  print(question, questionId, layoutId, lecturerId)
  if question:
    db.execute("DELETE FROM questions WHERE id = ? AND lecturerId = ? AND layoutId = ?",(questionId,lecturerId,layoutId,)).fetchall()
    con.commit()
    flash("Question deleted")
  else:
    flash("Question ID Invalid")

def addCourseToDb(courseId, courseName, lecturerId,sectionId):
    message =""
    currentcourses = db.execute("SELECT * FROM courses WHERE courseCode =? AND courseName=? AND lecturerId =?", (courseId,courseName,lecturerId)).fetchall()
    if not currentcourses:
      db.execute('INSERT INTO courses (courseCode, courseName, lecturerId) VALUES (?, ?, ?)', 
                  (courseId, courseName, lecturerId))
      con.commit()
      message = "Course added"
    courseId = db.execute("SELECT id FROM courses WHERE courseCode = ? AND courseName = ? AND lecturerId = ?",(courseId,courseName,lecturerId)).fetchone()[0]
    currentSections = db.execute("SELECT * FROM sections WHERE sectionCode = ? AND courseId = ?",(sectionId,courseId)).fetchall()
    if not currentSections:
      db.execute("INSERT INTO sections (sectionCode,courseId) VALUES(?,?)",(sectionId,courseId))
      con.commit()
      message = "Section added"
    return message,courseId
    

def extract_section_ids(filepath):
    section_ids = set()
    with open(filepath, newline="") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) < 3:
                raise ValueError("Missing section ID in CSV row")
            section_id = row[2].split("-")[0]
            section_ids.add(section_id)
    return section_ids

def insertLecturerRating(lecturerId,studentId,courseId,lecturerFinalRating):
  rating = db.execute("SELECT * FROM lecturerRatings WHERE lecturerId = ? AND studentId = ? AND courseId =? ",(lecturerId,studentId,courseId)).fetchone()
  if rating:
    db.execute("UPDATE lecturerRatings SET lecturerFinalRating = ? WHERE lecturerId = ? AND studentId = ? AND courseId = ?",(lecturerFinalRating,lecturerId,studentId,courseId))
    flash("Updated Lecturer Rating.")
  else:
    db.execute("INSERT INTO lecturerRatings (lecturerId,studentId,courseId,lecturerFinalRating) VALUES(?,?,?,?)",(lecturerId,studentId,courseId,lecturerFinalRating))
    flash("Added Lecturer Rating.")
  con.commit()
  
  return redirect("/dashboard")

def getCourseId(courseCode, courseName,sectionId,lecturerId):
  course = db.execute("SELECT id FROM courses WHERE courseCode = ? AND courseName = ? AND sessionCode = ? AND lecturerId = ?",(courseCode,courseName,sectionId,lecturerId)).fetchone()
  return course[0]

def getQuestions(lecturerId,layoutId):
  questions = db.execute("SELECT id,question FROM questions WHERE layoutId = ?",(layoutId,)).fetchall()
  return questions

def getCurrentQuestions(lecturerId, courseCode,courseName):
  layoutId = db.execute("SELECT layoutId FROM courses WHERE lecturerId = ? AND courseCode = ? AND courseName =?",(lecturerId,courseCode,courseName)).fetchone()[0]
  questions = db.execute("SELECT id,question FROM questions WHERE layoutId = ?",(layoutId,)).fetchall()
  return layoutId,questions

def changeLayout(layoutId,lecturerId,courseCode,courseName):
  db.execute("UPDATE courses SET layoutId = ? WHERE lecturerId = ? AND courseCode = ? AND courseName =?",(layoutId,lecturerId,courseCode,courseName))
  con.commit()
  flash("Layout changed")

def getReviewQuestions(courseId):
  layoutId = db.execute("SELECT layoutId FROM courses WHERE id = ?",(courseId,)).fetchone()[0]
  questions = db.execute("SELECT id,question FROM questions WHERE layoutId = ?",(layoutId,)).fetchall()
  return questions

def deleteCourse(courseCode,courseName,lecturerId):
  courseId = db.execute("SELECT id FROM courses WHERE courseCode = ? AND courseName = ? AND lecturerId = ?",(courseCode,courseName,lecturerId)).fetchall()
  for course in courseId:
    db.execute("DELETE FROM courses WHERE id = ?",(course[0],))
    db.execute("DELETE FROM classes WHERE courseId = ?",(course[0],))
    db.execute("DELETE FROM studentGroups WHERE courseId = ?",(course[0],))
    db.execute("DELETE FROM finalRatings WHERE courseId = ?",(course[0],))
    db.execute("DELETE FROM reviews WHERE courseId = ?",(course[0],))
    db.execute("DELETE FROM selfAssessment WHERE courseId = ?",(course[0],))
    con.commit()
  flash(f"Course {courseCode} {courseName} deleted")

def deleteFromCourses(courseCode,courseName,lecturerId,message):
  courseId = db.execute("SELECT id FROM courses WHERE courseCode = ? AND courseName = ? AND lecturerId = ?",(courseCode,courseName,lecturerId)).fetchall()
  for course in courseId:
    db.execute("DELETE FROM courses WHERE id = ?",(course[0],))
    con.commit()
  return redirect("/addingCourses")
