# "rating" is the current ith student that is getting adjusted
# "totalRating" is the total rating giving (unadjusted)
# "numOfStud" self explanitory

def adjustedRatings(Rat, totalRating, numOfStuds):
    AdjR = (Rat / totalRating) * 3 * numOfStuds
    AdjR = round(AdjR, 2)
    return AdjR #use this var


