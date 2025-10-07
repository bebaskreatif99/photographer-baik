document.addEventListener('DOMContentLoaded', () => {

    // --- Header Scroll Effect ---
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // --- Hamburger Menu for Mobile ---
    const hamburger = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.navbar-links');
    const navLinkItems = document.querySelectorAll('.navbar-links a, .dropdown .dropbtn');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleNav();
        });
    }

    // Toggle dropdown on mobile
    const dropdown = document.querySelector('.dropdown');
    if (dropdown) {
        const dropbtn = dropdown.querySelector('.dropbtn');
        dropbtn.addEventListener('click', (e) => {
            if (window.innerWidth <= 992) {
                e.preventDefault(); // Prevent link navigation on mobile
                dropdown.classList.toggle('active');
            }
        });
    }

    function toggleNav() {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('active');
        document.body.classList.toggle('no-scroll'); // Optional: prevent scrolling when menu is open
    }

    // Close menu when a link is clicked
    navLinkItems.forEach(item => {
        if (!item.parentElement.classList.contains('dropdown')) {
            item.addEventListener('click', () => {
                if (navLinks.classList.contains('active')) {
                    toggleNav();
                }
            });
        }
    });

    // --- Scroll To Top Button ---
    const scrollToTopBtn = document.getElementById("scrollToTopBtn");
    if (scrollToTopBtn) {
        window.onscroll = function() {
            if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
                scrollToTopBtn.style.display = "block";
            } else {
                scrollToTopBtn.style.display = "none";
            }
        };
        scrollToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
    
    // --- Hero Swiper ---
    if (typeof Swiper !== 'undefined') {
        const heroSwiper = new Swiper('.hero-swiper', {
            loop: true,
            effect: 'fade',
            speed: 1500,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
        });
    }
    
    // --- Fade-in Animation on Scroll ---
    const fadeInElements = document.querySelectorAll('.fade-in-element');
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    fadeInElements.forEach(element => {
        observer.observe(element);
    });
});

// --- SimpleLightbox Initialization (using jQuery) ---
$(function(){
    if (typeof $.fn.simpleLightbox !== 'undefined') {
        $('.gallery-grid a').simpleLightbox({
            overlayOpacity: 0.9,
            animationSpeed: 250,
            fadeSpeed: 300,
            captionsData: 'alt',
            captionDelay: 250,
        });
    }
});