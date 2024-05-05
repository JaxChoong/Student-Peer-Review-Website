import sqlite3
import csv
import re # this is regex (regular expression)
import secrets   # generate random string for password initially
from werkzeug.security import check_password_hash, generate_password_hash  #hashes passwords

from flask import flash,redirect

con = sqlite3.connect("database.db", check_same_thread=False)      # connects to the database
db = con.cursor()                         # cursor to go through database (allows db.execute() basically)

existingEmails = db.execute("SELECT email FROM users")
existingEmails = list({email[0] for email in existingEmails})    # turn existing users into a list

# Hard coded KEYS just in case
KEYS = ["id","email","name", "role"]
CSV_KEYS = ["email","name","role"]
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
  with open("addToDatabase.txt", newline="") as file:
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
      userId = int(row[0])
      userEmail = str(userId) + "@soffice.mmu.edu.my"
      password = secrets.token_urlsafe(32)
      name = row[1]
      role = row[2]
      role= role.upper()
      hashedPassword = generate_password_hash(password)
      
      # check if user Role exists
      if role not in ROLES:      
        print(f"Role {role} does not exist.")
        continue
      
      # if user not already existing and not empty row
      elif ( userEmail) not in existingEmails and row:
        gotNewUsers_flag = True
        collectTempUserCreds.append([f"{userEmail}",f"{name}", f"{password}"])
        db.execute("INSERT INTO users (id,email,name,password,role) VALUES(?,?,?,?,?)",(userId,userEmail,name,hashedPassword,role))
        con.commit()
        print("added to database")
      else:
        print(f"User {userId} already Exists.")
    if gotNewUsers_flag == True:
      newStudentsPassword(collectTempUserCreds) # function def'd later
  file.close()

# verifies incoming user
def checkUser(email, password, session):
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
  courseId , trimesterCode, lecturerId, lectureOrTutorial,sessionCode = course[0], course[2],course[3],course[6],course[7]
  studentsInClass = db.execute("SELECT studentId FROM classes WHERE courseid = ? AND trimesterCode =? AND lectureOrTutorial = ? AND sessionCode = ?" ,(courseId,trimesterCode,lectureOrTutorial,sessionCode))
  studentsInClass = [row[0] for row in studentsInClass.fetchall()]
  if len(students) < maxStudents:
    for student in students:
      studentId = student[0]
      studentName = student[1]
      if studentId not in studentsInClass:
        db.execute('INSERT INTO classes (courseId,trimesterCode,lecturerId,studentId,studentName,lectureOrTutorial,sessionCode) VALUES(?,?,?,?,?,?,?)', (courseId,trimesterCode,lecturerId,studentId,studentName,lectureOrTutorial,sessionCode))
        con.commit()
        print("Added to classes")
      else:
        print("Student already exists")
  print("done all")

# changing passwords
def checkPasswords(currentPassword,newPassword,confirmPassword,session):
  if not currentPassword or not newPassword or not confirmPassword:
    flash("INPUT FIELDS ARE EMPTY!")
    return redirect("/changePassword")
  elif currentPassword == newPassword:
    flash("CANNOT CHANGE CURRENT PASSWORD TO SAME PASSWORD")
    return redirect("/changePassword")
  elif not re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d]{8,}$", newPassword):
    # ^ => start of string
    # checks if password contains at both alphabets and numbers, and also if it is 8 characters long
    # (?=.*[A-Z]) => checks if there is at least one capital letter
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
    userPassword = db.execute("SELECT password FROM users WHERE email = ?", (session.get("email"),))
    userPassword = db.fetchone()
    userPassword = userPassword[0]
    passwordsMatch = check_password_hash(userPassword,currentPassword)
    if check_password_hash(userPassword,newPassword) == True:
      flash("CANNOT CHANGE PASSWORD TO EXISTING PASSWORD")
      return redirect("/changePassword")
    if passwordsMatch == True:
      changePassword(newPassword,session)
      flash("SUCCESSFULLY CHANGED PASSWORD")
      return redirect("/")
    elif passwordsMatch == False:
      flash("WRONG PASSWORD")
      return redirect("/changePassword")
  
def changePassword(newPassword,session):
  newPassword = generate_password_hash(newPassword)
  db.execute("UPDATE users SET password = ? WHERE email = ?", (newPassword, session.get("email")))
  con.commit()
  flash("PASSWORD CHANGED SUCCESFULLY!")
  return redirect("/")

def getCourses():
  # change this to integrate into website(select from user input)
  courses = db.execute("SELECT courseName FROM courses" )
  courses = db.fetchall()
  courseNames = [row[0] for row in courses] # selects all the names
  if courseNames == None:
    print("Subject is not in database")
  else:
    return courseNames
  
# courseId, courseName, lectOrTut, numStudents, numGroups, Section
# db.execute("SELECT courseId FROM courses").fetchall()
def addingClasses(courseId, courseName, trimesterCode, lecturerId, numStudents, numGroups, lectOrTut, Section):
  currentcourses = db.execute("SELECT courseId FROM courses").fetchall()
  for currentcourse in currentcourses:
    if courseId == currentcourse[0]:
      print("course already exists.")
      return

    db.execute('INSERT INTO courses (courseId, courseName, trimesterCode, lecturerId, studentNum, groupNum, lectureOrTutorial, sessionCode) VALUES(?,?,?,?,?,?,?,?)', (courseId, courseName, trimesterCode, lecturerId, numStudents, numGroups, lectOrTut, Section))
    con.commit()
    print("successfully added course.")