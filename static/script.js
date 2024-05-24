document.addEventListener('DOMContentLoaded', () => {
  const adjustRatingsButton = document.querySelector('#adjustRatingsButton');
  const submitButton = document.querySelector('#submit');
  adjustRatingsButton.addEventListener('click', () => {
    adjustRatings();
  });
});

function adjustRatings() {
  const ratings = document.querySelectorAll('.rating');
  const numStuds = ratings.length;
  let totalRating = 0;
  ratings.forEach(rating => {totalRating += parseFloat(rating.value);});
  ratings.forEach(rating => {
    AdjR = (parseFloat(rating.value) / totalRating) * 3 * numStuds;
    AdjR = Number(AdjR.toFixed(2));
    console.log(AdjR);
    rating.value = AdjR.toString();
  }
  );
  changeButtonState();
}

function changeButtonState(){
  const submitButton = document.querySelector('#submit');
  submitButton.disabled = false;
}
// function adjustedRatings(Rat, totalRating, numOfStuds):
//     AdjR = (Rat / totalRating) * 3 * numOfStuds
//     AdjR = round(AdjR, 2)
//     return AdjR #use this var