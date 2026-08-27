import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  outputDir: "./test-results",
  timeout: 150_000,
  fullyParallel: false,
  workers: 1,
  reporter: "line",
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://127.0.0.1:8765",
    colorScheme: "light",
    locale: "tr-TR",
    trace: "retain-on-failure",
  },
});
