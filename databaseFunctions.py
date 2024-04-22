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
    

db.execute('''CREATE TABLE IF NOT EXISTS studentGroups (
        course_id TEXT PRIMARY KEY,
        trimester_id TEXT NOT NULL,
        section TEXT NOT NULL,
        group_num TEXT NOT NULL,
        members_studentid TEXT NOT NULL,
        member_limit INTEGER NOT NULL
    )''')