(function() {
    var track = document.querySelector('.testimonials-cards');
    var prevButton = document.querySelector('.testimonials-nav-prev');
    var nextButton = document.querySelector('.testimonials-nav-next');

    if (!track || !prevButton || !nextButton) return;

    function cardStep() {
        var card = track.querySelector('.testimonial-card');
        if (!card) return 0;
        var gap = parseFloat(getComputedStyle(track).gap) || 0;
        return card.getBoundingClientRect().width + gap;
    }

    prevButton.addEventListener('click', function() {
        track.scrollBy({
            left: -cardStep(),
            behavior: 'smooth'
        });
    }   );
    nextButton.addEventListener('click', function() {
        track.scrollBy({
            left: cardStep(),
            behavior: 'smooth'
        });
    });
})();