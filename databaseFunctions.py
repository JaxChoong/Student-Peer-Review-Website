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
def databaseToCsv():
  users = db.execute("SELECT * FROM users")
  users = db.fetchall()          # get all the users cuz this library doesnt do it for you
  with open("usersInDatabase.txt", "w", newline='') as file:    # opens txt file and newline is empty to prevent "\n" to be made automatically
    writer = csv.writer(file)                               # creates writer to write into file as csv 
    
    # Write table header  with hardcoded KEYS constant 
    writer.writerow(KEYS) 
    
    # Write data rows
    for user in users:
      writer.writerow(user[0:3] + (user[4],))
  file.close()


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
      if role not in ROLES:      # check if user Role exists
        print(f"Role {role} does not exist.")
        continue
      elif ( userEmail) not in existingEmails and row:  # if user not already existing and not empty row
        gotNewUsers_flag = True
        collectTempUserCreds.append([f"{userEmail}",f"{name}", f"{password}"])
        db.execute("INSERT INTO users (id,email,name,password,role) VALUES(?,?,?,?,?)",(userId,userEmail,name,hashedPassword,role))
        con.commit()
        print("added to database")
      else:
        print(f"User {userId} already Exists.")
    if gotNewUsers_flag == True:
      newStudentsPassword(collectTempUserCreds)
  file.close()

def checkEmail(email, password, session):
  if email not in existingEmails:
    print("INTEGRATE THIS WITH OUR DATABASE FIRST RAAAAAAH")
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
      print("UR MOTHER WRONG PASSWORD LAA")
    

def newStudentsPassword(collectTempUserCreds):
  with open("newUsers.txt", "w", newline='') as file:    # opens txt file and newline is empty to prevent "\n" to be made automatically
    writer = csv.writer(file)                               # creates writer to write into file as csv 
  
    # Write table header  with hardcoded KEYS constant 
    writer.writerow(NEW_USER_KEYS) 
  
    # Write data rows
    for user in collectTempUserCreds:
      writer.writerow(user)
  file.close()

def addIntoClasses():
  courses = db.execute("SELECT * FROM courses")  # change this to integrate into website(select from user input)
  courses = db.fetchall()
  course = courses[0]
  students = db.execute("SELECT * FROM users WHERE role = ?",("STUDENT",))
  students = db.fetchall()
  maxStudents = int(course[4])
  courseId , trimesterCode, lecturerId, lectureOrTutorial,sectionCode = course[0], course[2],course[3],course[6],course[7]
  studentsInClass = db.execute("SELECT studentId FROM classes WHERE courseid = ? AND trimesterCode =? AND lectureOrTutorial = ? AND sectionCode = ?" ,(courseId,trimesterCode,lectureOrTutorial,sectionCode))
  studentsInClass = [row[0] for row in studentsInClass.fetchall()]
  if len(students) < maxStudents:
    for student in students:
      studentId = student[0]
      studentName = student[1]
      if studentId not in studentsInClass:
        db.execute('INSERT INTO classes (courseId,trimesterCode,lecturerId,studentId,studentName,lectureOrTutorial,sectionCode) VALUES(?,?,?,?,?,?,?)', (courseId,trimesterCode,lecturerId,studentId,studentName,lectureOrTutorial,sectionCode))
        con.commit()
        print("Added to classes")
      else:
        print("Student already exists")

def addIntoGroups():
  courses = db.execute("SELECT * FROM courses")  # change this to integrate into website(select from user input)
  courses = db.fetchall()
  course = courses[0]
  courseId , trimesterCode ,sectionCode ,memberLimit= course[0], course[2],course[7],course[8]
  # change this to select group number from HTML
  groups = db.execute("SELECT memberLimit FROM studentGroups WHERE courseId = ? AND trimesterCode =? AND sectionCode = ?" ,(courseId,trimesterCode,sectionCode))
  groups = db.fetchall()
  groupNum = db.execute("SELECT DISTINCT groupNum FROM studentGroups WHERE courseId = ? AND trimesterCode =? AND sectionCode = ?" ,(courseId,trimesterCode,sectionCode))
  groupNum = db.fetchall()
  groupNum = f"{sectionCode}-{len(groupNum) + 1}"

  # if len(groups) > 0:   # if there are groups already
  #   print("INTEGRATE CHECKING OF STUDENT GROUPS AND INCREMENT")
  # else:  # if there are no groups

    # change this to select group members from html
  students = db.execute("SELECT studentId from classes WHERE courseId = ? AND trimesterCode =? AND sectionCode = ?" ,(courseId,trimesterCode,sectionCode))
  students = db.fetchall()
  numberOfStudents = len(students)
  groupedStudents = ""

  if len(groups) > 0: # if there are already groups
    existingStudentGroups = db.execute("SELECT membersStudentId from studentGroups ")
    existingStudentGroups = db.fetchall()
    for group in existingStudentGroups:
      currentGroupMembers = group[0].split(sep=",")
      for i in range(numberOfStudents):
        if students[i][0] not in  currentGroupMembers and numberOfStudents <= memberLimit:
          for i in range(numberOfStudents):
            if i+1 == numberOfStudents:
              groupedStudents += students[i][0]
            else:
              groupedStudents += students[i][0] + ","
          groupNum = db.execute("SELECT DISTINCT groupNum FROM studentGroups WHERE courseId = ? AND trimesterCode =? AND sectionCode = ?" ,(courseId,trimesterCode,sectionCode))
          groupNum = db.fetchall()
          groupNum = f"{sectionCode}-{len(groupNum) + 1}"
          db.execute('INSERT INTO studentGroups (courseId,trimesterCode,sectionCode,groupNum,membersStudentId,memberLimit) VALUES (?,?,?,?,?,?)', (courseId,trimesterCode,sectionCode,groupNum,groupedStudents,memberLimit))
          con.commit()
          print("student no exists")
        else:
          print("student  exists")

  else:   # if there are no groups already
    if numberOfStudents <= memberLimit:
      for i in range(numberOfStudents):
        if i+1 == numberOfStudents:
          groupedStudents += students[i][0]
        else:
          groupedStudents += students[i][0] + ","
      db.execute('INSERT INTO studentGroups (courseId,trimesterCode,sectionCode,groupNum,membersStudentId,memberLimit) VALUES (?,?,?,?,?,?)', (courseId,trimesterCode,sectionCode,groupNum,groupedStudents,memberLimit))
      con.commit()
  print("done all")

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
