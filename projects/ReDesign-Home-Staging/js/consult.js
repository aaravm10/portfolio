/* consult.js - Form submission logic and FAQ accordion for consult.html */

/* fallback for when PHP server is not running */
/* intercepts form submit and redirects to confirmation.html after validating that server is not running */
const form = document.getElementById('consult-form');

if (form) {
    form.addEventListener('submit', function(e) {

        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const message = document.getElementById('message').value.trim();

            /* only intercept if not running on a server */
            if (window.location.protocol === 'file:') {
                e.preventDefault();
                if (name && email && message) {
                    window.location.href = 'form-utils/confirmation.html';
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {

    const faqList = document.querySelector('.faq-list');
    if (!faqList) return;

    faqList.querySelectorAll('.faq-question').forEach(btn => {
        btn.addEventListener('click', () => {
            const isOpen = btn.getAttribute('aria-expanded') === 'true';
            const answer = btn.nextElementSibling;
            const item = btn.closest('.faq-item');

            /* close all others */
            faqList.querySelectorAll('.faq-question').forEach(other => {
                if (other !== btn) {
                    other.setAttribute('aria-expanded', 'false');
                    other.nextElementSibling.hidden = true;
                    other.closest('.faq-item').classList.remove('open');
                }
            });

            /* toggle clicked one */
            btn.setAttribute('aria-expanded', !isOpen);
            answer.hidden = isOpen;
            item.classList.toggle('open', !isOpen);
        });
    });

});
