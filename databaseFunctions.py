import sqlite3
import csv
from flask import flash,redirect
import datetime
from supabase_py import create_client
from dotenv import load_dotenv
from flask import flash,redirect
import secrets   # generate random string for password initially
from werkzeug.security import check_password_hash, generate_password_hash  #hashes passwords
import os
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)


# Hard coded KEYS just in case
KEYS = ["id","email","name"]
CSV_KEYS = ["ï»¿email","studentId","name","section-group"]
CSV_CLEAN = ["email","studentId","name","section-group"]
ROLES = ["STUDENT","LECTURER"]
MARKS_HEADERS = ["Sections","Groups","Marks"]
NEW_USER_KEYS = ["email","name","password"]

# inputs csv files into the database
def csvToDatabase(courseId, lecturerId,filename):
    existingEmails =[]
    response = supabase.table('users').select('email').execute()
    data = response['data']
    for data in data:
      existingEmails.append(data['email'])
    message= None
    collectTempUserCreds = []
    gotNewUsers_flag = False
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
            name = row[2]
            role = "STUDENT"
            password = secrets.token_urlsafe(32)
            hashedPassword = generate_password_hash(password)
            if (userEmail)  in existingEmails:
              existingStudentId = supabase.table('users').select('studentId').eq('email',userEmail).execute()
              existingStudentId = existingStudentId['data']['studentId']
              if existingStudentId:
                pass
              else:
                supabase.table('users').update({'studentId': studentId}).eq('email', userEmail).execute()
            if (userEmail) not in existingEmails and row:
                gotNewUsers_flag = True
                collectTempUserCreds.append([f"{userEmail}",f"{name}", f"{password}"])
                supabase.table('users').insert({'email': userEmail, 'studentId': studentId, 'name': name, 'role': role, 'password': hashedPassword}).execute()
            response = supabase.table('users').select('id').eq('email',userEmail).execute()
            data = response['data']
            userId = data[0]['id']
            sectionCode = row[3].split("-")[0]
            groupNum = row[3].split("-")[1]
            response = supabase.table('sections').select('id').eq('sectionCode',sectionCode).eq('courseId',courseId).execute()
            data = response['data']
            sectionId = data[0]['id']
            addIntoClasses(courseId,sectionId,userId)
            groupId = addIntoGroups(groupNum,courseId,sectionCode)
            addIntoStudentGroups(groupId,userId)
    file.close()
    return message,collectTempUserCreds

def newStudentsPassword(collectTempUserCreds):
  with open("newUsers.txt", "w", newline='') as file:
    writer = csv.writer(file) 
  
    # Write table header with hardcoded KEYS
    writer.writerow(NEW_USER_KEYS) 
  
    # Write data
    for user in collectTempUserCreds:
      writer.writerow(user)
  file.close()

def addIntoClasses(courseId,sectionId,userId):
    response = supabase.table('classes').select('*').eq('courseId',courseId).eq('sectionId',sectionId).eq('studentId',userId).execute()
    existingClass = response['data']
    if existingClass is None:
        response = supabase.table('classes').insert({'courseId': courseId, 'sectionId': sectionId, 'studentId': userId}).execute()

def addIntoGroups(groupNum,courseId,sectionCode):
    response = supabase.table('sections').select('id').eq('sectionCode',sectionCode).eq('courseId',courseId).execute()
    data = response['data']
    sectionId = data[0]['id']
    response = supabase.table('groups').select('*').eq('groupName',groupNum).eq('courseId',courseId).eq('sectionId',sectionId).execute()
    existingGroup = response['data']
    if existingGroup is None:
      response = supabase.table('groups').insert({'courseId': courseId, 'sectionId': sectionId, 'groupName': groupNum}).execute()
    response = supabase.table('groups').select('id').eq('groupName',groupNum).eq('courseId',courseId).eq('sectionId',sectionId).execute()
    data = response['data']
    groupId = data[0]['id']
    return groupId

def addIntoStudentGroups(groupId,userId):
    existingStudentGroup = db.execute("SELECT * FROM studentGroups WHERE groupId =? AND studentId LIKE ?", (groupId, f"%{userId}%")).fetchone()
    response = supabase.table('studentGroups').select('*').eq('groupId',groupId).eq('studentId',userId).execute()
    existingStudentGroup = response['data']
    if existingStudentGroup is None:
        response = supabase.table('studentGroups').insert({'groupId': groupId, 'studentId': userId}).execute()


# gets the courses the current user's is registered in
def getRegisteredCourses(studentId):
  response = supabase.table('classes').select('courseId').eq('studentId',f'{studentId}').execute()
  data = response['data']
  coursesId =[]
  for id in data:
    coursesId.append(id['courseId'])
  registeredClasses = []
  for course in coursesId:
    response = supabase.table('courses').select('courseName','courseCode').eq('id',course).execute()
    data = response['data']
    wholeCourseName = data['courseName'],data['courseCode'],course
    registeredClasses.append(wholeCourseName)
  return registeredClasses

def getRegisteredCourseData(studentId):
  response = supabase.table('studentGroups').select('courseId','sectionId','groupId').eq('studentId',f'{studentId}').execute()
  data = response['data']
  group = []
  group.append(data['courseId'])
  group.append(data['sectionId'])
  group.append(data['groupId'])
  return group

# adds a course to the database
def addingClasses(courseId, courseName,session):
  currentcourses = db.execute("SELECT * FROM courses WHERE courseCode =?",courseId).fetchall()
  currentcourses = db.fetchall()
  currenctcourses = []
  response = supabase.table('courses').select('*').eq('courseCode',f'{courseId}').execute()
  data = response['data']
  for data in data:
    currentData = [data['id'],data['courseCode'],data['courseName'],data['lecturerId'],data['layoutId'],data['introId'],data['startDateId'],data['endDateId']]
    currentcourses.append(currentData)
  courseExists = False
  for currentcourse in currentcourses:
    if str(courseId) == currentcourse[0]:
      courseExists = True
    else:
      courseExists = False
  if courseExists == False:
    response = supabase.table('courses').insert({'courseCode': courseId, 'courseName': courseName, 'lecturerId': session.get("id")}).execute()
    flash("Successfully added course.")
    return redirect("/")
  else: 
    flash("Course already exists.")
    return redirect("/addingCourses")

  # make function for add class groups button



#adds user to database
def addUserToDatabase(email, username):

  response = supabase.table('users').select('email').execute()
  data = response['data']
  existingEmails = []
  for data in data:
    existingEmails.append(data['email'])
  if email in existingEmails:
    response = supabase.table('users').select('role').eq('email',email).execute()
    data = response['data']
    role = data['role']
    return role
  mailEnding = email.split("@")[1]
  if mailEnding.startswith("student"):
    role = "STUDENT"
  else:
    role = "LECTURER"
  response = supabase.table("users").insert({"email": email, "name": username, "role": role}).execute()
  return role



# gets number and members of the group
def getMembers(session):
  # Get the current user's details
  currentStudentId = session.get("id")
  # Get the class details for the current student
  # make it so that it understands the current student's class on button clicked
  courseId = session.get("courseId")
  sectionId,groupId = getReviewCourse(session.get("courseId"),currentStudentId)
  response = supabase.table('studentGroups').select('studentId').eq('groupId',f'{groupId}').execute()
  data = response['data']
  memberIdList = []
  for data in data:
    memberIdList.append(data['studentId'])
  # grabs Ids of the members
  for memberId in memberIdList:
    response = supabase.table('users').select('name').eq('id',f'{memberId}').execute()
    data = response['data']
    memberIdList[memberIdList.index(memberId)] = data['name']
  return memberIdList,classes

def reviewIntoDatabase(courseId,sectionId,groupNum,reviewerId,revieweeId,reviewScore,reviewComment):
  response = supabase.table('reviews').select('*').eq('courseId',f'{courseId}').eq('sectionId',f'{sectionId}').eq('groupId',f'{groupNum}').eq('reviewerId',f'{reviewerId}').eq('revieweeId',f'{revieweeId}').execute()
  data = response['data']
  reviewExists = data
  if reviewExists:
    response = supabase.table('reviews').update({'reviewScore': reviewScore, 'reviewComment': reviewComment}).eq('courseId',f'{courseId}').eq('sectionId',f'{sectionId}').eq('groupId',f'{groupNum}').eq('reviewerId',f'{reviewerId}').eq('revieweeId',f'{revieweeId}').execute()
    message = "update"
  else:
    response = supabase.table('reviews').insert({'courseId': courseId, 'sectionId': sectionId, 'groupId': groupNum, 'reviewerId': reviewerId, 'revieweeId': revieweeId, 'reviewScore': reviewScore, 'reviewComment': reviewComment}).execute()
    message  = "add"
  return message

# db.execute("CREATE TABLE IF NOT EXISTS selfAssessment (courseId TEXT NOT NULL,sectionId TEXT NOT NULL,groupNum TEXT NOT NULL,reviewerId INTEGER NOT NULL,)")
def getUserId(userEmail):
  response = supabase.table('users').select('id').eq('email',f'{userEmail}').execute()
  data = response['data']
  userId = data['id']
  return userId

def selfAssessmentIntoDatabase(courseId,questionId,question,answer,reviewerId):
  response = supabase.table('selfAssessment').select('*').eq('courseId',f'{courseId}').eq('questionId',f'{questionId}').eq('reviewerId',f'{reviewerId}').execute()
  data = response['data']
  selfAssessmentExists = data
  if selfAssessmentExists:
    response = supabase.table('selfAssessment').update({'answer': answer}).eq('courseId',f'{courseId}').eq('questionId',f'{questionId}').eq('reviewerId',f'{reviewerId}').execute()
    message = "update"
  else:
    response = supabase.table('selfAssessment').insert({'courseId': courseId, 'questionId': questionId, 'question': question, 'answer': answer, 'reviewerId': reviewerId}).execute()
    message = "add"
  return message

def getReviewCourse(courseId,reviewerId):
  reponse = supabase.table('studentGroups').select('groupId').eq('studentId',f'{reviewerId}').execute()
  data = response['data']
  groupIds = []
  for data in data:
    groupIds.append(data['groupId'])
  for id in groupIds:
    response = supabase.table('groups').select('sectionId').eq('id',f'{id}').eq('courseId',f'{courseId}').execute()
    data = response['data']
    sectionId = data['sectionId']
    if sectionId:
      return sectionId[0],id[0]
  return None,None

def getLecturerCourses(lecturerId):
  response = supabase.table('courses').select('id').eq('lecturerId',f'{lecturerId}').execute()
  data = response['data']
  courses = []
  for data in data:
    courses.append(data['id'])
  registeredClasses = []
  for course in courses:
    response = supabase.table('courses').select('courseCode','courseName').eq('id',f'{course}').execute()
    data = response['data']
    courseName = data['courseName']
    courseCode = data['courseCode']
    wholeCourseName = course[0],courseCode,courseName
    registeredClasses.append(wholeCourseName)
  return registeredClasses

def getGroups(courseId,sectionId):
  response = supabase.table('groups').select('*').eq('courseId',f'{courseId}').eq('sectionId',f'{sectionId}').execute()
  data = response['data']
  groups = []
  for data in data:
    id,groupName,courseId,sectionId = data['id'],data['groupName'],data['courseId'],data['sectionId']
    groups.append([id,groupName,courseId,sectionId])
  return groups 

def getStudentGroups(courseId,sectionId,groups):
  groupedStudents = []
  for group in groups:
    response = supabase.table('studentGroups').select('studentId').eq('groupId',f'{group[0]}').execute()
    data = response['data']
    studentGroups = []
    for data in data:
      studentGroups.append(data['studentId'])
    response = supabase.table('groups').select('groupName').eq('id',f'{group[0]}').execute()
    data = response['data']
    groupName = data['groupName']
    students =[groupName]
    for student in studentGroups:
      response = supabase.table('users').select('name').eq('id',f'{student}').execute()
      studentdata = response['data']
      name = studentdata['name']
      data = student,name,getStudentReview(courseId,sectionId,group[0],student),getSelfAssessment(courseId,student),getLecturerRating(sectionId,student)
      students.append(data)
    groupedStudents.append(students)
  return(groupedStudents)

def getLecturerRating(sectionId,studentId):
  response = supabase.table('lecturerRatings').select('lecturerFinalRating').eq('sectionId',f'{sectionId}').eq('studentId',f'{studentId}').execute()
  data = response['data']
  rating = data['lecturerFinalRating']
  if rating:
    return rating
  else:
    return None
      

def getStudentReview(courseId,sectionId,groupNum,studentId):
  totalRating = 0  # keep track of total rating
  response = supabase.table('reviews').select('revieweeId','reviewScore','reviewComment').eq('courseId',f'{courseId}').eq('sectionId',f'{sectionId}').eq('groupId',f'{groupNum}').eq('reviewerId',f'{studentId}').execute()
  data = response['data']
  reviews = []
  for data in data:
    reviews.append([data['revieweeId'],data['reviewScore'],data['reviewComment']])
  listReviews = []
  for review in reviews:
    student = [review[0],review[1],review[2]]
    listReviews.append(student)
  return listReviews

def getSelfAssessment(courseId,studentId):
  response = supabase.table('selfAssessment').select('*').eq('courseId',f'{courseId}').eq('reviewerId',f'{studentId}').execute()
  data = response['data']
  selfAssessment = []
  for data in data:
    selfAssessment.append([data['courseId'],data['questionId'],data['question'],data['answer'],data['reviewerId']])
  if selfAssessment:
    return selfAssessment
  else:
    return None


def getProfiles(lecturerId):
  response = supabase.table('questionLayouts').select('id','layoutName').eq('lecturerId','0').execute()
  data = response['data']
  default = []
  for data in data:
    default.append([data['id'],data['layoutName']])
  response = supabase.table('questionLayouts').select('id','layoutName').eq('lecturerId',f'{lecturerId}').execute()
  data = response['data']
  profiles = []
  for data in data:
    profiles.append([data['id'],data['layoutName']])
  profiles = default + profiles

  result = []
  for profile in profiles:
    layoutId = profile[0]
    layoutName = profile[1]

    response = supabase.table('questions').select('id','question').eq('layoutId',f'{layoutId}').execute()
    data = response['data']
    layoutQuestions = []
    for data in data:
      layoutQuestions.append([data['id'],data['question']])

    questions = []
    for q in layoutQuestions:
      questionId = q[0]
      question = q[1]
      questions.append({"id": questionId,"question": question})

    result.append({"id": layoutId,"layoutName": layoutName,"layoutQuestions": questions} )
  return result

def addProfile(layoutName,lecturerId):
  response = supabase.table('questionLayouts').insert({'layoutName': layoutName, 'lecturerId': lecturerId}).execute()
  flash("Profile added")

def deleteProfile(layoutId,lecturerId):
  response = supabase.table('questionLayouts').delete().eq('id',f'{layoutId}').eq('lecturerId',f'{lecturerId}').execute()
  response = supabase.table('questions').delete().eq('layoutId',f'{layoutId}').execute()
  flash("Profile deleted")

def addQuestions(question,lecturerId,layoutId):
  response = supabase.table('questions').insert({'question': question, 'lecturerId': lecturerId, 'layoutId': layoutId}).execute()
  flash("Question added")

def deleteQuestion(questionId,layoutId,lecturerId):
  response = supabase.table('questions').select('question').eq('id',f'{questionId}').eq('lecturerId',f'{lecturerId}').eq('layoutId',f'{layoutId}').execute()
  data = response['data']
  question = data['question']
  if question:
    response = supabase.table('questions').delete().eq('id',f'{questionId}').eq('lecturerId',f'{lecturerId}').eq('layoutId',f'{layoutId}').execute()
    flash("Question deleted")
  else:
    flash("Question ID Invalid")

def importAssignmentMarks(lecturerId, courseId, filepath):
  finalMarksData = []
  finalMarksHeaders = ["studentId", "Sections", "Group", "Average-Peer-Rating", "Lecturer-Rating", "Assignment-Mark", "Final-Result", "Comments", "Self-Assessment"]

  with open(filepath, newline="") as file:
    reader = csv.reader(file)
    i=0
    for row in reader:
        if i == 0:
          if row != MARKS_HEADERS:
            raise ValueError(f"Incorrect CSV file format. Please use the following format: {MARKS_HEADERS}")

            
          i += 1
          continue
        if len(row) != 3:
            raise ValueError(f"Missing column found in row {row}.")


        section = row[0]

        response = supabase.table('sections').select('id').eq('sectionCode',f'{section}').eq('courseId',f'{courseId}').execute()
        data = response['data']
        currentSectionId = data['id']
        if not currentSectionId:
            raise ValueError(f"Section {section} not found for course {courseId}.")

        group = row[1]
        response = supabase.table('groups').select('id').eq('groupName',f'{group}').eq('courseId',f'{courseId}').eq('sectionId',f'{currentSectionId}').execute()
        data = response['data']
        currentGroupId = data['id']
        if not currentGroupId:
            raise ValueError(f"Group {group} not found for course {courseId}.")

        response = supabase.table('studentGroups').select('studentId').eq('groupId',f'{currentGroupId}').execute()
        data = response['data']
        studentIds = []
        for data in data:
          studentIds.append(data['studentId'])
        assignmentmark = row[2]

        response = supabase.table('finalGroupMarks').insert({'groupId': currentGroupId, 'finalMark': assignmentmark}).execute()
        for studentId in studentIds:
            allComments = []
            allSelfAssessments = []
            response = supabase.table('users').select('email').eq('id',f'{studentId}').execute()
            data = response['data']
            actualStudentId = data['email']

            if not actualStudentId:
                continue

            response = supabase.table('finalRatings').select('finalRating').eq('studentId',f'{studentId}').eq('courseId',f'{courseId}').eq('sectionId',f'{currentSectionId}').execute()
            data = response['data']
            APR = data['finalRating']
            response = supabase.table('lecturerRatings').select('lecturerFinalRating').eq('studentId',f'{studentId}').eq('sectionId',f'{currentSectionId}').execute()
            data = response['data']
            LR = data['lecturerFinalRating']
            response = supabase.table('finalGroupMarks').select('finalMark').eq('groupId',f'{currentGroupId}').execute()
            data = response['data']
            AM = data['finalMark']

            response = supabase.table('reviews').select('revieweeId','reviewScore','reviewComment').eq('reviewerId',f'{studentId}').eq('courseId',f'{courseId}').eq('sectionId',f'{currentSectionId}').eq('groupId',f'{currentGroupId}').execute()
            data = response['data']
            comments = []
            for data in data:
              comments.append([data['revieweeId'],data['reviewScore'],data['reviewComment']])
            for i in comments:
                response = supabase.table('users').select('name').eq('id',f'{i[0]}').execute()
                data = response['data']
                studentName = data['name']
                rating = f"Rating: {i[1]}"
                comment = f"Comment: {i[2]}"
                allComments.append([studentName,rating,comment])
            response = supabase.table('selfAssessment').select('question','answer').eq('reviewerId',f'{studentId}').eq('courseId',f'{courseId}').execute()
            data = response['data']
            selfAssessments = []
            for data in data:
              selfAssessments.append([data['question'],data['answer']])
            for i in selfAssessments:
                question = f"Question: {i[0]}"
                answer = f"Answer: {i[1]}"
                allSelfAssessments.append([question,answer])


            APR_value = APR[0] if APR else 0
            LR_value = LR[0] if LR else 'NO LECTURER RATING'
            AM_value = AM[0] if AM else 0

            if APR_value and LR_value and AM_value:
                finalResult = round((0.5 * AM_value) + (0.25 * AM_value * float(APR_value / 3)) + (0.25 * AM_value * float(LR_value / 3)), 2)
            else:
                finalResult = "Not all marks available"

            finalMarksData.append((actualStudentId[0], section, group, APR_value, LR_value, assignmentmark, finalResult, allComments, allSelfAssessments))
  return finalMarksHeaders, finalMarksData

def writeFinalResults(filepath,finalMarksHeaders,finalMarksData):
  with open(filepath, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(finalMarksHeaders)  # Write the header
    writer.writerows(finalMarksData)

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
  sections = db.execute("SELECT * FROM sections WHERE courseId = ?",(courseId,)).fetchall()
  sectionGroup = []
  for section in sections:
    groups = db.execute("SELECT groupName FROM groups WHERE courseId = ? AND sectionId = ?",(courseId,section[0])).fetchall()
    for group in groups:
      sectionGroup.append((section[1],group[0]))
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
  db.execute("INSERT INTO reviewDates (date) VALUES(?)",(startDate,))
  con.commit()
  startDateId = db.execute("SELECT last_insert_rowid()").fetchone()[0]
  db.execute("INSERT INTO reviewDates (date) VALUES(?)",(endDate,))
  con.commit()
  endDateId = db.execute("SELECT last_insert_rowid()").fetchone()[0]
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

def registerUser(email,username,password):
  hashedPassword = generate_password_hash(password)
  if db.execute(f"SELECT email FROM users WHERE email = '{email}'").fetchone():
    return "User already exists"
  if email.split("@")[1].startswith("mmu"):
    role = "LECTURER"
  else:
    role = "STUDENT"
  db.execute(f"INSERT INTO users (email,name,password,role) VALUES('{email}','{username}','{hashedPassword}','{role}')",(email,username,hashedPassword,role))
  con.commit()
  return "success"

def checkUser(email,password):
  user = db.execute(f"SELECT * FROM users WHERE email = '{email}'", (email,))
  if not user:
    return "User does not exist"
  if check_password_hash(user[5],password):
    return user
  return "Incorrect password"

def saveResetPasswordToken(email,token):
  db.execute("INSERT into resetPassword (email,token) VALUES(?,?)" , (email,token))
  con.commit()

def deleteResetPasswordToken(email,token):
  db.execute("DELETE FROM resetPassword WHERE email = ? AND token = ?" , (email,token))
  con.commit()

def getResetPasswordEmail(token):
  db.execute("SELECT email FROM resetPassword WHERE token = ?", (token,))
  email = db.fetchone()
  return email[0]

def checkDatabasePasswords(newPassword,email):
  userPassword = db.execute("SELECT password FROM users WHERE email = ?", (email,))
  userPassword = db.fetchone()
  userPassword = userPassword[0]
  passwordsMatch = check_password_hash(userPassword,newPassword)
  if passwordsMatch == True:
    flash("CANNOT CHANGE PASSWORD TO EXISTING PASSWORD")
    return redirect("/changePassword")
  elif passwordsMatch == False:
    userId = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()[0]
    changePassword(newPassword,userId)
    flash("SUCCESSFULLY CHANGED PASSWORD")
    return redirect("/")

def changePassword(newPassword,id):
  newPassword = generate_password_hash(newPassword)
  db.execute("UPDATE users SET password = ? WHERE id = ?", (newPassword, id))
  con.commit()

def checkPasswords(currentPassword,newPassword,confirmPassword,studentId):
  userPassword = db.execute("SELECT password FROM users WHERE id = ?", (studentId,))
  userPassword = userPassword.fetchone()
  userPassword = userPassword[0]
  passwordsMatch = check_password_hash(userPassword,currentPassword)
  if passwordsMatch == False:
    flash("INCORRECT CURRENT PASSWORD")
    return redirect("/changePassword")
  elif newPassword != confirmPassword:
    flash("PASSWORDS DO NOT MATCH")
    return redirect("/changePassword")
  elif newPassword == currentPassword:
    flash("CANNOT CHANGE PASSWORD TO EXISTING PASSWORD")
    return redirect("/changePassword")
  elif newPassword == confirmPassword:
    changePassword(newPassword,studentId)
    flash("SUCCESSFULLY CHANGED PASSWORD")
    return redirect("/dashboard")
  
response = supabase.table('questions').select('id').execute()
data = response['data']
for data in data:
  print(data[f'id'])

response = supabase.table('questions').select('*').eq('id','7').execute()
print(response['data'])

response = supabase.table('questions').select('*').execute()
data = response['data']
questions =[]
for question in data:
  questions.append(question['question'])
print(questions)

print("hi")
response = supabase.table('questions').select('question','id').execute()
data = response['data']
print(data)
# supabase.table('users').update({'studentId': studentId}).eq('email', userEmail).execute()
# supabase.table('users').insert({'email': userEmail, 'studentId': studentId, 'name': name, 'role': role, 'password': hashedPassword}).execute()