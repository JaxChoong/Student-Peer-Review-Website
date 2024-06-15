import csv
from flask import flash,redirect
import datetime
from supabase import create_client,Client
from dotenv import load_dotenv
from flask import flash,redirect
import secrets   # generate random string for password initially
from werkzeug.security import check_password_hash, generate_password_hash  #hashes passwords
import os
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# setup supabase 
url: str = supabase_url
key: str = supabase_key
supabase: Client = create_client(url, key)

# Hard coded KEYS just in case
KEYS = ["id","email","name"]
CSV_KEYS = ["ï»¿email","studentId","name","section","group"]
CSV_CLEAN = ["email","studentId","name","section","group"]
ROLES = ["STUDENT","LECTURER"]
MARKS_HEADERS = ["Sections","Groups","Marks"]
NEW_USER_KEYS = ["email","name","password"]

# inputs csv files into the database
def csvToDatabase(courseId, lecturerId,filename):
    existingEmails =[]
    response = supabase.table('users').select('email').execute()
    data = response.data
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
              response  = supabase.table('users').select('studentId').eq('email',f'{userEmail}').execute()
              existingStudentId = response.data[0]['studentId']
              if existingStudentId:
                pass
              else:
                supabase.table('users').update({'studentId': studentId}).eq('email',f'{userEmail}').execute()
            if (userEmail) not in existingEmails and row:
                gotNewUsers_flag = True
                collectTempUserCreds.append([f"{userEmail}",f"{name}", f"{password}"])
                supabase.table('users').insert({'email': userEmail, 'studentId': studentId, 'name': name, 'role': role, 'password': hashedPassword}).execute()
            response = supabase.table('users').select('id').eq('email',f'{userEmail}').execute()
            data = response.data[0]
            userId = data['id']
            sectionCode = row[3]
            groupNum = row[4]
            response = supabase.table('sections').select('id').eq('sectionCode',f'{sectionCode}').eq('courseId',f'{courseId}').execute()
            data = response.data
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
    response = supabase.table('classes').select('*').eq('courseId',f'{courseId}').eq('sectionId',f'{sectionId}').eq('studentId',f'{userId}').execute()
    existingClass = response.data
    if not existingClass:
      response = supabase.table('classes').insert({'courseId': courseId, 'sectionId': sectionId, 'studentId': userId}).execute()

def addIntoGroups(groupNum,courseId,sectionCode):
    response = supabase.table('sections').select('id').eq('sectionCode',f'{sectionCode}').eq('courseId',f'{courseId}').execute()
    data = response.data
    sectionId = data[0]['id']
    response = supabase.table('groups').select('*').eq('groupName',f'{groupNum}').eq('courseId',f'{courseId}').eq('sectionId',f'{sectionId}').execute()
    existingGroup = response.data
    if not existingGroup:
      response = supabase.table('groups').insert({'courseId': courseId, 'sectionId': sectionId, 'groupName': groupNum}).execute()
    response = supabase.table('groups').select('id').eq('groupName',f'{groupNum}').eq('courseId',f'{courseId}').eq('sectionId',f'{sectionId}').execute()
    data = response.data
    groupId = data[0]['id']
    return groupId

def addIntoStudentGroups(groupId,userId):
    response = supabase.table('studentGroups').select('*').eq('groupId',f'{groupId}').eq('studentId',f'{userId}').execute()
    existingStudentGroup = response.data
    if not existingStudentGroup:
      response = supabase.table('studentGroups').insert({'groupId': groupId, 'studentId': userId}).execute()


# gets the courses the current user's is registered in
def getRegisteredCourses(studentId):
  response = supabase.table('classes').select('courseId').eq('studentId',f'{studentId}').execute()
  data = response.data
  coursesId =[]
  for id in data:
    coursesId.append(id['courseId'])
  registeredClasses = []
  for course in coursesId:
    response = supabase.table('courses').select('courseName','courseCode').eq('id',f'{course}').execute()
    data = response.data[0]
    wholeCourseName = data['courseName'],data['courseCode'],course
    registeredClasses.append(wholeCourseName)
  return registeredClasses

def getRegisteredCourseData(studentId):
  response = supabase.table('studentGroups').select('courseId','sectionId','groupId').eq('studentId',f'{studentId}').execute()
  data = response.data
  group = []
  group.append(data['courseId'])
  group.append(data['sectionId'])
  group.append(data['groupId'])
  return group

# adds a course to the database
def addingClasses(courseId, courseName,session):
  currentcourses = []
  response = supabase.table('courses').select('*').eq('courseCode',f'{courseId}').execute()
  data = response.data
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
  data = response.data
  existingEmails = []
  for data in data:
    existingEmails.append(data['email'])
  if email in existingEmails:
    response = supabase.table('users').select('role').eq('email',f'{email}').execute()
    data = response.data
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
  data = response.data
  classes = []
  # JAX CHECK THIS
  memberIdList = []
  for data in data:
    classes.append((data['studentId'],))
    memberIdList.append(data['studentId'])
  # grabs Ids of the members
  for memberId in memberIdList:
    response = supabase.table('users').select('name').eq('id',f'{memberId}').execute()
    data = response.data[0]
    memberIdList[memberIdList.index(memberId)] = data['name']
  return memberIdList,classes

def reviewIntoDatabase(courseId,sectionId,groupNum,reviewerId,revieweeId,reviewScore,reviewComment):
  response = supabase.table('reviews').select('*').eq('courseId',f'{courseId}').eq('sectionId',f'{sectionId}').eq('groupId',f'{groupNum}').eq('reviewerId',f'{reviewerId}').eq('revieweeId',f'{revieweeId}').execute()
  data = response.data
  reviewExists = data
  if reviewExists:
    response = supabase.table('reviews').update({'reviewScore': reviewScore, 'reviewComment': reviewComment}).eq('courseId',f'{courseId}').eq('sectionId',f'{sectionId}').eq('groupId',f'{groupNum}').eq('reviewerId',f'{reviewerId}').eq('revieweeId',f'{revieweeId}').execute()
    message = "update"
  else:
    response = supabase.table('reviews').insert({'courseId': courseId, 'sectionId': sectionId, 'groupId': groupNum, 'reviewerId': reviewerId, 'revieweeId': revieweeId, 'reviewScore': reviewScore, 'reviewComment': reviewComment}).execute()
    message  = "add"
  return message


def getUserId(userEmail):
  response = supabase.table('users').select('id').eq('email',f'{userEmail}').execute()
  data = response.data
  userId = data['id']
  return userId

def selfAssessmentIntoDatabase(courseId,questionId,question,answer,reviewerId):
  response = supabase.table('selfAssessment').select('*').eq('courseId',f'{courseId}').eq('questionId',f'{questionId}').eq('reviewerId',f'{reviewerId}').execute()
  data = response.data
  selfAssessmentExists = data
  if selfAssessmentExists:
    response = supabase.table('selfAssessment').update({'answer': answer}).eq('courseId',f'{courseId}').eq('questionId',f'{questionId}').eq('reviewerId',f'{reviewerId}').execute()
    message = "update"
  else:
    response = supabase.table('selfAssessment').insert({'courseId': courseId, 'questionId': questionId, 'question': question, 'answer': answer, 'reviewerId': reviewerId}).execute()
    message = "add"
  return message

def getReviewCourse(courseId,reviewerId):
  response = supabase.table('studentGroups').select('groupId').eq('studentId',f'{reviewerId}').execute()
  data = response.data
  groupIds = []
  for data in data:
    groupIds.append(data['groupId'])
  for id in groupIds:
    response = supabase.table('groups').select('sectionId').eq('id',id).eq('courseId',courseId).execute()
    data = response.data
    if data:
      data = data[0]
    else:
      continue
    sectionId = data['sectionId']
    if sectionId:
      return sectionId,id
  return None,None

def getLecturerCourses(lecturerId):
  response = supabase.table('courses').select('id').eq('lecturerId',f'{lecturerId}').execute()
  data = response.data
  courses = []
  for data in data:
    courses.append(data['id'])
  registeredClasses = []
  for course in courses:
    response = supabase.table('courses').select('courseCode','courseName').eq('id',f'{course}').execute()
    data = response.data[0]
    courseName = data['courseName']
    courseCode = data['courseCode']
    wholeCourseName = course,courseCode,courseName
    registeredClasses.append(wholeCourseName)
  return registeredClasses

def getGroups(courseId,sectionId):
  response = supabase.table('groups').select('*').eq('courseId',f'{courseId}').eq('sectionId',f'{sectionId}').execute()
  data = response.data
  groups = []
  for data in data:
    id,groupName,courseId,sectionId = data['id'],data['groupName'],data['courseId'],data['sectionId']
    groups.append([id,groupName,courseId,sectionId])
  return groups 

def getStudentGroups(courseId,sectionId,groups):
  groupedStudents = []
  for group in groups:
    # get studentIds for students in the group
    response = supabase.table('studentGroups').select('studentId').eq('groupId',f'{group[0]}').execute()
    data = response.data
    studentGroups = []
    for data in data:
      studentGroups.append(data['studentId'])
    # get group name
    response = supabase.table('groups').select('groupName').eq('id',f'{group[0]}').execute()
    data = response.data[0]
    groupName = data['groupName']
    # setup array with the current group' name
    students =[groupName]
    for student in studentGroups:
      # for each student in the group, get their naeme
      response = supabase.table('users').select('name').eq('id',f'{student}').execute()
      studentdata = response.data[0]
      name = studentdata['name']
      # the student's id, name, the reviews they gave( long nested array ),self assessments( questions & answers), lecturer rating
      data = int(student),f'{name}',getStudentReview(courseId,sectionId,group[0],student),getSelfAssessment(courseId,student),getLecturerRating(sectionId,student)
      students.append(data)
    # save the current student's data into the current group
    groupedStudents.append(students)
  return(groupedStudents)

def getLecturerRating(sectionId,studentId):
  response = supabase.table('lecturerRatings').select('lecturerFinalRating').eq('sectionId',f'{sectionId}').eq('studentId',f'{studentId}').execute()
  data = response.data
  if data:
    rating = data[0]['lecturerFinalRating']
    return rating
  else:
    return None
      

def getStudentReview(courseId,sectionId,groupNum,studentId):
  totalRating = 0  # keep track of total rating
  response = supabase.table('reviews').select('revieweeId','reviewScore','reviewComment').eq('courseId',f'{courseId}').eq('sectionId',f'{sectionId}').eq('groupId',f'{groupNum}').eq('reviewerId',f'{studentId}').execute()
  data = response.data
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
  data = response.data
  selfAssessment = []
  for data in data:
    selfAssessment.append([data['courseId'],data['questionId'],data['question'],data['answer'],data['reviewerId']])
  if selfAssessment:
    return selfAssessment
  else:
    return None


def getProfiles(lecturerId):
  response = supabase.table('questionLayouts').select('id','layoutName').eq('lecturerId','0').execute()
  data = response.data
  default = []
  for data in data:
    default.append([data['id'],data['layoutName']])
  response = supabase.table('questionLayouts').select('id','layoutName').eq('lecturerId',f'{lecturerId}').execute()
  data = response.data
  profiles = []
  for data in data:
    profiles.append([data['id'],data['layoutName']])
  profiles = default + profiles

  result = []
  for profile in profiles:
    layoutId = profile[0]
    layoutName = profile[1]

    response = supabase.table('questions').select('id','question').eq('layoutId',f'{layoutId}').execute()
    data = response.data
    layoutQuestions = []
    for data in data:
      layoutQuestions.append([data['id'],data['question']])

    questions = []
    for q in layoutQuestions:
      questionId = q[0]
      question = q[1]
      questions.append({"id": questionId,"question": question})
    # save the current profile's data
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
  data = response.data
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
      data = response.data
      currentSectionId = data[0]['id']
      if not currentSectionId:
        raise ValueError(f"Section {section} not found for course {courseId}.")
      group = row[1]
      response = supabase.table('groups').select('id').eq('groupName',f'{group}').eq('courseId',f'{courseId}').eq('sectionId',f'{currentSectionId}').execute()
      data = response.data
      currentGroupId = data[0]['id']
      if not currentGroupId:
        raise ValueError(f"Group {group} not found for course {courseId}.")

      # get studentids of students in the group
      response = supabase.table('studentGroups').select('studentId').eq('groupId',f'{currentGroupId}').execute()
      data = response.data
      studentIds = []
      for data in data:
        studentIds.append(data['studentId'])
      assignmentmark = row[2]
      # get final group marks data in table
      response = supabase.table('finalGroupMarks').select('id').eq('groupId',f'{currentGroupId}').execute()
      data = response.data
      # if exist already, update it. if not, insert it
      if data:
        response = supabase.table('finalGroupMarks').update({'finalMark': assignmentmark}).eq('groupId',f'{currentGroupId}').execute()
      else:
        response = supabase.table('finalGroupMarks').insert({'groupId': currentGroupId, 'finalMark': assignmentmark}).execute()
      for studentId in studentIds:
        # get data for each student
        allComments = []
        allSelfAssessments = []
        response = supabase.table('users').select('studentId').eq('id',f'{studentId}').execute()
        data = response.data[0]
        actualStudentId = data['studentId']
        if not actualStudentId:
          continue
        # get students' reviews
        response = supabase.table('reviews').select('reviewScore').eq('revieweeId',f'{studentId}').eq('courseId',f'{courseId}').eq('sectionId',f'{currentSectionId}').eq('groupId',f'{currentGroupId}').execute()
        data = response.data
        APR = 0
        # add up all the ratings given to this student
        for ratings in data:
          APR += ratings['reviewScore']
        # calculate average
        APR = APR / len(data)
        # get lect rating
        response = supabase.table('lecturerRatings').select('lecturerFinalRating').eq('studentId',f'{studentId}').eq('sectionId',f'{currentSectionId}').execute()
        data = response.data
        LR = data[0]['lecturerFinalRating']
        # get final group marks
        response = supabase.table('finalGroupMarks').select('finalMark').eq('groupId',f'{currentGroupId}').execute()
        data = response.data
        AM = data[0]['finalMark']
        response = supabase.table('reviews').select('revieweeId','reviewScore','reviewComment').eq('reviewerId',f'{studentId}').eq('courseId',f'{courseId}').eq('sectionId',f'{currentSectionId}').eq('groupId',f'{currentGroupId}').execute()
        data = response.data
        comments = []
        for data in data:
          # saves the id, comment and score given to the student's groupmates
          comments.append([data['revieweeId'],data['reviewScore'],data['reviewComment']])
        for i in comments:
          # formats student's name, rating and comment
          response = supabase.table('users').select('name').eq('id',f'{i[0]}').execute()
          data = response.data[0]
          studentName = data['name']
          rating = f"Rating: {i[1]}"
          comment = f"Comment: {i[2]}"
          allComments.append([studentName,rating,comment])
        # get self assessment data
        response = supabase.table('selfAssessment').select('question','answer').eq('reviewerId',f'{studentId}').eq('courseId',f'{courseId}').execute()
        data = response.data
        selfAssessments = []
        for data in data:
          # saves the question and answer given by the student
          selfAssessments.append([data['question'],data['answer']])
        for i in selfAssessments:
          # formats it
          question = f"Question: {i[0]}"
          answer = f"Answer: {i[1]}"
          allSelfAssessments.append([question,answer])
        
        APR_value = APR if APR else 0
        LR_value = LR if LR else 'NO LECTURER RATING'
        AM_value = AM if AM else 0
        if APR_value and LR_value and AM_value:
          # calculate final marks
          finalResult = round((0.5 * AM_value) + (0.25 * AM_value * float(APR_value / 3)) + (0.25 * AM_value * float(LR_value / 3)), 2)
        else:
          finalResult = "Not all marks available"
        # saves the final data as a row to be written
        finalMarksData.append((actualStudentId, section, group, APR_value, LR_value, assignmentmark, finalResult, allComments, allSelfAssessments))
  return finalMarksHeaders, finalMarksData

def writeFinalResults(filepath,finalMarksHeaders,finalMarksData):
  with open(filepath, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(finalMarksHeaders)  # Write the header
    writer.writerows(finalMarksData)

def addCourseToDb(courseId, courseName, lecturerId,sectionId):
    message =""
    response = supabase.table('courses').select('*').eq('courseCode',f'{courseId}').eq('courseName',f'{courseName}').eq('lecturerId',f'{lecturerId}').execute()
    data = response.data
    currentcourses = data
    if not currentcourses:
      response = supabase.table('courses').insert({'courseCode': courseId, 'courseName': courseName, 'lecturerId': lecturerId}).execute()
      message = "Course added"
    response = supabase.table('courses').select('id').eq('courseCode',f'{courseId}').eq('courseName',f'{courseName}').eq('lecturerId',f'{lecturerId}').execute()
    data = response.data[0]
    courseId = data['id']
    response = supabase.table('sections').select('*').eq('sectionCode',f'{sectionId}').eq('courseId',f'{courseId}').execute()
    data = response.data
    currentSections = data
    if not currentSections:
      response = supabase.table('sections').insert({'sectionCode': sectionId, 'courseId': courseId}).execute()
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
      section_id = row[3]
      section_ids.add(section_id)
  return section_ids

def insertLecturerRating(lecturerId,studentId,sectionId,lecturerFinalRating):
  response = supabase.table('lecturerRatings').select('*').eq('lecturerId',f'{lecturerId}').eq('studentId',f'{studentId}').eq('sectionId',f'{sectionId}').execute()
  data = response.data
  if data:
    data = data[0]
    rating = [data['lecturerId'],data['studentId'],data['sectionId'],data['lecturerFinalRating']]
  else:
    rating = None
  if rating:
    response = supabase.table('lecturerRatings').update({'lecturerFinalRating': lecturerFinalRating}).eq('lecturerId',f'{lecturerId}').eq('studentId',f'{studentId}').eq('sectionId',f'{sectionId}').execute()
    flash("Updated Lecturer Rating.")
  else:
    response = supabase.table('lecturerRatings').insert({'lecturerId': lecturerId, 'studentId': studentId, 'sectionId': sectionId, 'lecturerFinalRating': lecturerFinalRating}).execute()
    flash("Added Lecturer Rating.")  
  return redirect("/dashboard")

def getCourseId(courseCode, courseName,sectionId,lecturerId):
  response = supabase.table('courses').select('id').eq('courseCode',f'{courseCode}').eq('courseName',f'{courseName}').eq('lecturerId',f'{lecturerId}').execute()
  data = response.data
  courseId = data['id']
  return courseId

def getQuestions(lecturerId,layoutId):
  response = supabase.table('questions').select('id','question').eq('layoutId',f'{layoutId}').execute()
  data = response.data
  questions = []
  for data in data:
    questions.append([data['id'],data['question']])
  return questions

def getCurrentQuestions( courseId):
  response = supabase.table('courses').select('layoutId').eq('id',f'{courseId}').execute()
  data = response.data[0]
  layoutId = data['layoutId']
  response = supabase.table('questions').select('id','question').eq('layoutId',f'{layoutId}').execute()
  data = response.data
  questions = []
  for data in data:
    questions.append([data['id'],data['question']])
  return layoutId,questions

def changeLayout(layoutId,courseId):
  response = supabase.table('courses').update({'layoutId': layoutId}).eq('id',f'{courseId}').execute()
  flash("Layout changed")

def getReviewQuestions(courseId):
  response = supabase.table('courses').select('layoutId').eq('id',f'{courseId}').execute()
  data = response.data[0]
  layoutId = data['layoutId']
  response = supabase.table('questions').select('id','question').eq('layoutId',f'{layoutId}').execute()
  data = response.data
  questions = []
  for data in data:
    questions.append([data['id'],data['question']])
  return questions

def deleteCourse(courseId, lecturerId):
  # Delete from courses
  response = supabase.table('sections').delete().eq('courseId', f'{courseId}').execute()
  response = supabase.table('courses').delete().eq('id', f'{courseId}').execute()
  
  # Get all group IDs for the course
  response = supabase.table('groups').select('id').eq('courseId', f'{courseId}').execute()
  data = response.data
  groups =[]
  for data in data:
    groups.append(data['id'])
  
  # Delete from studentGroups for each group
  for group in groups:
    response = supabase.table('studentGroups').delete().eq('groupId', f'{group}').execute()

  # Delete from groups
  response = supabase.table('groups').delete().eq('courseId', f'{courseId}').execute()

  # Delete from classes
  response = supabase.table('classes').delete().eq('courseId', f'{courseId}').execute()

  # Delete from reviews
  response = supabase.table('reviews').delete().eq('courseId', f'{courseId}').execute()

  # Delete from selfAssessment
  response = supabase.table('selfAssessment').delete().eq('courseId', f'{courseId}').execute()

  flash("Course deleted")


def deleteFromCourses(courseId,lecturerId,message):
  response = supabase.table('courses').delete().eq('id',f'{courseId}').eq('lecturerId',f'{lecturerId}').execute()
  return redirect("/addingCourses")

def getCourseSection(courseId):
  response = supabase.table('sections').select('*').eq('courseId',f'{courseId}').execute()
  data = response.data
  sections = []
  for data in data:
    sections.append([data['id'],data['sectionCode'],data['courseId'],data['startDateId'],data['endDateId']])
  return sections

def getSectionAndGroup(courseId):
  response = supabase.table('sections').select('*').eq('courseId',f'{courseId}').execute()
  data = response.data
  sections = []
  # get all sections for the course
  for data in data:
    sections.append([data['id'],data['sectionCode'],data['courseId'],data['startDateId'],data['endDateId']])
  sectionGroup = []
  for section in sections:
    # select groupname for the students
    response = supabase.table('groups').select('groupName').eq('courseId',f'{courseId}').eq('sectionId',f'{section[0]}').execute()
    data = response.data
    groups = []
    for data in data:
      groups.append(data['groupName'])
    for group in groups:
      # put section name and groups for that section
      sectionGroup.append((section[1],group))
  return sectionGroup

def getIntro(courseId):
  response = supabase.table('courses').select('introId').eq('id',f'{courseId}').execute()
  data = response.data[0]
  intro = data['introId']
  response = supabase.table('introduction').select('content').eq('id',f'{intro}').execute()
  data = response.data[0]
  content = data['content']
  return content

def changeIntro(courseId,content):
  response = supabase.table('introduction').insert({'content': content}).execute()
  # check this jax
  introId = response.data[0]['id']
  response = supabase.table('courses').update({'introId': introId}).eq('id',f'{courseId}').execute()
  flash("Introduction changed")

def changeReviewDateForCourse(courseId,startDate,endDate):
  response = supabase.table('reviewDates').insert({'date': startDate}).execute()
  startDateId = response.data[0]['id']
  response = supabase.table('reviewDates').insert({'date': endDate}).execute()
  endDateId = response.data[0]['id']
  response = supabase.table('courses').update({'startDateId': startDateId, 'endDateId': endDateId}).eq('id',f'{courseId}').execute()
  response = supabase.table('sections').select('id').eq('courseId',f'{courseId}').execute()
  data = response.data
  sectionIds = []
  for data in data:
    sectionIds.append(data['id'])
  for section in sectionIds:
    response = supabase.table('sections').update({'startDateId': startDateId, 'endDateId': endDateId}).eq('id',f'{section}').execute()

def getReviewDateForCourse(courseId):
  response = supabase.table('courses').select('startDateId','endDateId').eq('id',f'{courseId}').execute()
  data = response.data
  if data:
    data = data[0]
    startDateId = data['startDateId']
    endDateId = data['endDateId']
    response = supabase.table('reviewDates').select('date').eq('id',f'{startDateId}').execute()
    data = response.data[0]
    startDate = data['date']
    response = supabase.table('reviewDates').select('date').eq('id',f'{endDateId}').execute()
    data = response.data[0]
    endDate = data['date']

  else:
    startDate = None
    endDate = None
  return startDate,endDate

def changeReviewDate(courseId, sectionId, startDate, endDate):
  response = supabase.table('reviewDates').insert({'date': startDate}).execute()
  startDateId = response.data[0]['id']  

  response = supabase.table('reviewDates').insert({'date': endDate}).execute()
  endDateId = response.data[0]['id']

  response = supabase.table('sections').update({'startDateId': startDateId, 'endDateId': endDateId}).eq('id', f'{sectionId}').execute()


def getReviewDate(sectionId):
  response = supabase.table('sections').select('startDateId','endDateId').eq('id',f'{sectionId}').execute()
  data = response.data[0]
  if data:
    startDateId = data['startDateId']
    endDateId = data['endDateId']
    response = supabase.table('reviewDates').select('date').eq('id',f'{startDateId}').execute()
    data = response.data[0]
    startDate = data['date']
    response = supabase.table('reviewDates').select('date').eq('id',f'{endDateId}').execute()
    data = response.data[0]
    endDate = data['date']
    return startDate,endDate
  if not data:
    startDateId = None
    endDateId = None
    return startDate,endDate

def checkDates(sectionId):
  startDate,endDate = getReviewDate(sectionId)
  today = datetime.datetime.now().strftime("%Y-%m-%d")
  if not startDate  or not endDate:
    return None,"No Review Dates Set By Lecturer."
  elif today >= startDate and today <= endDate:
    return True,f"Peer Review is Open From {startDate} to {endDate}"
  elif today < startDate:
    return False,f"Peer Review Will Open From {startDate} to {endDate}"
  else:
    return False,f"Peer Review Was Open From {startDate} to {endDate}"
  
def getDefaultIntro():
  response = supabase.table('introduction').select('content').eq('id','1').execute()
  data = response.data[0]
  intro = data['content']
  return intro

def registerUser(email,username,password):
  hashedPassword = generate_password_hash(password)
  response = supabase.table('users').select('*').eq('email',f'{email}').execute()
  data = response.data
  if data:
    return "User already exists"
  if email.split("@")[1].startswith("mmu"):
    role = "LECTURER"
  else:
    role = "STUDENT"
  response = supabase.table('users').insert({'email': email, 'name': username, 'role': role, 'password': hashedPassword}).execute()
  return "success"

def checkUser(email,password):
  email=email.strip()
  response = supabase.table('users').select('*').eq('email',f'{email}').execute()
  data = response.data
  if not data:
    return "User does not exist"
  else:
    user = []
    for data in data:
      user.append(data['id'])
      user.append(data['email'])
      user.append(data['studentId'])
      user.append(data['name'])
      user.append(data['role'])
      user.append(data['password'])
  if check_password_hash(user[5],password):
    return user
  return "Incorrect password"

def saveResetPasswordToken(email,token):
  response = supabase.table('resetPassword').insert({'email': email, 'token': token}).execute()

def deleteResetPasswordToken(email,token):
  response = supabase.table('resetPassword').delete().eq('email',f'{email}').eq('token',f'{token}').execute()

def getResetPasswordEmail(token):
  response = supabase.table('resetPassword').select('email').eq('token',f'{token}').execute()
  data = response.data[0]
  email = data['email']
  return email

def checkDatabasePasswords(newPassword,email):
  response = supabase.table('users').select('password').eq('email',f'{email}').execute()
  data = response.data
  userPassword = data[0]['password']
  passwordsMatch = check_password_hash(userPassword,newPassword)
  if passwordsMatch == True:
    flash("CANNOT CHANGE PASSWORD TO EXISTING PASSWORD")
    return redirect("/changePassword")
  elif passwordsMatch == False:
    response = supabase.table('users').select('id').eq('email',f'{email}').execute()
    data = response.data[0]
    userId = data['id']
    changePassword(newPassword,userId)
    flash("SUCCESSFULLY CHANGED PASSWORD")
    return redirect("/")

def changePassword(newPassword,id):
  newPassword = generate_password_hash(newPassword)
  response = supabase.table('users').update({'password': newPassword}).eq('id',f'{id}').execute()

def checkPasswords(currentPassword,newPassword,confirmPassword,studentId):
  response = supabase.table('users').select('password').eq('id',f'{studentId}').execute()
  data = response.data
  userPassword = data[0]['password']
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
  
def getExistingEmail(email):
  response = supabase.table('users').select('email').eq('email',email).execute()
  data = response.data
  print(data)
  if data:
    return True
  else:
    return False

def checkHeaders(filepath):
  with open(filepath, newline="") as file:
    reader = csv.reader(file)
    headers = next(reader)
    if headers != CSV_KEYS:
      raise ValueError(f"Incorrect CSV file format. Please use the following format: {CSV_CLEAN}")
    return True