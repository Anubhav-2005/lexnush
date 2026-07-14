const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
    testDir: "./tests/e2e",
    timeout: 30_000,
    use: {
        baseURL: "http://127.0.0.1:8001",
        browserName: "chromium",
        headless: true,
    },
    webServer: {
        command: "PORT=8001 python3 app.py",
        url: "http://127.0.0.1:8001/healthz",
        reuseExistingServer: !process.env.CI,
        timeout: 30_000,
    },
});
