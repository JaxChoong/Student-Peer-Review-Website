from cs50 import SQL

db = SQL("sqlite:///database.db")

users = db.execute("SELECT * FROM USERS")

KEYS = ["id","username","password", "position"]
# print(users[0]["id"])
# print(users[0]["username"])
# print(users[0]["password"])
# print(users[0]["position"])
values = list(users[0].values())


file = open("csv.txt","w")
for i in range(len(KEYS)):
  if i < len(KEYS) -1 :
    file.write(KEYS[i] + ",")
  else:
    file.write(KEYS[i] +"\n")

for i in range(len(values)):
  if i < len(values) -1 :
    file.write(str(values[i]) + ",")
  else:
    file.write(str(values[i]))

file.close()

file = open("csv.txt","r")
print(file.read())