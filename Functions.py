# "rating" is the current ith student that is getting adjusted
# "totalRating" is the total rating giving (unadjusted)
# "numOfStud" self explanitory

def adjustedRatings(Rat, totalRating, numOfStuds):
    AdjR = (Rat / totalRating) * 3 * numOfStuds
    AdjR = round(AdjR, 2)
    print(AdjR) #use this var

# 4 3 2 1
#this checks weither the student did the peer review
def done_Peer_Review(column1, column2, column3, column4):
    peerReviewDone = False
    if column1 != 0 and column2 != 0 and column3 != 0 and column4 != 0:
        peerReviewDone = True
    else:
        pass
    print(peerReviewDone) #use this var

# 5 3 3 3
adjustedRatings(3, 14, 4)
# 4.29 2.57 2.57 2.57
# total = 12 (NO MATTER WHAT)

done_Peer_Review(0, 0, 0, 0)









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
