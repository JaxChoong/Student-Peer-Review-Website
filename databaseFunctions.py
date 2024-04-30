import sqlite3
import csv
import secrets   # generate random string for password initially

con = sqlite3.connect("database.db", check_same_thread=False)      # connects to the database
db = con.cursor()                         # cursor to go through database (allows db.execute() basically)

existingEmails = db.execute("SELECT username FROM users")
existingEmails = list({user[0] for user in existingEmails})    # turn existing users into a list


# Hard coded KEYS just in case
KEYS = ["id","username","password", "role"]
CSV_KEYS = ["id","role"]
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
    if header != CSV_KEYS:                      # checks if header of csv matches database
      print(f"Invalid CSV format. Header does not match expected format.\n Use {CSV_KEYS}")
      return
    
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
      role = row[1]
      role= role.upper()
      if role not in ROLES:      # check if user Role exists
        print(f"Role {role} does not exist.")
        continue
      elif ( userEmail) not in existingEmails and row:  # if user not already existing and not empty row
        db.execute("INSERT INTO users (id,username,password,role) VALUES(?,?,?,?)",(userId,userEmail,password,role))
        con.commit()
        print("added to database")
      else:
        print(f"User {userId} already Exists.")
  file.close()

def checkEmail(session):
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


csvToDatabase()