from cs50 import SQL

db = SQL("sqlite:///database.db")

users = db.execute("SELECT * FROM USERS")

# Hard coded KEYS just in case
KEYS = ["id","username","password", "position"]
values = list(users[0].values())

# Prints KEYS into csv first
file = open("csv.txt","w")
for i in range(len(KEYS)):
  if i < len(KEYS) -1 :
    file.write(KEYS[i] + ",")
  else:
    file.write(KEYS[i] +"\n")

# Writes data into csv  (for now just 1 line)
for i in range(len(values)):
  if i < len(values) -1 :
    file.write(str(values[i]) + ",")
  else:
    file.write(str(values[i]))

file.close()

file = open("csv.txt","r")
print(file.read())