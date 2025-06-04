document.addEventListener('DOMContentLoaded', function() {
    const stars = document.querySelectorAll('.star-icon');
    const ratingInput = document.getElementById('id_rating');
    

    const currentRating = parseInt(ratingInput.value) || 0;
    if (currentRating > 0) {
        highlightStars(currentRating);
    }
    

    stars.forEach(star => {
        star.addEventListener('click', function() {
            const value = parseInt(this.getAttribute('data-value'));
            ratingInput.value = value;
            highlightStars(value);
        });
        

        star.addEventListener('mouseover', function() {
            const value = parseInt(this.getAttribute('data-value'));
            highlightStars(value);
        });
        

        star.addEventListener('mouseout', function() {
            const currentValue = parseInt(ratingInput.value) || 0;
            highlightStars(currentValue);
        });
    });
    
    function highlightStars(count) {
        stars.forEach((star, index) => {
            if (index < count) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }
});