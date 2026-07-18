(() => {
    document.documentElement.classList.add("has-js");
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const qs = (selector, scope = document) => scope.querySelector(selector);
    const qsa = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

    function setPageLocked(isLocked) {
        document.body.classList.toggle("no-scroll", isLocked);
    }

    function syncPageLock() {
        setPageLocked(Boolean(qs(".mobile-menu.is-active, .search-overlay.is-active")));
    }

    function trapFocus(event, container) {
        if (event.key !== "Tab") return;
        const focusable = qsa('a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])', container)
            .filter((element) => !element.closest("[inert]"));
        if (!focusable.length) return;

        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }

    function initPreloader() {
        const preloader = qs("#preloader");
        if (!preloader) return;

        window.setTimeout(() => {
            preloader.classList.add("is-hidden");
            window.setTimeout(() => preloader.remove(), 450);
        }, prefersReducedMotion ? 0 : 180);
    }

    function initNavbar() {
        const navbar = qs("[data-navbar]");
        if (!navbar) return;

        const sync = () => navbar.classList.toggle("is-scrolled", window.scrollY > 24);
        sync();
        window.addEventListener("scroll", sync, { passive: true });
    }

    function initMobileMenu() {
        const toggle = qs(".mobile-toggle");
        const menu = qs("#mobile-menu");
        if (!toggle || !menu) return;
        let lastFocused;

        const setOpen = (isOpen) => {
            if (isOpen) lastFocused = document.activeElement;
            toggle.classList.toggle("is-active", isOpen);
            toggle.setAttribute("aria-expanded", String(isOpen));
            toggle.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
            menu.classList.toggle("is-active", isOpen);
            menu.setAttribute("aria-hidden", String(!isOpen));
            menu.inert = !isOpen;
            syncPageLock();
            if (isOpen) {
                window.requestAnimationFrame(() => qs("a", menu)?.focus({ preventScroll: true }));
            } else if (lastFocused instanceof HTMLElement) {
                lastFocused.focus();
            }
        };

        toggle.addEventListener("click", () => setOpen(!menu.classList.contains("is-active")));
        qsa(".mobile-links a", menu).forEach((link) => link.addEventListener("click", () => setOpen(false)));
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && menu.classList.contains("is-active")) setOpen(false);
            if (menu.classList.contains("is-active")) trapFocus(event, menu);
        });
    }

    function initTheme() {
        const toggle = qs("#theme-toggle");
        if (!toggle) return;

        const syncLabel = () => {
            const isDark = document.documentElement.getAttribute("data-theme") === "dark";
            toggle.setAttribute("aria-label", isDark ? "Switch to light theme" : "Switch to dark theme");
        };

        syncLabel();

        toggle.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme");
            const nextTheme = currentTheme === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", nextTheme);
            try {
                localStorage.setItem("theme", nextTheme);
            } catch {
                // Browsers may deny localStorage in strict privacy modes.
            }
            syncLabel();
        });
    }

    function initBackToTop() {
        const button = qs("#back-to-top");
        if (!button) return;

        const sync = () => button.classList.toggle("is-visible", window.scrollY > 360);
        sync();
        window.addEventListener("scroll", sync, { passive: true });
        button.addEventListener("click", () => window.scrollTo({ top: 0, behavior: prefersReducedMotion ? "auto" : "smooth" }));
    }

    function initDisclaimer() {
        const panel = qs("#legal-notice");
        const dismissButton = qs("#dismiss-legal-notice");
        const storageKey = "lexnush_legal_notice_dismissed";
        if (!panel || !dismissButton) return;

        const hasDismissed = () => {
            try {
                return sessionStorage.getItem(storageKey) === "true";
            } catch {
                return false;
            }
        };

        const rememberDismissed = () => {
            try {
                sessionStorage.setItem(storageKey, "true");
            } catch {
                // Browsers may deny sessionStorage in strict privacy modes.
            }
        };

        const setOpen = (isOpen) => {
            panel.classList.toggle("is-visible", isOpen);
            panel.setAttribute("aria-hidden", String(!isOpen));
        };

        if (!hasDismissed()) {
            window.setTimeout(() => setOpen(true), prefersReducedMotion ? 0 : 1800);
        }

        dismissButton.addEventListener("click", () => {
            rememberDismissed();
            setOpen(false);
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && panel.classList.contains("is-visible")) setOpen(false);
        });
    }

    function initFadeIns() {
        const elements = qsa(".fade-in");
        if (!elements.length) return;

        if (prefersReducedMotion || !("IntersectionObserver" in window)) {
            elements.forEach((element) => element.classList.add("is-visible"));
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.12 }
        );

        elements.forEach((element) => observer.observe(element));
    }

    function initCopyLinks() {
        qsa("[data-copy-link]").forEach((button) => {
            button.addEventListener("click", async () => {
                const feedback = qs(".copy-feedback", button.closest(".article-share") || document);
                try {
                    await navigator.clipboard.writeText(window.location.href);
                    if (feedback) feedback.textContent = "Link copied.";
                } catch {
                    if (feedback) feedback.textContent = "Copy failed. Please copy the browser address.";
                }
            });
        });
    }

    function initReadingProgress() {
        const bar = qs("#reading-progress-bar");
        if (!bar) return;

        let scheduled = false;
        const sync = () => {
            scheduled = false;
            const maximum = document.documentElement.scrollHeight - window.innerHeight;
            const progress = maximum > 0 ? Math.min(1, Math.max(0, window.scrollY / maximum)) : 0;
            bar.style.transform = `scaleX(${progress})`;
        };
        const schedule = () => {
            if (!scheduled) {
                scheduled = true;
                window.requestAnimationFrame(sync);
            }
        };

        sync();
        window.addEventListener("scroll", schedule, { passive: true });
        window.addEventListener("resize", schedule, { passive: true });
    }

    function initCharacterCounters() {
        qsa("[data-character-counter]").forEach((field) => {
            const counter = qs(`#${field.dataset.characterCounter}`);
            if (!counter || !field.maxLength) return;
            const sync = () => {
                counter.textContent = `${field.value.length} / ${field.maxLength}`;
            };
            sync();
            field.addEventListener("input", sync);
        });
    }

    function createSearchState(className, text) {
        const element = document.createElement("div");
        element.className = className;
        element.textContent = text;
        return element;
    }

    function highlightedText(text, query) {
        const fragment = document.createDocumentFragment();
        const lowerText = text.toLowerCase();
        const lowerQuery = query.toLowerCase();
        const start = lowerText.indexOf(lowerQuery);

        if (start === -1 || !query) {
            fragment.append(document.createTextNode(text));
            return fragment;
        }

        fragment.append(document.createTextNode(text.slice(0, start)));
        const mark = document.createElement("mark");
        mark.textContent = text.slice(start, start + query.length);
        fragment.append(mark, document.createTextNode(text.slice(start + query.length)));
        return fragment;
    }

    function initSearch() {
        const trigger = qs("#search-trigger");
        const overlay = qs("#search-overlay");
        const input = qs("#search-input");
        const closeButton = qs("#close-search");
        const results = qs("#search-results");
        if (!trigger || !overlay || !input || !closeButton || !results) return;

        let debounceTimer;
        let abortController;
        let lastFocused;

        const setOpen = (isOpen) => {
            if (isOpen) lastFocused = document.activeElement;
            overlay.classList.toggle("is-active", isOpen);
            overlay.setAttribute("aria-hidden", String(!isOpen));
            overlay.inert = !isOpen;
            syncPageLock();
            if (isOpen) {
                window.setTimeout(() => input.focus(), 80);
            } else {
                input.value = "";
                results.replaceChildren();
                if (abortController) abortController.abort();
                if (lastFocused instanceof HTMLElement) lastFocused.focus();
            }
        };

        const renderResults = (items, query) => {
            results.replaceChildren();
            if (!items.length) {
                results.append(createSearchState("search-empty", "No results found."));
                return;
            }

            items.forEach((item) => {
                const link = document.createElement("a");
                const type = document.createElement("span");
                const title = document.createElement("strong");
                const summary = document.createElement("p");

                link.className = "search-item";
                link.href = item.url;
                type.textContent = item.type;
                title.append(highlightedText(item.title, query));
                summary.textContent = item.summary || "";
                link.append(type, title, summary);
                results.append(link);
            });
        };

        trigger.addEventListener("click", () => setOpen(true));
        closeButton.addEventListener("click", () => setOpen(false));
        overlay.addEventListener("click", (event) => {
            if (event.target === overlay) setOpen(false);
        });

        document.addEventListener("keydown", (event) => {
            if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
                event.preventDefault();
                setOpen(true);
            }
            if (event.key === "Escape" && overlay.classList.contains("is-active")) setOpen(false);
            if (overlay.classList.contains("is-active")) trapFocus(event, overlay);
        });

        input.addEventListener("input", () => {
            window.clearTimeout(debounceTimer);
            const query = input.value.trim();

            if (abortController) abortController.abort();
            if (!query) {
                results.replaceChildren();
                return;
            }

            results.replaceChildren(createSearchState("search-loading", "Searching..."));
            debounceTimer = window.setTimeout(async () => {
                abortController = new AbortController();
                try {
                    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, { signal: abortController.signal });
                    if (!response.ok) throw new Error(`Search failed with ${response.status}`);
                    renderResults(await response.json(), query);
                } catch (error) {
                    if (error.name !== "AbortError") {
                        results.replaceChildren(createSearchState("search-empty", "Search is temporarily unavailable."));
                    }
                }
            }, 220);
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        initPreloader();
        initNavbar();
        initMobileMenu();
        initTheme();
        initBackToTop();
        initDisclaimer();
        initFadeIns();
        initCopyLinks();
        initReadingProgress();
        initCharacterCounters();
        initSearch();
    });
})();
