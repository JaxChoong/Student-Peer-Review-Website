import databaseFunctions as df

EMAIL = ("student.mmu.edu.my", "soffice.mmu.edu.my", "mmu.edu.my", "office.mmu.edu.my" , "gmail.com","moe-dl.edu.my")

def VerifyEmail(id_info, session):
    email = id_info.get("email")
    emailEnding = email.split("@")
    emailEnding = emailEnding[1]
    
    if emailEnding in EMAIL:
        session["google_id"] = id_info.get("sub")
        session["name"]= id_info.get("name")
        session["email"] = id_info.get("email")

        return True
    else:
        return False
        
# rat = 5
# totalRat = 15
# numOfStuds = 4

def adjustedRatings(rat, totalRat, numOfStuds):
    AdjRat = (rat / totalRat) * 3 * numOfStuds
    print(AdjRat)

adjustedRatings(5, 15, 4)