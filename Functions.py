# "rating" is the current ith student that is getting adjusted
# "totalRating" is the total rating giving (unadjusted)
# "numOfStud" self explanitory

def adjustedRatings(Rat, totalRating, numOfStuds):
    global AdjR
    AdjR = (Rat / totalRating) * 3 * numOfStuds
    AdjR = round(AdjR, 2)

# 5 3 3 3
adjustedRatings(3, 14, 4)
print(AdjR)
# 4.29 2.57 2.57 2.57
# total = 12 (NO MATTER WHAT)









# FUTURE IMPROVEMENTS

# def VerifyEmail(username, password):
#     emailEnding = username.split("@")
    
#     if emailEnding in EMAIL:
    
#         return True
#     else:
#         return False

# "AM" = assignment marks
# "APR" = Average Peer Marks for the ith person (including his own, pre adjusting)
# "LE" = Lecturer evaluation
# def FinalMarks(AM, APR, LE):
#     Final = (1 / 2) * AM + (1 / 4) * AM * (APR / 3) + (1 / 4) * AM * (LE / 3)
