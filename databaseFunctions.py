import sqlite3
import csv

con = sqlite3.connect("database.db")      # connects to the database
db = con.cursor()                         # cursor to go through database (allows db.execute() basically)

users = db.execute("SELECT * FROM USERS")
users = db.fetchall()          # get all the users cuz this library doesnt do it for you
existingUsers = db.execute("SELECT id,username FROM USERS")
existingUsers = list({(user[0],user[1]) for user in existingUsers})    # turn existing users into a list


# Hard coded KEYS just in case
KEYS = ["id","username","password", "position"]
POSITIONS = ["STUDENT","LECTURER"]

# Copy this function into the main code
def databaseToCsv():
  with open("databaseToCsv.txt", "w", newline='') as file:    # opens txt file and newline is empty to prevent "\n" to be made automatically
    writer = csv.writer(file)                               # creates writer to write into file as csv 
    
    # Write table header  with hardcoded KEYS constant 
    writer.writerow(KEYS) 
    
    # Write data rows
    print(f"{existingUsers}")
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
      
      # get current userid and username
      user_id= int(row[0])
      username= row[1]
      userPosition = row[3]
      userPosition= userPosition.upper()
      if userPosition not in POSITIONS:      # check if user position exists
        print(f"Position {userPosition} does not exist.")
        continue
      elif ( user_id,username) not in existingUsers and row:  # if user not already existing and not empty row
        print("added to database")
        db.execute("INSERT INTO USERS (id,username,password,position) VALUES(?,?,?,?)",user_id, username,row[2],userPosition)
      else:
        print(f"User {user_id}, {username} already Exists.")
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
#         sessionCode TEXT NOT NULL          
#     )''')

# db.execute('''DROP TABLE courses''')


# db.execute("INSERT INTO courses (courseId,courseName,trimesterCode,lecturerId,studentNum,lectureOrTutorial,sessionCode) VALUES(?,?,?,?,?,?,?)",("CSP1123","MINI IT PROJECT",2410,"MU1234",30,"LECTURE","TT4L"))
# con.commit()

def addIntoClasses():
  courses = db.execute("SELECT * FROM courses")  # change this to integrate into website(select from user input)
  courses = db.fetchall()
  course = courses[0]
  students = db.execute("SELECT * FROM users WHERE role = ?",("STUDENT",))
  students = db.fetchall()
  maxStudents = int(course[4])
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



addIntoClasses()