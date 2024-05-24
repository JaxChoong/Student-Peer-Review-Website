document.addEventListener('DOMContentLoaded', () => {
  const adjustRatingsButton = document.querySelector('#adjustRatingsButton');
  adjustRatingsButton.addEventListener('click', () => {
    adjustRatings();
  });
});

function adjustRatings() {
  const ratings = document.querySelectorAll('.rating');
  ratings.forEach(rating => {
    console.log(rating.value);
  });
}