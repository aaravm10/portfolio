/* transformation-slider.js – before/after slider */
(function () {
    var slider = document.getElementById('transformation-slider');
    var afterClip = document.getElementById('after-clip');
    var handle = document.getElementById('slider-handle');

    if (!slider || !afterClip || !handle) return;

    // set the position of the slider based on the percentage
    function setPosition(percent) {
        percent = Math.max(0, Math.min(100, percent));
        afterClip.style.width = percent + '%';
        afterClip.style.setProperty('--clip', percent);
        handle.style.left = percent + '%';
        handle.setAttribute('aria-valuenow', Math.round(percent));
    }

    // get the percentage of the slider based on the x-coordinate of the mouse
    function getPercent(e) {
        var rect = slider.getBoundingClientRect();
        var x = e.touches ? e.touches[0].clientX : e.clientX;
        return ((x - rect.left) / rect.width) * 100;
    }
    
    /* Drag handle */
    handle.addEventListener('mousedown', function () {
        function move(e) { setPosition(getPercent(e)); }
        function up() {
            document.removeEventListener('mousemove', move);
            document.removeEventListener('mouseup', up);
        }
        document.addEventListener('mousemove', move);
        document.addEventListener('mouseup', up);
    });

    /* Click on slider to jump */
    slider.addEventListener('click', function (e) {
        if (e.target === handle || handle.contains(e.target)) return;
        setPosition(getPercent(e));
    });

    setPosition(50); /* start at 50% */
  })();