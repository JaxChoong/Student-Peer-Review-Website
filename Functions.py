import databaseFunctions as df

EMAIL = ("student.mmu.edu.my", "soffice.mmu.edu.my", "mmu.edu.my", "office.mmu.edu.my")

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
        