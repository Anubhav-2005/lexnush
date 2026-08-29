(() => {
    try {
        document.documentElement.setAttribute("data-theme", localStorage.getItem("theme") || "dark");
    } catch {
        document.documentElement.setAttribute("data-theme", "dark");
    }

    document.addEventListener("DOMContentLoaded", () => {
        const adminThemeToggle = document.querySelector(".admin-theme-toggle");
        if (!adminThemeToggle) return;

        adminThemeToggle.addEventListener("click", () => {
            const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
            document.documentElement.dataset.theme = nextTheme;
            try {
                localStorage.setItem("theme", nextTheme);
            } catch {
                // Browsers may deny localStorage in strict privacy modes.
            }
        });
    });
})();
