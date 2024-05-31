document.addEventListener('DOMContentLoaded', () => {
  const ratings = document.querySelectorAll('.rating');
  const adjustRatingsButton = document.querySelector('#adjustRatingsButton');
  const submitButton = document.querySelector('#submit');
  adjustRatingsButton.addEventListener('click', () => {
    adjustRatings();
  });
  ratings.forEach(rating => {rating.addEventListener('input', () => {
    submitButton.disabled = true;
  });
  ratings.forEach(rating => {rating.addEventListener('focusout', () => {
    if (rating.value > 5){
      rating.value = 5;
    }
  })
})
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
  submitButton.disabled = !submitButton.disabled;
}
