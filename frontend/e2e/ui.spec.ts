import { expect, test, type Page } from "@playwright/test";

function captureSeriousErrors(page: Page) {
  const errors: string[] = [];
  page.on("console", (message: { type: () => string; text: () => string }) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error: Error) => errors.push(error.message));
  return errors;
}

test("masaüstünde gerçek belgeler, chat, kaynak ve bilinmeyen cevap çalışır", async ({ page }) => {
  const errors = captureSeriousErrors(page);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");

  await expect(page.getByText("Yerel Bilgi Asistanı", { exact: true })).toBeVisible();
  const desktopSidebar = page.locator("aside").first();
  await expect(desktopSidebar.getByText("Databases", { exact: true })).toBeVisible();
  await expect(desktopSidebar.getByText(/\d+ belge • \d+ parça/)).toBeVisible();
  await expect(page.getByText("Belgelerinizdeki bilgiye, anında ulaşın.")).toBeVisible();
  await expect(page.getByLabel(/Yerel AI|Foundry Local/)).toBeVisible();

  await desktopSidebar.getByRole("button", { name: "Databases belgesini aç" }).click();
  await expect(page.getByRole("heading", { name: "Databases" })).toBeVisible();
  await expect(page.getByText(/Relational Databases/)).toBeVisible();
  await page.getByRole("button", { name: "Belge önizlemesini kapat" }).click();

  await page.getByRole("button", { name: "TCP ile UDP arasındaki fark nedir?" }).click();
  await expect(page.getByText("Belgelerde aranıyor…")).toBeVisible();
  await expect(page.getByText(/TCP, bir bağlantı/)).toBeVisible({ timeout: 120_000 });
  await page.getByText(/kaynak parçası$/i).click();
  await expect(page.getByText("networking.md", { exact: true }).first()).toBeVisible();

  const composer = page.getByRole("textbox", { name: "Soru", exact: true });
  await composer.fill("Tiramisu yapmak için hangi malzemeler gerekir?");
  await composer.press("Enter");
  await expect(page.getByText("Bu bilgi sağlanan belgelerde bulunmuyor.")).toBeVisible({
    timeout: 30_000,
  });
  await expect(page.getByText("Belgelerde bulunamadı")).toBeVisible();

  await page.screenshot({ path: "test-results/desktop.png", fullPage: true });
  expect(errors).toEqual([]);
});

test("mobil yerleşim drawer ve dokunma hedefleriyle taşmadan çalışır", async ({ page }) => {
  const errors = captureSeriousErrors(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await expect(page.getByText("Belgelerinizdeki bilgiye, anında ulaşın.")).toBeVisible();
  await page.getByRole("button", { name: "Bilgi Kütüphanesi panelini aç" }).click();
  const mobileSidebar = page.getByLabel("Bilgi Kütüphanesi", { exact: true });
  await expect(mobileSidebar.getByRole("button", { name: "Doküman Ekle" })).toBeVisible();
  await expect(mobileSidebar.getByText(/\d+ belge • \d+ parça/)).toBeVisible();
  await page.waitForTimeout(250);

  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  await page.screenshot({ path: "test-results/mobile.png", fullPage: true });
  expect(errors).toEqual([]);
});

test("açık tema masaüstü karşılama ekranı sunum düzeninde görünür", async ({ page }) => {
  const errors = captureSeriousErrors(page);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");

  await expect(page.getByText("Belgelerinizdeki bilgiye, anında ulaşın.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Doküman Ekle" }).first()).toBeVisible();
  await expect(page.locator("body")).toHaveCSS("background-color", "rgb(248, 250, 249)");
  await page.waitForTimeout(300);
  await page.screenshot({ path: "test-results/design-desktop.png", fullPage: true });
  expect(errors).toEqual([]);
});
