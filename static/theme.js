(() => {
    try {
        document.documentElement.setAttribute("data-theme", localStorage.getItem("theme") || "dark");
    } catch {
        document.documentElement.setAttribute("data-theme", "dark");
    }
})();
