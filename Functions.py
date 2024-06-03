# "rating" is the current ith student that is getting adjusted
# "totalRating" is the total rating giving (unadjusted)
# "numOfStud" self explanitory

def adjustedRatings(Rat, totalRating, numOfStuds):
    AdjR = (Rat / totalRating) * 3 * numOfStuds
    AdjR = round(AdjR, 2)
    return AdjR #use this var


# "AM" = assignment marks
# "APR" = Average Peer Marks for the ith person (including his own, pre adjusting)
# "LE" = Lecturer evaluation

def calculateFinalMark(APR, LE, AM):
    AM = float(AM)

    finalmarks = (0.5) * AM + (0.25) * AM * (float(APR / 3)) + (0.25) * AM * (float(LE / 3))
    return round(finalmarks,2)
