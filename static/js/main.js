// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {

    // --- Hamburger Menu Toggle ---
    const hamburger = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.navbar-links');
    const dropdownToggle = document.querySelector('.dropbtn');
    const dropdownParent = document.querySelector('.dropdown');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            hamburger.classList.toggle('active');
            // Jika navbar ditutup, pastikan dropdown juga tertutup
            if (!navLinks.classList.contains('active') && dropdownParent) {
                dropdownParent.classList.remove('active');
            }
        });
    }

    // --- Dropdown Toggle (for mobile and desktop) ---
    if (dropdownToggle && dropdownParent) {
        dropdownToggle.addEventListener('click', (e) => {
            // Mencegah navigasi link jika #
            e.preventDefault(); 
            // Toggle class 'active' pada parent dropdown
            dropdownParent.classList.toggle('active');
        });

        // Close dropdown if clicking outside (desktop behavior)
        document.addEventListener('click', (e) => {
            if (!dropdownParent.contains(e.target) && !hamburger.contains(e.target)) {
                dropdownParent.classList.remove('active');
            }
        });
    }

    // --- Header Scroll Effect ---
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) { // Jika discroll lebih dari 50px
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // --- Initialize Hero Swiper ---
    const heroSwiper = new Swiper('.hero-swiper', {
        loop: true,
        effect: 'fade', // Efek transisi
        speed: 1000, // Kecepatan transisi slide (ms)
        autoplay: {
            delay: 5000, // Ganti slide setiap 5 detik
            disableOnInteraction: false, // Lanjutkan autoplay setelah interaksi user
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

    // --- Scroll To Top Button ---
    const scrollToTopBtn = document.getElementById("scrollToTopBtn");

    if (scrollToTopBtn) {
        window.onscroll = function() { scrollFunction() };

        function scrollFunction() {
            if (document.body.scrollTop > 200 || document.documentElement.scrollTop > 200) {
                scrollToTopBtn.style.display = "block";
            } else {
                scrollToTopBtn.style.display = "none";
            }
        }

        scrollToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});

// --- SimpleLightbox Initialization (for gallery) ---
// Note: This often needs to be initialized outside DOMContentLoaded or using jQuery ready function
// because SimpleLightbox might assume jQuery is loaded globally earlier.
$(function(){
    var lightbox = $('.simple-lightbox a').simpleLightbox({
        overlayOpacity: 0.9,
        animationSpeed: 250,
        fadeSpeed: 300,
        captionsData: 'alt',
        captionDelay: 250,
        closeText: 'Tutup',
        navText: ['Prev', 'Next']
    });
});