import sqlite3
import csv
from flask import flash,redirect
import datetime
from flask import flash,redirect

con = sqlite3.connect("database.db", check_same_thread=False)      # connects to the database
db = con.cursor()                         # cursor to go through database (allows db.execute() basically)


# Hard coded KEYS just in case
KEYS = ["id","email","name"]
CSV_KEYS = ["ï»¿email","studentId","name","section-group"]
CSV_CLEAN = ["email","studentId","name","section-group"]
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
            studentId = row[1]
            print(studentId)
            name = row[2]
            role = "STUDENT"
            if (userEmail)  in existingEmails:
              db.execute("SELECT studentId FROM users WHERE email = ?", (userEmail,))
              existingStudentId = db.fetchone()[0]
              if existingStudentId:
                print("studentId exists")
                pass
              else:
                print("studentId does not exist")
                db.execute("UPDATE users SET studentId = ? WHERE email = ?", (studentId,userEmail))
                con.commit()
            if (userEmail) not in existingEmails and row:
                db.execute("INSERT INTO users (email,studentId,name,role) VALUES(?,?,?,?)", (userEmail,studentId, name, role))
                con.commit()
            userId = db.execute("SELECT id FROM users WHERE email = ?", (userEmail,)).fetchone()[0]
            sectionCode = row[3].split("-")[0]
            groupNum = row[3].split("-")[1]
            sectionId = db.execute("SELECT id FROM sections WHERE sectionCode = ? AND courseId = ?",(sectionCode,courseId)).fetchone()[0]
            addIntoClasses(courseId,sectionId,userId)
            groupId = addIntoGroups(groupNum,courseId,sectionCode)
            addIntoStudentGroups(groupId,userId)
    file.close()
    return message

def addIntoClasses(courseId,sectionId,userId):
    existingClass = db.execute("SELECT * FROM classes WHERE courseId =? AND sectionId =? AND studentId =?", (courseId, sectionId, userId)).fetchone()
    if existingClass is None:
        db.execute("INSERT INTO classes (courseId,sectionId,studentId) VALUES (?,?,?)", (courseId, sectionId, userId))
        con.commit()

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
  db.execute("SELECT courseId FROM classes WHERE studentId LIKE ?", (studentId,))
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
  sectionId,groupId = getReviewCourse(session.get("courseId"),currentStudentId)
  classes = db.execute("SELECT studentId FROM studentGroups WHERE groupId =? ", (groupId,))
  classes = db.fetchall()
  # grabs Ids of the members
  memberIdList = [member[0] for member in classes ]
  for memberId in memberIdList:
    member = db.execute("SELECT name FROM users WHERE id = ?", (memberId,))
    memberIdList[memberIdList.index(memberId)] = member.fetchone()[0]
  return memberIdList,classes

def reviewIntoDatabase(courseId,sectionId,groupNum,reviewerId,revieweeId,reviewScore,reviewComment):
  reviewExists = db.execute("SELECT * FROM reviews WHERE courseId = ? AND sectionId = ? AND groupId = ? AND reviewerId = ? AND revieweeId = ?",(courseId,sectionId,groupNum,reviewerId,revieweeId)).fetchone()
  if reviewExists:
    db.execute("UPDATE reviews SET reviewScore = ?, reviewComment = ? WHERE courseId = ? AND sectionId = ? AND groupId = ? AND reviewerId = ? AND revieweeId = ?",(reviewScore,reviewComment,courseId,sectionId,groupNum,reviewerId,revieweeId))
    message = "update"
  else:
    db.execute("INSERT INTO reviews (courseId,sectionId,groupId,reviewerId,revieweeId,reviewScore,reviewComment) VALUES(?,?,?,?,?,?,?)",(courseId,sectionId,groupNum,reviewerId,revieweeId,reviewScore,reviewComment))
    message  = "add"
  con.commit()
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
  groupIds = db.execute("SELECT groupId FROM studentGroups WHERE studentId = ?",(reviewerId,)).fetchall()
  for id in groupIds:
    sectionId = db.execute("SELECT sectionId FROM groups WHERE id = ? AND courseId =?",(id[0],courseId)).fetchone()
    if sectionId:
      return sectionId[0],id[0]
  return None,None

def getLecturerCourses(lecturerId):
  courses = db.execute("SELECT id FROM courses WHERE lecturerId = ?",(lecturerId,)).fetchall()
  registeredClasses = []
  for course in courses:
    db.execute("SELECT courseCode,courseName FROM courses WHERE id =?", (course[0],))
    courseName = db.fetchmany()[0]
    wholeCourseName = course[0],courseName[0],courseName[1]
    registeredClasses.append(wholeCourseName)
  return registeredClasses

def getGroups(courseId,sectionId):
  groups = db.execute("SELECT * FROM groups WHERE courseId = ? AND sectionId = ?",(courseId,sectionId)).fetchall()
  return groups

def getStudentGroups(courseId,sectionId,groups):
  groupedStudents = []
  for group in groups:
    studentGroups = db.execute("SELECT studentId from studentGroups WHERE groupId = ?",(group[0],)).fetchall()
    students = [db.execute("SELECT groupName FROM groups WHERE id = ?",(group[0],)).fetchone()[0]]
    for student in studentGroups:
      name = db.execute("SELECT name FROM users WHERE id = ?",(student[0],)).fetchone()[0]
      data = student[0],name,getStudentReview(courseId,sectionId,group[0],student[0]),getSelfAssessment(courseId,student[0]),getLecturerRating(sectionId,student[0])
      students.append(data)
    groupedStudents.append(students)
  return(groupedStudents)

def getLecturerRating(sectionId,studentId):
  rating = db.execute("SELECT lecturerFinalRating FROM lecturerRatings WHERE sectionId = ? AND studentId = ?",(sectionId,studentId)).fetchone()
  if rating:
    return rating[0]
  else:
    return None
      

def getStudentReview(courseId,sectionId,groupNum,studentId):
  studentRatings = db.execute("SELECT * FROM reviews WHERE courseId =? AND sectionId = ? AND groupId = ? AND revieweeId = ?",(courseId,sectionId,groupNum,studentId,)).fetchall()
  totalRating = 0  # keep track of total rating
  reviews = db.execute("SELECT revieweeId,reviewScore,reviewComment FROM reviews WHERE courseId = ? AND sectionId = ? AND groupId = ? AND reviewerId = ?",(courseId,sectionId,groupNum,studentId)).fetchall()
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

def importAssignmentMarks(lecturerId, courseId, filepath, output_filepath):
    with open(filepath, newline="") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        finalMarksData = []
        finalMarksHeaders = ["studentId", "Sections", "finalAssignmentMark"]
        for row in reader:
          if len(row) != 2:
              raise ValueError(f"Missing column found in row {row}.")
          
          courseCode = db.execute("SELECT courseCode FROM courses WHERE id = ?",(courseId,)).fetchone()

          section = row[0].split("-")[0]
          currentSectionId = db.execute("SELECT id FROM sections WHERE sectionCode = ? AND courseId = ?",(section,courseId)).fetchone()
          currentSectionCode = db.execute("SELECT sectionCode FROM sections WHERE id = ?",(currentSectionId[0],)).fetchone()
          if not currentSectionId:
              print("sectionnotfound")
              raise ValueError(f"Section {section} not found for course {courseId}.")
          
          group = row[0].split("-")[1]
          currentGroupId = db.execute("SELECT id FROM groups WHERE groupName = ? AND courseId = ? AND sectionId = ?",(group,courseId,currentSectionId[0])).fetchone()
          currentGroupName = db.execute("SELECT groupName FROM groups WHERE id = ?",(currentGroupId[0],)).fetchone()
          if not currentSectionId:
            print("groupnotfound")
            raise ValueError(f"Group {group} not found for course {courseId}.")

          studentIds = db.execute("SELECT studentId FROM studentGroups WHERE groupId = ?",(currentGroupId[0],)).fetchall()

          assignmentmark = row[1]

          db.execute("INSERT INTO finalGroupMarks (groupId, finalMark) VALUES(?, ?)",(currentGroupId[0], assignmentmark))
          con.commit()

          
          for studentId in studentIds:
            allComments = []
            allSelfAssessments = []
            actualStudentId = db.execute("SELECT studentId FROM users WHERE id = ?",(studentId[0],)).fetchone()
            actualStudentName = db.execute("SELECT name FROM users WHERE id = ?",(studentId[0],)).fetchone()

            APR = db.execute("SELECT finalRating FROM finalRatings WHERE studentId = ? AND courseId = ? AND sectionId = ?",(studentId[0],courseId,currentSectionId[0])).fetchone()
            if not APR:
              APR = f"{actualStudentName[0]} does not have a final rating."
            
            LR = db.execute("SELECT lecturerFinalRating FROM lecturerRatings WHERE studentId = ? AND sectionId = ?",(studentId[0],currentSectionId[0])).fetchone()
            if not LR:
              LR = f"{actualStudentName[0]} does not have a lecturer rating."
            
            AM = db.execute("SELECT finalMark FROM finalGroupMarks WHERE groupId = ?",(currentGroupId[0],)).fetchone()
            if not AM:
              AM = f"Group {currentGroupName[0]} does not have a final mark."

            comments = db.execute("SELECT reviewComment FROM reviews WHERE reviewerId = ? AND courseId = ? AND sectionId = ? AND groupId = ?",(studentId[0],courseId,currentSectionId[0],currentGroupId[0])).fetchall()

            for i in comments: 
              allComments.append(i[0])

            selfAssessments = db.execute("SELECT answer FROM selfAssessment WHERE reviewerId = ? AND courseId = ?",(studentId[0],courseId)).fetchall()

            for i in selfAssessments:
              allSelfAssessments.append(i[0])            

            allComments = ", ".join(allComments)
            allSelfAssessments = ", ".join(allSelfAssessments)
          
            if APR and LR and AM:
              finalResult = round((0.5) * AM[0] + (0.25) * AM[0] * float(APR[0]/3) + (0.25) * AM[0] * float(LR[0]/3),2)
            else:
              finalResult = "N/A"

            print(actualStudentId[0], currentSectionCode[0],currentGroupName[0], APR[0], LR[0], assignmentmark, finalResult, allComments, allSelfAssessments)

              # finalMarksData.append((actualStudentId[0], currentSectionCode[0], finalAssignmentMark))
        #     else:
        #       finalMarksData.append((actualStudentId[0], currentSectionCode[0], "N/A"))
        # print(output_filepath,finalMarksHeaders,finalMarksData)
        # writeFinalMark(output_filepath,finalMarksHeaders,finalMarksData)

def writeFinalMark(filepath,finalMarksHeaders,finalAssignmentMark):
  print("writing final mark")
  with open(filepath, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(finalMarksHeaders)  # Write the header
    writer.writerows(finalAssignmentMark)

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
            section_id = row[3].split("-")[0]
            section_ids.add(section_id)
    return section_ids

def insertLecturerRating(lecturerId,studentId,sectionId,lecturerFinalRating):
  rating = db.execute("SELECT * FROM lecturerRatings WHERE lecturerId = ? AND studentId = ? AND sectionId =? ",(lecturerId,studentId,sectionId)).fetchone()
  if rating:
    db.execute("UPDATE lecturerRatings SET lecturerFinalRating = ? WHERE lecturerId = ? AND studentId = ? AND sectionId = ?",(lecturerFinalRating,lecturerId,studentId,sectionId))
    flash("Updated Lecturer Rating.")
  else:
    db.execute("INSERT INTO lecturerRatings (lecturerId,studentId,sectionId,lecturerFinalRating) VALUES(?,?,?,?)",(lecturerId,studentId,sectionId,lecturerFinalRating))
    flash("Added Lecturer Rating.")
  con.commit()
  
  return redirect("/dashboard")

def getCourseId(courseCode, courseName,sectionId,lecturerId):
  course = db.execute("SELECT id FROM courses WHERE courseCode = ? AND courseName = ? AND sessionCode = ? AND lecturerId = ?",(courseCode,courseName,sectionId,lecturerId)).fetchone()
  return course[0]

def getQuestions(lecturerId,layoutId):
  questions = db.execute("SELECT id,question FROM questions WHERE layoutId = ?",(layoutId,)).fetchall()
  return questions

def getCurrentQuestions( courseId):
  layoutId = db.execute("SELECT layoutId FROM courses WHERE id=?",(courseId,)).fetchone()[0]
  questions = db.execute("SELECT id,question FROM questions WHERE layoutId = ?",(layoutId,)).fetchall()
  return layoutId,questions

def changeLayout(layoutId,courseId):
  db.execute("UPDATE courses SET layoutId = ? WHERE id =?",(layoutId,courseId))
  con.commit()
  flash("Layout changed")

def getReviewQuestions(courseId):
  layoutId = db.execute("SELECT layoutId FROM courses WHERE id = ?",(courseId,)).fetchone()[0]
  questions = db.execute("SELECT id,question FROM questions WHERE layoutId = ?",(layoutId,)).fetchall()
  return questions

def deleteCourse(courseId,lecturerId):
  db.execute("DELETE FROM courses WHERE id = ?",(courseId,))
  groups = db.execute("SELECT id FROM groups WHERE courseId = ?",(courseId,)).fetchall()
  for group in groups:
    db.execute("DELETE FROM studentGroups WHERE groupId = ?",(group[0],))
  db.execute("DELETE FROM groups WHERE courseId = ?",(courseId,))
  db.execute("DELETE FROM classes WHERE courseId=?", (courseId,))
  db.execute("DELETE FROM sections WHERE courseId =?",(courseId,))
  db.execute("DELETE FROM reviews WHERE courseId = ?",(courseId,))
  db.execute("DELETE FROM selfAssessment WHERE courseId = ?",(courseId,))
  con.commit()
  flash("Course deleted")

def deleteFromCourses(courseId,lecturerId,message):
  db.execute("DELETE FROM courses WHERE id = ?",(courseId,))
  con.commit()
  return redirect("/addingCourses")

def getCourseSection(courseId):
  sections = db.execute("SELECT * FROM sections WHERE courseId = ?",(courseId,)).fetchall()
  return sections

def getSectionAndGroup(courseId):
  print(courseId)
  sections = db.execute("SELECT * FROM sections WHERE courseId = ?",(courseId,)).fetchall()
  print(sections)
  sectionGroup = []
  for section in sections:
    groups = db.execute("SELECT groupName FROM groups WHERE courseId = ? AND sectionId = ?",(courseId,section[0])).fetchall()
    for group in groups:
      sectionGroup.append((section[1],group[0]))
  print(sectionGroup)
  return sectionGroup

def getIntro(courseId):
  intro = db.execute("SELECT introId FROM courses WHERE id = ?",(courseId,)).fetchone()[0]
  return db.execute("SELECT content FROM introduction WHERE id = ?",(intro,)).fetchone()[0]

def changeIntro(courseId,content):
  db.execute("INSERT INTO introduction (content) VALUES(?)",(content,))
  con.commit()
  introId = db.execute("SELECT last_insert_rowid()").fetchone()[0]
  db.execute("UPDATE courses SET introId = ? WHERE id = ?",(introId,courseId))
  con.commit()
  flash("Introduction changed")

def changeReviewDateForCourse(courseId,startDate,endDate):
  print(courseId,startDate,endDate)
  db.execute("INSERT INTO reviewDates (date) VALUES(?)",(startDate,))
  con.commit()
  startDateId = db.execute("SELECT last_insert_rowid()").fetchone()[0]
  db.execute("INSERT INTO reviewDates (date) VALUES(?)",(endDate,))
  con.commit()
  endDateId = db.execute("SELECT last_insert_rowid()").fetchone()[0]
  print(startDateId,endDateId)
  db.execute("UPDATE courses SET startDateId = ?, endDateId = ? WHERE id = ?",(startDateId,endDateId,courseId)) 
  con.commit()
  sectionIds = db.execute("SELECT id FROM sections WHERE courseId = ?",(courseId,)).fetchall()
  for section in sectionIds:
    db.execute("UPDATE sections SET startDateId = ?, endDateId = ? WHERE id = ?",(startDateId,endDateId,section[0]))
    con.commit()

def getReviewDateForCourse(courseId):
  db.execute("SELECT startDateId,endDateId FROM courses WHERE id = ?",(courseId,))
  dates = db.fetchmany()
  try:
    startDate = db.execute("SELECT date FROM reviewDates WHERE id = ?",(dates[0][0],)).fetchone()[0]
    endDate = db.execute("SELECT date FROM reviewDates WHERE id = ?",(dates[0][1],)).fetchone()[0]
  except:
    startDate = None
    endDate = None
  return startDate,endDate

def changeReviewDate(courseId,sectionId,startDate,endDate):
  db.execute("INSERT INTO reviewDates (date) VALUES(?)",(startDate,))
  con.commit()
  startDateId = db.execute("SELECT last_insert_rowid()").fetchone()[0]
  db.execute("INSERT INTO reviewDates (date) VALUES(?)",(endDate,))
  con.commit()
  endDateId = db.execute("SELECT last_insert_rowid()").fetchone()[0]
  db.execute("UPDATE sections SET startDateId = ?, endDateId = ? WHERE id = ?",(startDateId,endDateId,sectionId)) 
  con.commit()

def getReviewDate(sectionId):
  db.execute("SELECT startDateId,endDateId FROM sections WHERE id = ?",(sectionId,))
  dates = db.fetchmany()
  try:
    startDate = db.execute("SELECT date FROM reviewDates WHERE id = ?",(dates[0][0],)).fetchone()[0]
    endDate = db.execute("SELECT date FROM reviewDates WHERE id = ?",(dates[0][1],)).fetchone()[0]
  except:
    startDate = None
    endDate = None
  return startDate,endDate

def checkDates(sectionId):
  startDate,endDate = getReviewDate(sectionId)
  today = datetime.datetime.now().strftime("%Y-%m-%d")
  if startDate == None or endDate == None:
    return None,"No Review Dates Set By Lecturer."
  elif today >= startDate and today <= endDate:
    return True,f"Peer Review is Open From {startDate} to {endDate}"
  elif today < startDate:
    return False,f"Peer Review Will Open From {startDate} to {endDate}"
  else:
    return False,f"Peer Review Was Open From {startDate} to {endDate}"
  
def getDefaultIntro():
  intro = db.execute("SELECT content FROM introduction WHERE id = 1").fetchone()[0]
  return intro