from cs50 import SQL
import csv

db = SQL("sqlite:///database.db")

users = db.execute("SELECT * FROM USERS")

# RUN THIS TO ADD ANOTHER USER TO DATABASE
# db.execute("INSERT INTO USERS(username,password,position) VALUES(?,?,?)", 'Eric','000','STUDENT')


# Hard coded KEYS just in case
KEYS = ["id","username","password", "position"]

# Copy this function into the main code
def writeToCsv():
  with open("databaseToCsv.txt", "w", newline='') as file:    # opens txt file and newline is empty to prevent "\n" to be made automatically
    writer = csv.writer(file)                               # creates writer to write into file as csv 
    
    # Write table header  with hardcoded KEYS constant 
    writer.writerow(KEYS) 
    
    # Write data rows
    for user in users:
      writer.writerow(user.values())
  file.close()

# writeToCsv()
# file = open("databaseToCsv.txt","r")
# print(file.read())

def csvToDatabase():
  with open("databaseToCsv.txt", newline="") as file:
    reader = csv.reader(file)
    if next(reader) == KEYS:
      for row in reader:
        db.execute("INSERT INTO USERS (username,password,position) VALUES(?,?,?)", row[1],row[2],row[3])