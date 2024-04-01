from cs50 import SQL
import csv

db = SQL("sqlite:///database.db")

users = db.execute("SELECT * FROM USERS")
existingUsers = db.execute("SELECT id,username FROM USERS")
existingUsers = list({(user['id'],user['username']) for user in existingUsers})    # turn existing users into a list


# Hard coded KEYS just in case
KEYS = ["id","username","password", "position"]

# Copy this function into the main code
def databaseToCsv():
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

    if next(reader) != KEYS:                      # checks if header of csv matches database
      print("Invalid CSV format. Header does not match expected format.")
      return
    
    for row in reader:   # loops through each row in the csv
      # get current userid and username
      user_id= int(row[0])
      username= row[1]
      if ( user_id,username) not in existingUsers and row:  # if user not already existing and not empty row
        print("added to database")
        db.execute("INSERT INTO USERS (id,username,password,position) VALUES(?,?,?,?)",row[0], row[1],row[2],row[3])
      else:
        print(f"User {user_id}, {username} already Exists.")
  file.close()

csvToDatabase()