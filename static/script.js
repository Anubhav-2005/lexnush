(() => {
    document.documentElement.classList.add("has-js");
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const qs = (selector, scope = document) => scope.querySelector(selector);
    const qsa = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

    function setPageLocked(isLocked) {
        document.body.classList.toggle("no-scroll", isLocked);
    }

    function syncBackgroundInert() {
        const searchOpen = Boolean(qs(".search-overlay.is-active"));
        const mobileOpen = Boolean(qs(".mobile-menu.is-active"));
        const shell = qs(".site-shell");
        const main = qs(".site-main");
        const footer = qs(".site-footer");
        const consent = qs("#cookie-consent");

        if (shell) shell.inert = searchOpen;
        if (main) main.inert = !searchOpen && mobileOpen;
        if (footer) footer.inert = !searchOpen && mobileOpen;
        if (consent) consent.inert = searchOpen || mobileOpen || !consent.classList.contains("is-visible");
    }

    function syncPageLock() {
        setPageLocked(Boolean(qs(".mobile-menu.is-active, .search-overlay.is-active")));
        syncBackgroundInert();
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
        qsa("a", menu).forEach((link) => link.addEventListener("click", () => setOpen(false)));
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && menu.classList.contains("is-active")) setOpen(false);
            if (menu.classList.contains("is-active")) trapFocus(event, menu);
        });

        const mobileNavigation = window.matchMedia("(max-width: 1100px)");
        const closeAtDesktop = (event) => {
            if (!event.matches && menu.classList.contains("is-active")) setOpen(false);
        };
        mobileNavigation.addEventListener?.("change", closeAtDesktop);
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

        const sync = () => {
            const isVisible = window.scrollY > 360;
            button.classList.toggle("is-visible", isVisible);
            button.setAttribute("aria-hidden", String(!isVisible));
            button.inert = !isVisible;
            button.tabIndex = isVisible ? 0 : -1;
        };
        sync();
        window.addEventListener("scroll", sync, { passive: true });
        button.addEventListener("click", () => window.scrollTo({ top: 0, behavior: prefersReducedMotion ? "auto" : "smooth" }));
    }

    function initCookieConsent() {
        const panel = qs("#cookie-consent");
        if (!panel) return;

        const storageKey = "lexnush_cookie_consent";
        const analyticsId = (document.body.dataset.googleAnalyticsId || "").trim();
        const readConsent = () => {
            const match = document.cookie.match(new RegExp(`(?:^|; )${storageKey}=([^;]*)`));
            return match ? decodeURIComponent(match[1]) : "";
        };
        const writeConsent = (choice) => {
            const secure = window.location.protocol === "https:" ? "; Secure" : "";
            document.cookie = `${storageKey}=${encodeURIComponent(choice)}; Max-Age=31536000; Path=/; SameSite=Lax${secure}`;
        };
        const setOpen = (isOpen) => {
            panel.classList.toggle("is-visible", isOpen);
            panel.setAttribute("aria-hidden", String(!isOpen));
            panel.inert = !isOpen || Boolean(qs(".mobile-menu.is-active, .search-overlay.is-active"));
        };
        const clearAnalyticsCookies = () => {
            const cookieNames = document.cookie.split(";")
                .map((cookie) => cookie.split("=", 1)[0].trim())
                .filter((name) => name === "_ga" || name.startsWith("_ga_"));
            const hostParts = window.location.hostname.split(".");
            const domains = ["", window.location.hostname];
            if (hostParts.length > 1) domains.push(`.${hostParts.slice(-2).join(".")}`);
            cookieNames.forEach((name) => {
                domains.forEach((domain) => {
                    const domainPart = domain ? `; Domain=${domain}` : "";
                    document.cookie = `${name}=; Max-Age=0; Path=/${domainPart}; SameSite=Lax`;
                });
            });
        };
        const loadAnalytics = () => {
            if (!analyticsId || window.__lexnushAnalyticsLoaded) return;
            window.__lexnushAnalyticsLoaded = true;
            window.dataLayer = window.dataLayer || [];
            window.gtag = window.gtag || function gtag() { window.dataLayer.push(arguments); };
            window.gtag("consent", "default", { analytics_storage: "granted" });
            window.gtag("js", new Date());
            window.gtag("config", analyticsId, { anonymize_ip: true, allow_google_signals: false });
            const script = document.createElement("script");
            script.async = true;
            script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(analyticsId)}`;
            document.head.append(script);
        };
        const choose = (choice) => {
            writeConsent(choice);
            if (choice === "analytics") {
                loadAnalytics();
            } else {
                if (window.gtag) window.gtag("consent", "update", { analytics_storage: "denied" });
                clearAnalyticsCookies();
            }
            setOpen(false);
            if (choice === "essential" && window.__lexnushAnalyticsLoaded) window.location.reload();
        };

        let savedChoice = readConsent();
        if (savedChoice === "all") {
            savedChoice = "analytics";
            writeConsent(savedChoice);
        }
        if (savedChoice === "analytics") loadAnalytics();
        if (!savedChoice) setOpen(true);

        qsa("[data-cookie-consent]").forEach((button) => {
            button.addEventListener("click", () => choose(button.dataset.cookieConsent));
        });
        qsa("[data-cookie-preferences]").forEach((button) => {
            button.addEventListener("click", () => setOpen(true));
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

    function initReaderTools() {
        qsa("[data-copy-citation]").forEach((button) => {
            button.addEventListener("click", async () => {
                const feedback = qs(".reader-tools-feedback", button.closest(".article-reader-tools") || document);
                try {
                    await navigator.clipboard.writeText(button.dataset.copyCitation || "");
                    if (feedback) feedback.textContent = "Citation copied.";
                } catch {
                    if (feedback) feedback.textContent = "Copy failed. Select the browser address to cite this page.";
                }
            });
        });
        qsa("[data-print-article]").forEach((button) => button.addEventListener("click", () => window.print()));
    }

    function initArticleToc() {
        const toc = qs(".article-toc");
        if (!toc) return;
        const links = qsa('a[href^="#"]', toc);
        const headings = links.map((link) => qs(link.getAttribute("href"))).filter(Boolean);
        if (!headings.length || !("IntersectionObserver" in window)) return;

        const byId = new Map(links.map((link) => [link.getAttribute("href").slice(1), link]));
        const observer = new IntersectionObserver((entries) => {
            const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
            if (!visible.length) return;
            links.forEach((link) => link.removeAttribute("aria-current"));
            byId.get(visible[0].target.id)?.setAttribute("aria-current", "location");
        }, { rootMargin: "-18% 0px -68% 0px", threshold: 0 });
        headings.forEach((heading) => observer.observe(heading));
    }

    function initNativeShare() {
        qsa("[data-native-share]").forEach((button) => {
            if (!("share" in navigator)) {
                button.hidden = true;
                return;
            }

            button.addEventListener("click", async () => {
                try {
                    await navigator.share({
                        title: button.dataset.shareTitle || document.title,
                        text: button.dataset.shareText || "",
                        url: window.location.href,
                    });
                } catch (error) {
                    // Closing the native share sheet is an expected user action.
                    if (error && error.name !== "AbortError") {
                        const feedback = qs(".copy-feedback", button.closest(".article-share") || document);
                        if (feedback) feedback.textContent = "Sharing is unavailable on this device.";
                    }
                }
            });
        });
    }

    function initReadingProgress() {
        const bar = qs("#reading-progress-bar");
        if (!bar) return;
        const articleBody = qs(".article-body");

        let scheduled = false;
        const sync = () => {
            scheduled = false;
            let progress = 0;
            if (articleBody) {
                const rect = articleBody.getBoundingClientRect();
                const start = rect.top + window.scrollY;
                const length = Math.max(1, rect.height);
                const readingPosition = window.scrollY + window.innerHeight * 0.34;
                progress = Math.min(1, Math.max(0, (readingPosition - start) / length));
            } else {
                const maximum = document.documentElement.scrollHeight - window.innerHeight;
                progress = maximum > 0 ? Math.min(1, Math.max(0, window.scrollY / maximum)) : 0;
            }
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

    function initFormSubmissionStates() {
        qsa("form[data-submit-state]").forEach((form) => {
            form.addEventListener("submit", () => {
                if (!form.checkValidity()) return;
                const button = qs('button[type="submit"]', form);
                if (!button || button.disabled) return;
                button.disabled = true;
                button.classList.add("is-loading");
                button.setAttribute("aria-busy", "true");
                button.textContent = form.dataset.submitLabel || "Sending…";
            });
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
        initCookieConsent();
        initFadeIns();
        initCopyLinks();
        initReaderTools();
        initArticleToc();
        initNativeShare();
        initReadingProgress();
        initCharacterCounters();
        initFormSubmissionStates();
        initSearch();
    });
})();
