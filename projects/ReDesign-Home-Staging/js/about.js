/* about.js - team member carousel */

document.addEventListener('DOMContentLoaded', () => {

    const track   = document.querySelector('.carousel-track');
    const wrapper = document.querySelector('.carousel-track-wrapper');
    const prevBtn = document.querySelector('.carousel-btn.prev');
    const nextBtn = document.querySelector('.carousel-btn.next');

    if (!track || !prevBtn || !nextBtn) return;

    const original = Array.from(track.children);
    const total    = original.length;

    /* clone all cards and append for infinite loop */
    original.forEach(card => {
        track.appendChild(card.cloneNode(true));
    });

    let current = 0;

    /* recalculate visible on every call so resize is always correct */
    function getVisible() {
        return window.innerWidth <= 768 ? 1 : 3;
    }

    function cardWidth() {
        return wrapper.offsetWidth / getVisible();
    }

    /* set all card widths based on current visible count */
    function updateCardWidths() {
        const width = cardWidth();
        Array.from(track.children).forEach(card => {
            card.style.minWidth = width + 'px';
        });
    }

    function goTo(index, animate = true) {
        track.style.transition = animate ? 'transform 0.4s ease' : 'none';
        current = index;
        track.style.transform = `translateX(-${current * cardWidth()}px)`;
    }

    nextBtn.addEventListener('click', () => {
        current++;
        goTo(current);

        /* silently reset to start after animation */
        if (current >= total) {
            setTimeout(() => goTo(0, false), 400);
        }
    });

    prevBtn.addEventListener('click', () => {
        if (current <= 0) {
            goTo(total, false);
            setTimeout(() => {
                current = total - 1;
                goTo(current);
            }, 20);
        } else {
            current--;
            goTo(current);
        }
    });

    /* on resize recalculate card widths and reposition */
    window.addEventListener('resize', () => {
        updateCardWidths();
        goTo(current, false);
    });

    /* init */
    updateCardWidths();
    goTo(0, false);

});