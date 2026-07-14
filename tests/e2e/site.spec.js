const { test, expect } = require("@playwright/test");

const article = "/blogs/surgery-or-autopsy-adr-award-modification";

test("public routes return rendered pages", async ({ page }) => {
    for (const path of ["/", "/about/", "/blogs/", article, "/interviews/", "/contact/", "/privacy/", "/not-found"]) {
        const response = await page.goto(path);
        expect(response.status()).toBe(path === "/not-found" ? 404 : 200);
        await expect(page.locator("main")).toBeVisible();
    }
});

for (const width of [320, 360, 375, 390, 414, 768, 1024, 1440]) {
    test(`article is visible without horizontal overflow at ${width}px`, async ({ page }) => {
        await page.setViewportSize({ width, height: 900 });
        await page.goto(article);
        await expect(page.locator("article.article-container")).toBeVisible();
        expect(await page.locator("article.article-container").innerText()).toContain("The LexNush Takeaway");
        const dimensions = await page.locator("html").evaluate((html) => ({ width: html.clientWidth, scroll: html.scrollWidth }));
        expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.width);
    });
}

test("mobile menu and search dialog expose accessible state", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 900 });
    await page.goto("/");
    const menu = page.getByRole("button", { name: "Open menu" });
    await menu.click();
    const closeMenu = page.getByRole("button", { name: "Close menu" });
    await expect(closeMenu).toHaveAttribute("aria-expanded", "true");
    await expect(page.getByRole("navigation", { name: "Mobile navigation" })).toBeVisible();
    await closeMenu.click();
    await page.getByRole("button", { name: "Search LexNush" }).click();
    await expect(page.getByRole("dialog", { name: "Search" })).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.getByRole("dialog", { name: "Search" })).not.toBeVisible();
});
