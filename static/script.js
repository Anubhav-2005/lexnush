document.addEventListener("DOMContentLoaded", () => {
    
    // ================= 1. UI VARIABLES =================
    const navbar = document.querySelector('.navbar');
    const mobileToggle = document.querySelector('.mobile-toggle');
    const mobileOverlay = document.querySelector('.mobile-menu-overlay');
    const backToTopBtn = document.getElementById('back-to-top');

    // Search Variables
    const searchTrigger = document.getElementById('search-trigger');
    const searchOverlay = document.getElementById('search-overlay');
    const searchInput = document.getElementById('search-input');
    const closeSearch = document.getElementById('close-search');
    const resultsContainer = document.getElementById('search-results');

    // ================= 2. PRELOADER & FADE IN =================
    const preloader = document.getElementById('preloader');
    const loadingBar = document.querySelector('.loading-bar');
    
    setTimeout(() => { 
        if(loadingBar) loadingBar.style.width = "100%"; 
    }, 50);

    setTimeout(() => { 
        if(preloader) {
            preloader.style.opacity = "0"; 
            setTimeout(() => preloader.remove(), 500);
        }
    }, 800);

    // ================= 3. NAVBAR SCROLL EFFECT =================
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    });

    // ================= 4. MOBILE MENU LOGIC =================
    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            const isActive = mobileOverlay.classList.toggle('active');
            mobileToggle.classList.toggle('active'); // Animate the hamburger
            document.body.style.overflow = isActive ? 'hidden' : '';
        });
        
        // Close menu when clicking any link
        document.querySelectorAll('.mobile-links a').forEach(link => {
            link.addEventListener('click', () => {
                mobileOverlay.classList.remove('active');
                mobileToggle.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }

    // ================= 5. THEME SWITCHER =================
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const iconSun = document.querySelector('.icon.sun');
    const iconMoon = document.querySelector('.icon.moon');

    function updateThemeIcons(theme) {
        if (!iconSun || !iconMoon) return;
        const isLight = theme === 'light';
        
        iconSun.style.opacity = isLight ? '1' : '0';
        iconSun.style.transform = isLight ? 'translate(-50%, -50%) rotate(0deg)' : 'translate(-50%, -50%) rotate(-90deg)';
        
        iconMoon.style.opacity = isLight ? '0' : '1';
        iconMoon.style.transform = isLight ? 'translate(-50%, -50%) rotate(90deg)' : 'translate(-50%, -50%) rotate(0deg)';
    }

    // Initialize Theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    htmlElement.setAttribute('data-theme', savedTheme);
    updateThemeIcons(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcons(newTheme);
        });
    }

    // ================= 6. BACK TO TOP BUTTON =================
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            backToTopBtn.classList.toggle('visible', window.scrollY > 300);
        });
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // ================= 7. DISCLAIMER MODAL =================
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

    // ================= 8. FADE ANIMATIONS =================
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
    
    // ================= 9. 3D TILT INIT =================
    if (typeof VanillaTilt !== 'undefined') {
        VanillaTilt.init(document.querySelectorAll("[data-tilt]"), {
            max: 5, speed: 400, glare: true, "max-glare": 0.2,
        });
    }

    // ================= 10. SPOTLIGHT SEARCH (THE FIX) =================
    function toggleSearch(show) {
        if (!searchOverlay) return; // Safety Check
        
        if (show) {
            searchOverlay.classList.add('active');
            setTimeout(() => { if(searchInput) searchInput.focus(); }, 100);
            document.body.style.overflow = 'hidden';
        } else {
            searchOverlay.classList.remove('active');
            document.body.style.overflow = '';
            if(searchInput) searchInput.value = ''; 
            if(resultsContainer) resultsContainer.innerHTML = ''; 
        }
    }

    // Event Listeners for Search
    if(searchTrigger) {
        searchTrigger.addEventListener('click', (e) => {
            e.preventDefault(); // Stop any default button behavior
            toggleSearch(true);
        });
    }

    if(closeSearch) {
        closeSearch.addEventListener('click', () => toggleSearch(false));
    }

    if(searchOverlay) {
        searchOverlay.addEventListener('click', (e) => {
            if (e.target === searchOverlay) toggleSearch(false);
        });
    }

    // Keyboard Shortcuts (Cmd+K or Esc)
    document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            toggleSearch(true);
        }
        if (e.key === 'Escape' && searchOverlay && searchOverlay.classList.contains('active')) {
            toggleSearch(false);
        }
    });

    // Live Search Logic (Debounced)
    let debounceTimer;
    if(searchInput) {
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();

            if (query.length === 0) {
                if(resultsContainer) resultsContainer.innerHTML = '';
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`/api/search?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (!resultsContainer) return;
                        resultsContainer.innerHTML = '';
                        
                        if (data.length === 0) {
                            resultsContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-muted);">No results found.</div>';
                        } else {
                            data.forEach(item => {
                                const el = document.createElement('a');
                                el.className = 'search-item';
                                el.href = item.url;
                                el.innerHTML = `<span>${item.type}</span><strong>${item.title}</strong>`;
                                resultsContainer.appendChild(el);
                            });
                        }
                    })
                    .catch(err => console.error("Search API Error:", err));
            }, 300);
        });
    }
});