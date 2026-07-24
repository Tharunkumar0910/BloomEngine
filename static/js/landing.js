/**
 * BloomEngine - Landing Page JavaScript
 * Handles smooth scrolling, navbar transitions, animations, and action triggers.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Scroll Reveal Animations using IntersectionObserver
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.15
  };

  const revealElements = document.querySelectorAll('.feature-card, .taxonomy-card, .step-card, .section-header');

  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  revealElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    revealObserver.observe(el);
  });

  // 2. Navbar Background Blur on Scroll
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 30) {
        navbar.style.boxShadow = '0 10px 30px -10px rgba(109, 74, 255, 0.12)';
      } else {
        navbar.style.boxShadow = 'none';
      }
    });
  }

  // 3. Smooth Scroll for Anchor Links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId && targetId !== '#') {
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
          e.preventDefault();
          targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      }
    });
  });

  // 4. Launch BloomEngine Action Buttons
  document.querySelectorAll('.btn-launch-app').forEach(btn => {
    btn.addEventListener('click', () => {
      window.location.href = '/auth';
    });
  });
});
