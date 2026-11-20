import { test, expect, type Page } from "@playwright/test";

async function evaluate(page: Page, yes: boolean) {
  for (const choice of await page.locator(`input[type="radio"][value="${yes}"] + span`).all()) await choice.click();
  await page.getByRole("button", { name: "Ver orientación comercial" }).click();
  await expect(page.locator("#save-status")).toHaveText("Evaluación guardada en el historial de este navegador.");
}

test("history survives reload and page reopening; offline CRUD preserves answers and results", async ({ page, context }) => {
  await page.goto("/");
  await expect(page.locator("#history-status")).toContainText("Todavía no hay");
  await expect(page.locator("#offline-status")).toContainText("Lista para usar");
  await evaluate(page, true);
  await expect(page.locator("#history-list > li")).toHaveCount(1);
  await page.reload();
  await expect(page.locator("#history-list > li")).toHaveCount(1);
  const reopened = await context.newPage();
  await page.close();
  await reopened.goto("/");
  await expect(reopened.locator("#history-list > li")).toHaveCount(1);
  await context.setOffline(true);
  await reopened.reload();
  await expect(reopened.locator("#history-list > li")).toHaveCount(1);
  await evaluate(reopened, false);
  await expect(reopened.locator("#history-list > li")).toHaveCount(2);
  const cards = reopened.locator("#history-list > li");
  await expect(cards.first().locator("summary")).toContainText("9.8");
  await expect(cards.last().locator("summary")).toContainText("81.4");
  await cards.first().locator("summary").click();
  await expect(cards.first().locator("dd")).toHaveText(Array(7).fill("No"));
  const stored = await reopened.evaluate(async () => {
    return new Promise<any[]>((resolve, reject) => {
      const open = indexedDB.open("tenate-history", 1);
      open.onerror = () => reject(open.error);
      open.onsuccess = () => {
        const db = open.result;
        const tx = db.transaction("assessments");
        const request = tx.objectStore("assessments").getAll();
        tx.oncomplete = () => { db.close(); resolve(request.result); };
      };
    });
  });
  expect(stored).toHaveLength(2);
  expect(stored.every(r => Object.keys(r.evidence).length === 7 && /^[a-f0-9]{64}$/.test(r.model.sha256))).toBe(true);
  const probabilities = stored.map(r => r.result.probability).sort((a, b) => a - b);
  expect(probabilities[0]).toBeCloseTo(5 / 51, 12);
  expect(probabilities[1]).toBeCloseTo(96 / 118, 12);
  reopened.once("dialog", dialog => dialog.dismiss());
  await cards.first().getByRole("button").click();
  await expect(cards).toHaveCount(2);
  reopened.once("dialog", dialog => dialog.accept());
  await cards.first().getByRole("button").click();
  await expect(cards).toHaveCount(1);
  await reopened.reload();
  await expect(cards).toHaveCount(1);
  reopened.once("dialog", dialog => dialog.accept());
  await reopened.getByRole("button", { name: "Eliminar todo el historial" }).click();
  await expect(cards).toHaveCount(0);
  await reopened.reload();
  await expect(reopened.locator("#history-status")).toContainText("Todavía no hay");
});

test("a quota error keeps inference usable and never claims the record was saved", async ({ page }) => {
  await page.addInitScript(() => {
    IDBObjectStore.prototype.add = function () { throw new DOMException("Full", "QuotaExceededError"); };
  });
  await page.goto("/");
  for (const choice of await page.locator('input[value="true"] + span').all()) await choice.click();
  await page.getByRole("button", { name: "Ver orientación comercial" }).click();
  await expect(page.locator("#probability-value")).toContainText("81.4");
  await expect(page.locator("#save-status")).toContainText("no se pudo guardar");
  await expect(page.locator("#history-list > li")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Ver orientación comercial" })).toBeEnabled();
});

test("blocked storage does not prevent evaluation", async ({ page }) => {
  await page.addInitScript(() => {
    IDBFactory.prototype.open = function () { throw new DOMException("Denied", "SecurityError"); };
  });
  await page.goto("/");
  await expect(page.locator("#history-status")).toContainText("No se pudo leer");
  for (const choice of await page.locator('input[value="false"] + span').all()) await choice.click();
  await page.getByRole("button", { name: "Ver orientación comercial" }).click();
  await expect(page.locator("#probability-value")).toContainText("9.8");
  await expect(page.locator("#save-status")).toContainText("no se pudo guardar");
});

test("history fits a 320 px screen and reset retains saved evaluations", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 740 });
  await page.goto("/");
  await evaluate(page, true);
  await page.getByRole("button", { name: "Realizar otra evaluación" }).click();
  await expect(page.locator("input:checked")).toHaveCount(0);
  await expect(page.locator("#history-list > li")).toHaveCount(1);
  await page.locator("#history-list summary").click();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.locator("#history").screenshot({ path: "test-results/history-mobile.png" });
});
