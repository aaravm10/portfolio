/* navbar.js - mobile hamburger toggle */

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('#nav-toggle');
  const links = document.querySelector('#nav-links');

  if (toggle && links) {
    toggle.addEventListener('click', () => {
      const open = links.classList.toggle('open');
      toggle.classList.toggle('open', open);
    });

    /* close menu when a link is clicked on mobile */
    links.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        links.classList.remove('open');
        toggle.classList.remove('open');
      });
    });
  }
});