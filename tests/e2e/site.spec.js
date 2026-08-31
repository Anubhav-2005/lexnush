const { test, expect } = require("@playwright/test");

const article = "/blogs/surgery-or-autopsy-adr-award-modification";
const counselArticle = "/blogs/every-file-has-a-story";
const keralaArticle = "/blogs/from-kerala-to-keralam-inside-article-3";

test("public routes return rendered pages", async ({ page }) => {
    for (const path of ["/", "/about/", "/analysis/", "/law-explained/", "/judgment-explained/", "/authors/anushka-pandey/", "/blogs/", article, counselArticle, keralaArticle, "/counsels-desk/", "/contact/", "/privacy/", "/terms/", "/disclaimer/", "/editorial-standards/", "/accessibility/", "/thank-you/", "/not-found"]) {
        const response = await page.goto(path);
        expect(response.status()).toBe(path === "/not-found" ? 404 : 200);
        await expect(page.locator("main")).toBeVisible();
    }
});

test("Counsel's Desk publishes the latest reflection and links to its article", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/counsels-desk/");

    const card = page.locator(".single-post-grid .blog-card");
    await expect(card).toContainText("Every File Has a Story");
    await expect(card).toContainText("Counsel's Desk");
    await expect(card).toContainText("27 August 2026");
    await card.getByRole("link", { name: "Read article" }).click();

    expect(page.url()).toContain(counselArticle);
    await expect(page.getByRole("heading", { name: "Every File Has a Story" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "The story arrives before the law does" })).toBeVisible();
    const dimensions = await page.locator("html").evaluate((html) => ({ width: html.clientWidth, scroll: html.scrollWidth }));
    expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.width);
});

test("legacy interviews route redirects to Counsel’s Desk", async ({ page }) => {
    const response = await page.goto("/interviews/");
    expect(response.status()).toBe(200);
    expect(page.url()).toContain("/counsels-desk/");
    await expect(page.getByRole("heading", { name: "FROM THE COUNSEL'S DESK" })).toBeVisible();
});

test("article exposes useful sharing destinations", async ({ page }) => {
    await page.goto(article);
    await expect(page.getByRole("link", { name: "WhatsApp" })).toHaveAttribute("href", /wa\.me/);
    await expect(page.getByRole("link", { name: "Email" })).toHaveAttribute("href", /mailto:/);
    const share = page.locator(".article-share");
    await expect(share.getByRole("link", { name: "LinkedIn" })).toHaveAttribute("href", /linkedin\.com\/sharing/);
    await expect(share.getByRole("button", { name: "Copy link" })).toBeVisible();
});

test("article offers orientation, citation, print and related reading", async ({ page }) => {
    await page.goto(article);
    const toc = page.locator(".article-toc");
    await expect(toc).toBeVisible();
    const firstLink = toc.getByRole("link").first();
    const target = await firstLink.getAttribute("href");
    expect(target).toMatch(/^#[a-z0-9-]+$/);
    await firstLink.click();
    await expect(page.locator(target)).toBeVisible();
    await expect(page.getByRole("button", { name: /Print/ })).toBeVisible();
    await expect(page.getByText("More from LexNush")).toBeVisible();
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
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/");
    const menu = page.getByRole("button", { name: "Open menu" });
    await menu.click();
    const closeMenu = page.getByRole("button", { name: "Close menu" });
    await expect(closeMenu).toHaveAttribute("aria-expanded", "true");
    await expect(page.getByRole("navigation", { name: "Mobile navigation" })).toBeVisible();
    await expect(page.locator(".mobile-menu-subscribe")).toBeVisible();
    await expect(page.locator("main")).toHaveAttribute("inert", "");
    await closeMenu.click();
    await page.getByRole("button", { name: "Search LexNush" }).click();
    await expect(page.getByRole("dialog", { name: "Search" })).toBeVisible();
    await expect(page.locator(".site-shell")).toHaveAttribute("inert", "");
    await page.keyboard.press("Escape");
    await expect(page.getByRole("dialog", { name: "Search" })).not.toBeVisible();
});

test("mobile subscription and cookie choices stay out of the reading surface", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/");
    await expect(page.locator(".mobile-subscribe-cta")).toHaveCount(0);
    const consent = page.locator("#cookie-consent");
    await expect(consent).toBeVisible();
    await consent.getByRole("button", { name: "Essential only" }).click();
    await expect(consent).not.toBeVisible();
    await expect(consent).toHaveAttribute("inert", "");
    const dimensions = await page.locator("html").evaluate((html) => ({ width: html.clientWidth, scroll: html.scrollWidth }));
    expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.width);
});

test("mobile navigation remains reachable in landscape", async ({ page }) => {
    await page.setViewportSize({ width: 568, height: 320 });
    await page.goto("/");
    await page.getByRole("button", { name: "Open menu" }).click();

    const menu = page.locator("#mobile-menu");
    const geometry = await menu.evaluate((element) => ({
        clientHeight: element.clientHeight,
        scrollHeight: element.scrollHeight,
        overflowY: getComputedStyle(element).overflowY,
    }));
    expect(["auto", "scroll"]).toContain(geometry.overflowY);

    const finalAction = page.locator(".mobile-menu-subscribe");
    await finalAction.scrollIntoViewIfNeeded();
    const box = await finalAction.boundingBox();
    expect(box.y).toBeGreaterThanOrEqual(0);
    expect(box.y + box.height).toBeLessThanOrEqual(320);
});

test("primary mobile controls meet touch target sizing", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/");

    for (const selector of ["#search-trigger", "#theme-toggle", ".mobile-toggle"]) {
        const box = await page.locator(selector).boundingBox();
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
    }

    await page.getByRole("button", { name: "Search LexNush" }).click();
    const closeBox = await page.locator("#close-search").boundingBox();
    expect(closeBox.width).toBeGreaterThanOrEqual(44);
    expect(closeBox.height).toBeGreaterThanOrEqual(44);
    await page.keyboard.press("Escape");

    await page.evaluate(() => window.scrollTo(0, 600));
    const backToTop = page.locator("#back-to-top");
    await expect(backToTop).toBeVisible();
    const backBox = await backToTop.boundingBox();
    expect(backBox.width).toBeGreaterThanOrEqual(44);
    expect(backBox.height).toBeGreaterThanOrEqual(44);
});

for (const width of [320, 390, 559, 561, 768, 899, 901]) {
    test(`home cards retain deliberate proportions at ${width}px`, async ({ page }) => {
        await page.emulateMedia({ reducedMotion: "reduce" });
        await page.setViewportSize({ width, height: width < 600 ? 844 : 1024 });
        await page.goto("/");

        const cards = page.locator("#latest .latest-card");
        await expect(cards.first()).toBeVisible();
        const boxes = await cards.evaluateAll((elements) => elements.map((element) => {
            const rect = element.getBoundingClientRect();
            return { left: rect.left, right: rect.right, width: rect.width, height: rect.height };
        }));
        for (const box of boxes) {
            expect(box.left).toBeGreaterThanOrEqual(0);
            expect(box.right).toBeLessThanOrEqual(width + 0.5);
            expect(box.width).toBeGreaterThan(0);
        }
        if (width <= 640) expect(Math.max(...boxes.map((box) => box.height))).toBeLessThan(330);
    });
}
