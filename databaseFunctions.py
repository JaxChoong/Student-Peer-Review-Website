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
    groupNumToAdd = []
    reader = csv.reader(file)
    header =  next(reader)
    if header != CSV_KEYS:                      # checks if header of csv matches database
      print(f"Invalid CSV format. Header does not match expected format.\n Using: {header} \n Change to : {CSV_KEYS}")
      return
    collectTempUserCreds = []
    gotNewUsers_flag = False
    for row in reader:   # loops through each row in the csv
      foundEmptyValue = False     # flag for empty values
      if len(row) != len(CSV_KEYS):    # check for missing coloumns
        print(f"Missing coloumn found in row {row}. Skipping...")
        foundEmptyValue = True
        continue

      for data in row:         
        if not data:         #checks if data coloumn is empty      
          foundEmptyValue = True
          print(f"Empty value found in row {row}. Skipping...")
          break

      if foundEmptyValue == True:
        continue                   # skips this cycle of the loop
      
      # get current userid and name
      userEmail = row[0] 
      name = row[1]
      role = "STUDENT"
      
      # check if user Role exists
      if role not in ROLES:      
        print(f"Role {role} does not exist.")
        continue
      
      # if user not already existing and not empty row
      elif ( userEmail) not in existingEmails and row:
        gotNewUsers_flag = True
        db.execute("INSERT INTO users (email,name,role) VALUES(?,?,?,?)",(userEmail,name,role))
        con.commit()
        print("added to database")
      else:
        print(f"User {userEmail} already Exists.")
      sectionGroup = row[2].split("-")
      section,group = sectionGroup[0],sectionGroup[1]
      if group not in groupNumToAdd:
        groupNumToAdd.append(group)
      studentsToGroup.append(row)
    if gotNewUsers_flag == True:
      newStudentsPassword(collectTempUserCreds) # function def'd later
    addIntoGroups(studentsToGroup,groupNumToAdd,section)
  file.close()


# verifies incoming user
def checkUser(email, password, session):
  existingEmails = db.execute("SELECT email FROM users")
  existingEmails = list({email[0] for email in existingEmails})    # turn existing users into a list
  if email not in existingEmails:
    print("Not inside database, consult with your lecturer")
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
      print("Wrong Password")


# creates a new password for every students (lecturers pass them on)
def newStudentsPassword(collectTempUserCreds):
  with open("newUsers.txt", "w", newline='') as file:
    writer = csv.writer(file) 
  
    # Write table header with hardcoded KEYS
    writer.writerow(NEW_USER_KEYS) 
  
    # Write data
    for user in collectTempUserCreds:
      writer.writerow(user)
  file.close()


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
  studentsInClass = db.execute("SELECT studentEmail FROM classes WHERE courseId = ? AND lectureOrTutorial = ? AND sectionId = ?" ,(courseId,lectureOrTutorial,sectionId))
  studentsInClass = [row[0] for row in studentsInClass.fetchall()]
  if len(students) < maxStudents:
    for student in students:
      studentId = student[0]
      studentName = student[1]
      if studentId not in studentsInClass:
        db.execute('INSERT INTO classes (courseId,lecturerEmail,studentEmail,studentName,lectureOrTutorial,sectionId) VALUES(?,?,?,?,?,?)', (courseId,lecturerId,studentId,studentName,lectureOrTutorial,sectionId))
        con.commit()
        print("Added to classes")
      else:
        print("Student already exists")


# checks if user is in a group
def isUserInGroup(studentId, courseId, sectionId):
  # Query the database to check if the student is already in any group for the specified course, trimester, and section
  existing_group = db.execute("SELECT * FROM studentGroups WHERE courseId = ? AND sectionId = ? AND membersStudentEmail LIKE ?", (courseId, sectionId, f"%{studentId}%"))
  existing_group = db.fetchone()
  return existing_group is not None


def addIntoGroups(studentsToGroup,groupNumToAdd,section):
  courses = db.execute("SELECT * FROM courses")  # Assuming this fetches courses based on user input
  courses = db.fetchall()
  course = courses[0]
  courseId, sectionId, memberLimit = course[0], course[6], course[3]
  
  # Fetch existing groups for the course
  existing_groups = db.execute("SELECT groupNum FROM studentGroups WHERE courseId = ? AND sectionId = ?", (courseId, sectionId))
  existing_groups = db.fetchall()
  existing_groups = [group[0] for group in existing_groups]
  
  grouped_students = []  # List to hold students for each group

  if section != sectionId:
    return print("Wrong section!")
  for group in groupNumToAdd:
    group_exists = False
    for existingGroup in existing_groups:
      if group == existingGroup:
        print(f"Group {group} already exists")
        group_exists = True
        break  # Exit the inner loop if group already exists
    if group_exists:
      continue  # Skip to the next iteration of the outermost loop

    # If the group doesn't exist, proceed with processing students
    for student in studentsToGroup:
      studentId, studentSectionAndGroup = student[0], student[2].split("-")
      section, studentGroupNum = studentSectionAndGroup[0], studentSectionAndGroup[1]

      if isUserInGroup(student[0], courseId, sectionId):
        # Check if the student is already in any group
        print(f"Student {student[0]} is already in a group.")
        continue  # Skip adding this student to any group
      elif studentGroupNum == group:
        grouped_students.append(studentId)

    # If the current group is full or it's the last student
    if len(grouped_students) == memberLimit:
      # Insert current group into the database
      db.execute('INSERT INTO studentGroups (courseId, sectionId, groupNum, membersStudentEmail, memberLimit) VALUES (?, ?, ?, ?, ?)',(courseId,  sectionId, group, ','.join(grouped_students), memberLimit))
      con.commit()
      
      grouped_students = []  # Reset list for the next group
  print("Done grouping students.")


# changing passwords
def checkPasswords(currentPassword,newPassword,confirmPassword,email):
  if not currentPassword or not newPassword or not confirmPassword:
    flash("INPUT FIELDS ARE EMPTY!")
    return redirect("/changePassword")
  elif currentPassword == newPassword:
    flash("CANNOT CHANGE CURRENT PASSWORD TO SAME PASSWORD")
    return redirect("/changePassword")
  elif not re.match(r"^(?=.*[a-z])(?=.*\d)[A-Za-z\d]{8,}$", newPassword):
    # ^ => start of string
    # checks if password contains at both alphabets and numbers, and also if it is 8 characters long
    # (?=.*[a-z]) => checks if there is at least one small letter
    # (?=.*\d) => checks if there are digits
    # [A-Za-z\d]{8,} => checks if the newPassword has a combination of alphabets and numbers that is 8 char long
    # $ => end of string
    flash("NEW PASSWORD MUST CONTAIN AT LEAST 1 UPPERCASE LETTER,1 LOWERCASE LETTER AND 1 NUMBER, AND BE AT LEAST 8 CHARACTERS LONG")
    return redirect("/changePassword")
  elif newPassword != confirmPassword:
    flash("NEW PASSWORDS DO NOT MATCH")
    return redirect("/changePassword")
  else:  # if all fields are right
    return checkDatabasePasswords(newPassword,email)
  

# checks if new password is the same as the old password
def checkDatabasePasswords(newPassword,email):
  userPassword = db.execute("SELECT password FROM users WHERE email = ?", (email,))
  userPassword = db.fetchone()
  userPassword = userPassword[0]
  passwordsMatch = check_password_hash(userPassword,newPassword)
  if passwordsMatch == True:
    flash("CANNOT CHANGE PASSWORD TO EXISTING PASSWORD")
    return redirect("/changePassword")
  elif passwordsMatch == False:
    changePassword(newPassword,email)
    flash("SUCCESSFULLY CHANGED PASSWORD")
    return redirect("/")


# changes password in database
def changePassword(newPassword,email):
  newPassword = generate_password_hash(newPassword)
  db.execute("UPDATE users SET password = ? WHERE email = ?", (newPassword, email))
  con.commit()


# gets the courses the current user's is registered in
def getRegisteredCourses(studentEmail):
  classes = db.execute("SELECT courseId FROM classes WHERE studentEmail = ?", (studentEmail,))
  classes = db.fetchall()
  coursesId = [row[0] for row in classes]
  registeredClasses = []
  for course in coursesId:
    db.execute("SELECT courseName FROM courses WHERE courseId = ?", (course,))
    courseName = db.fetchone()
    wholeCourseName = course + " - " + courseName[0]
    registeredClasses.append([wholeCourseName])
  return registeredClasses


# adds a course to the database
def addingClasses(courseId, courseName):
  currentcourses = db.execute("SELECT courseId FROM courses").fetchall()
  for currentcourse in currentcourses:
    if courseId == currentcourse[0]:
      print("course already exists.")
      return False
    else:
      return True
    
  if addingClasses == True:
      db.execute('INSERT INTO courses (courseId, courseName) VALUES(?,?)', (courseId, courseName))
      con.commit()
      print("successfully added course.")

  # make function for add class groups button



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


#adds user to database
def addUserToDatabase(email, username):
  existingEmails = db.execute("SELECT email FROM users")
  existingEmails = list({email[0] for email in existingEmails})    # turn existing users into a list
  if email in existingEmails:
    return 
  userId = email.split("@")[0]
  if userId.startswith("MU"):
    role = "LECTURER"
  else:
    role = "STUDENT"
  db.execute("INSERT INTO users (id,email,name,role) VALUES(?,?,?,?)",(userId,email,username,role))
  con.commit()



# gets number and members of the group
def getMembers(session):
  # Get the current user's details
  currentstudent = db.execute("SELECT * FROM users WHERE email = ?", (session.get("email"),))
  currentstudent = db.fetchone()
  currentStudentId = currentstudent[0]
 
  # Get the class details for the current student
  # make it so that it understands the current student's class on button clicked
  classes = db.execute("SELECT membersStudentEmail FROM studentGroups WHERE membersStudentEmail LIKE ?", (f"%{currentStudentId}%",))
  classes = db.fetchone()
  # grabs Ids of the members
  memberIdList = []
  memberIdList = classes[0].split(",")
  for memberId in memberIdList:
    member = db.execute("SELECT name FROM users WHERE email = ?", (memberId,))
    member = member.fetchone()
    memberIdList[memberIdList.index(memberId)] = member[0]
  return memberIdList,classes

def reviewIntoDatabase(courseId,sectionId,groupNum,reviewerEmail,reviewData,assessmentData):
  db.execute("INSERT INTO reviews (courseId,sectionId,groupNum,reviewerEmail,reviewData,assessmentData) VALUES(?,?,?,?,?,?)",(courseId,sectionId,groupNum,reviewerEmail,reviewData,assessmentData))
  con.commit()
  print("Review added to database")
