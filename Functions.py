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
        
# "rating" is the current ith student that is getting adjusted
# "totalRating" is the total rating giving (unadjusted)
# "numOfStud" self explanitory

def adjustedRatings(Rat, totalRating, numOfStuds):
    AdjR = (Rat / totalRating) * 3 * numOfStuds
    print(f"{AdjR:.2f}")

# 5 3 3 3
adjustedRatings(3, 14, 4)
# 4.29 2.57 2.57 2.57
# total = 12 (NO MATTER WHAT)