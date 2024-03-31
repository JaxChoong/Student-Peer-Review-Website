from cs50 import SQL

db = SQL("sqlite:///database.db")

users = db.execute("SELECT * FROM USERS")
# Hard coded KEYS just in case
KEYS = ["id","username","password", "position"]

# Prints KEYS into csv first
file = open("csv.txt","w")
for i in range(len(KEYS)):
  if i < len(KEYS) -1 :
    file.write(KEYS[i] + ",")
  else:
    file.write(KEYS[i] +"\n")

# Writes data into csv  (for now just 1 line)
for i in range(len(users)):
  values = list(users[i].values())
  for j in range(len(values)):
    if j < len(values) -1 :
      file.write(str(values[j]) + ",")
    else:
      file.write(str(values[j]) +"\n")

file.close()

file = open("csv.txt","r")
print(file.read())