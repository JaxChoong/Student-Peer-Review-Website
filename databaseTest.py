from cs50 import SQL

db = SQL("sqlite:///database.db")

users = db.execute("SELECT * FROM USERS")


print(users[0]["id"])
print(users[0]["username"])
print(users[0]["password"])
print(users[0]["position"])