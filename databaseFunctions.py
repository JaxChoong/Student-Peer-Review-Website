import sqlite3
import csv

con = sqlite3.connect("database.db", check_same_thread=False)      # connects to the database
db = con.cursor()                         # cursor to go through database (allows db.execute() basically)

existingEmails = db.execute("SELECT email FROM users")
existingEmails = list({user[0] for user in existingEmails})    # turn existing users into a list


# Hard coded KEYS just in case
KEYS = ["id","name","email", "role"]
ROLES = ["STUDENT","LECTURER"]

# Copy this function into the main code
def databaseToCsv():
  users = db.execute("SELECT * FROM users")
  users = db.fetchall()          # get all the users cuz this library doesnt do it for you
  with open("databaseToCsv.txt", "w", newline='') as file:    # opens txt file and newline is empty to prevent "\n" to be made automatically
    writer = csv.writer(file)                               # creates writer to write into file as csv 
    
    # Write table header  with hardcoded KEYS constant 
    writer.writerow(KEYS) 
    
    # Write data rows
    for user in users:
      writer.writerow(user)
  file.close()


def csvToDatabase():
  with open("databaseToCsv.txt", newline="") as file:
    reader = csv.reader(file)
    header =  next(reader)
    if header != KEYS:                      # checks if header of csv matches database
      print("Invalid CSV format. Header does not match expected format.")
      return
    
    for row in reader:   # loops through each row in the csv
      foundEmptyValue = False     # flag for empty values
      if len(row) != len(KEYS):    # check for missing coloumns
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
      user_id= int(row[0])
      name= row[1]
      email = row[2]
      userRole = row[3]
      userRole= userRole.upper()
      if userRole not in ROLES:      # check if user Role exists
        print(f"Role {userRole} does not exist.")
        continue
      elif ( email) not in existingEmails and row:  # if user not already existing and not empty row
        db.execute("INSERT INTO users (id,name,email,role) VALUES(?,?,?,?)",(user_id, name,email,userRole))
        con.commit()
        print("added to database")
      else:
        print(f"User {user_id}, {name} already Exists.")
  file.close()

def checkEmail(session):
  print(session["email"], existingEmails)
  if session["email"] not in existingEmails:
    db.execute("INSERT INTO users (id,name,email,role) VALUES(?,?,?,?)",(session["google_id"],session["name"],session["email"],"STUDENT"))
    con.commit()
  else:
    pass
    

# db.execute('''CREATE TABLE IF NOT EXISTS classes (
#         courseId TEXT,
#         trimesterCode INTEGER NOT NULL,
#         lecturerId TEXT NOT NULL,
#         studentId INTEGER NOT NULL,
#         studentName TEXT  NOT NULL,
#         lectureOrTutorial TEXT NOT NULL,
#         sectionCode TEXT NOT NULL          
#     )''')

# db.execute('''DROP TABLE courses''')


# db.execute("INSERT INTO courses (courseId,courseName,trimesterCode,lecturerId,studentNum,lectureOrTutorial,sectionCode) VALUES(?,?,?,?,?,?,?)",("CSP1123","MINI IT PROJECT",2410,"MU1234",30,"LECTURE","TT4L"))
# con.commit()

def addIntoClasses():
  courses = db.execute("SELECT * FROM courses")  # change this to integrate into website(select from user input)
  courses = db.fetchall()
  course = courses[0]
  students = db.execute("SELECT * FROM users WHERE role = ?","STUDENT")
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
  courseId , trimesterCode ,sectionCode = course[0], course[2],course[7]
  memberLimit = 4     #current placeholder member limit
  # change this to select group number from HTML
  groups = db.execute("SELECT memberLimit FROM studentGroups WHERE courseId = ? AND trimesterCode =? AND sectionCode = ?" ,(courseId,trimesterCode,sectionCode))
  groups = db.fetchall()
  if len(groups) > 0:   # if there are groups already
    maxGroupMembers = db.execute("SELECT memberLimit FROM studentGroups WHERE courseId = ? AND trimesterCode =? AND sectionCode = ?" ,(courseId,trimesterCode,sectionCode))
    maxGroupMembers = db.fetchall()
    groupNum = db.execute("SELECT DISTINCT groupNum FROM studentGroups WHERE courseId = ? AND trimesterCode =? AND sectionCode = ?" ,(courseId,trimesterCode,sectionCode))
    groupNum = len(groupNum) + 1
  else:  # if there are no groups
    # change this to select group members from html
    students = db.execute("SELECT studentId from classes WHERE courseId = ? AND trimesterCode =? AND sectionCode = ?" ,(courseId,trimesterCode,sectionCode))
    students = db.fetchall()
    groupedStudents = ""
    for i in range(len(students)):
      if i+1 == len(students):
        groupedStudents += students[i][0]
      else:
        groupedStudents += students[i][0] + ","
    groupNum = db.execute("SELECT DISTINCT groupNum FROM studentGroups WHERE courseId = ? AND trimesterCode =? AND sectionCode = ?" ,(courseId,trimesterCode,sectionCode))
    groupNum = db.fetchall()
    groupNum = f"{sectionCode}-{len(groupNum) + 1}"
    db.execute('INSERT INTO studentGroups (courseId,trimesterCode,sectionCode,groupNum,membersStudentId,memberLimit) VALUES (?,?,?,?,?,?)', (courseId,trimesterCode,sectionCode,groupNum,groupedStudents,memberLimit))
    con.commit()

    
addIntoGroups()