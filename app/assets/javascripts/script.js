document.addEventListener('DOMContentLoaded', () => {
  const ratings = document.querySelectorAll('.rating');
  const adjustRatingsButton = document.querySelector('#adjustRatingsButton');
  const submitButton = document.querySelector('#submit');
  const warning = document.querySelectorAll('.warning');

  adjustRatingsButton.addEventListener('click', () => {
    adjustRatings();
  });

  ratings.forEach(rating => {
    rating.addEventListener('input', () => {
      validateRatings();
    });

    rating.addEventListener('focusout', () => {
      if (rating.value > 5) {
        rating.value = 5;
      }
      else if (rating.value < 1) {
        rating.value = 1;
      }
    });
  });

  function validateRatings() {
    let allValid = true;
    ratings.forEach(rating => {
      if (isNaN(rating.value) || rating.value.trim() === "") {
        allValid = false;
      }
    });

    if (allValid) {
      warning.forEach(w => {
        w.textContent = "Please adjust the ratings before submitting!";
      });
      submitButton.disabled = true;
      adjustRatingsButton.disabled = false;
    } else {
      warning.forEach(w => {
        w.textContent = "Please enter a valid number in ratings!";
      });
      submitButton.disabled = true;
      adjustRatingsButton.disabled = true;
    }
  }

  function adjustRatings() {
    const numStuds = ratings.length;
    let totalRating = 0;
    ratings.forEach(rating => {
      totalRating += parseFloat(rating.value);
    });

    ratings.forEach(rating => {
      let adjR = (parseFloat(rating.value) / totalRating) * 3 * numStuds;
      adjR = Number(adjR.toFixed(2));
      console.log(adjR);
      rating.value = adjR.toString();
    });

    warning.forEach(w => {
      w.textContent = "";
    });
    submitButton.disabled = false;
  }
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
  const warning = document.querySelector('.warning');
  warning.textContent = "";
}

function changeButtonState(){
  const submitButton = document.querySelector('#submit');
  submitButton.disabled = !submitButton.disabled;
}
