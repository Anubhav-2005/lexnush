document.addEventListener("DOMContentLoaded", () => {
    
    // ================= 1. PRELOADER & FADE IN =================
    const preloader = document.getElementById('preloader');
    const loadingBar = document.querySelector('.loading-bar');
    
    setTimeout(() => { if(loadingBar) loadingBar.style.width = "100%"; }, 50);
    setTimeout(() => { 
        if(preloader) preloader.style.opacity = "0"; 
        // Remove from DOM after fade out
        setTimeout(() => { if(preloader) preloader.remove(); }, 500);
    }, 800);

    // ================= 2. NAVBAR SCROLL EFFECT =================
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // ================= 3. THEME TOGGLE LOGIC =================
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const iconSun = document.querySelector('.icon.sun');
    const iconMoon = document.querySelector('.icon.moon');

    function updateIcons(theme) {
        if (!iconSun || !iconMoon) return;
        if (theme === 'light') {
            // Light Mode: Show Sun, Hide Moon
            iconSun.style.opacity = '1';
            iconSun.style.transform = 'translate(-50%, -50%) rotate(0deg)';
            iconMoon.style.opacity = '0';
            iconMoon.style.transform = 'translate(-50%, -50%) rotate(90deg)';
        } else {
            // Dark Mode: Show Moon, Hide Sun
            iconSun.style.opacity = '0';
            iconSun.style.transform = 'translate(-50%, -50%) rotate(-90deg)';
            iconMoon.style.opacity = '1';
            iconMoon.style.transform = 'translate(-50%, -50%) rotate(0deg)';
        }
    }

    // Set Initial State
    const savedTheme = localStorage.getItem('theme') || 'dark';
    htmlElement.setAttribute('data-theme', savedTheme);
    updateIcons(savedTheme);

    // Toggle Click Event
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isDark = htmlElement.getAttribute('data-theme') === 'dark';
            const newTheme = isDark ? 'light' : 'dark';
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateIcons(newTheme);
        });
    }

    // ================= 4. MOBILE MENU =================
    const mobileToggle = document.querySelector('.mobile-toggle');
    const mobileOverlay = document.querySelector('.mobile-menu-overlay');
    
    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            mobileOverlay.classList.toggle('active');
            document.body.style.overflow = mobileOverlay.classList.contains('active') ? 'hidden' : '';
        });
        
        // Close when clicking a link
        document.querySelectorAll('.mobile-links a').forEach(link => {
            link.addEventListener('click', () => {
                mobileOverlay.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }

    // ================= 5. BACK TO TOP BUTTON =================
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // ================= 6. DISCLAIMER MODAL =================
    const modal = document.getElementById('disclaimer-modal');
    const acceptBtn = document.getElementById('accept-btn');
    const hasAccepted = sessionStorage.getItem('lexnush_disclaimer_accepted');

    if (!hasAccepted && modal) {
        setTimeout(() => {
            modal.classList.add('visible');
            document.body.style.overflow = 'hidden';
        }, 1500);
    }

    if (acceptBtn) {
        acceptBtn.addEventListener('click', () => {
            if(modal) modal.classList.remove('visible');
            document.body.style.overflow = '';
            sessionStorage.setItem('lexnush_disclaimer_accepted', 'true');
        });
    }

    // ================= 7. SCROLL FADE ANIMATIONS =================
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
    
    // ================= 8. 3D TILT INIT =================
    if (typeof VanillaTilt !== 'undefined') {
        VanillaTilt.init(document.querySelectorAll("[data-tilt]"), {
            max: 5, speed: 400, glare: true, "max-glare": 0.2,
        });
    }
});