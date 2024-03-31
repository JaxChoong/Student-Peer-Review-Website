from cs50 import SQL

db = SQL("sqlite:///database.db")

users = db.execute("SELECT * FROM USERS")

# RUN THIS TO ADD ANOTHER USER TO DATABASE
# db.execute("INSERT INTO USERS(username,password,position) VALUES(?,?,?)", 'Eric','000','STUDENT')


# Hard coded KEYS just in case
KEYS = ["id","username","password", "position"]

# Prints KEYS into Csv first
file = open("databaseToCsv.txt","w")
for i in range(len(KEYS)):
  if i < len(KEYS) -1 :
    file.write(KEYS[i] + ",")
  else:
    file.write(KEYS[i] +"\n")

# Writes data into Csv  (for now just 1 line)
for i in range(len(users)):            # Loop through users in the database
  values = list(users[i].values())
  for j in range(len(values)):         # Loop through each value of the user
    if j < len(values) -1 :
      file.write(str(values[j]) + ",")
    else:
      file.write(str(values[j]))
      if i < len(users)-1:             # If its not last user, then add newline after last value of current user.
        file.write("\n")

file.close()

file = open("databaseToCsv.txt","r")
print(file.read())