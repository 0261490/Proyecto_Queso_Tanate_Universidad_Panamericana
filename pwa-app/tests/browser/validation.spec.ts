import { readFileSync } from "node:fs";
import { test, expect } from "@playwright/test";

const fixture = JSON.parse(readFileSync(new URL("../../../inference-engine/tests/fixtures/assessment-reference.json", import.meta.url), "utf8"));

test("incomplete forms do not infer or save and focus the first missing answer", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Ver orientación comercial" }).click();
  await expect(page.getByRole("alert")).toContainText("Faltan 7 preguntas");
  await expect(page.locator('input[name="traditionalMexican"][value="true"]')).toBeFocused();
  await expect(page.locator("#results")).toBeHidden();
  await expect(page.locator("#history-list > li")).toHaveCount(0);
  for (const choice of (await page.locator('input[value="true"] + span').all()).slice(0, 6)) await choice.click();
  await page.getByRole("button", { name: "Ver orientación comercial" }).click();
  await expect(page.getByRole("alert")).toContainText("Falta responder una pregunta");
  await expect(page.locator('input[name="sensoryUniqueness"][value="true"]')).toBeFocused();
  await expect(page.locator("#history-list > li")).toHaveCount(0);
});

test("mixed Python golden cases reach the visible result and exact native history offline", async ({ page, context }, testInfo) => {
  const failures: string[] = [];
  page.on("requestfailed", request => failures.push(`${request.url()}: ${request.failure()?.errorText}`));
  page.on("pageerror", error => failures.push(error.message));
  await page.goto("/");
  await expect(page.locator("#offline-status")).toContainText("Lista para usar");
  const cacheState = await page.evaluate(async () => ({
    controller: navigator.serviceWorker.controller?.state,
    caches: await Promise.all((await caches.keys()).map(async name => {
      const cache = await caches.open(name);
      return { name, resources: await Promise.all((await cache.keys()).map(async r => ({ url: r.url,
        origin: r.headers.get("origin"), vary: (await cache.match(r))?.headers.get("vary") }))) };
    })),
  }));
  await testInfo.attach("offline-readiness", { body: JSON.stringify(cacheState, null, 2), contentType: "application/json" });
  await context.setOffline(true);
  await page.reload();
  await testInfo.attach("offline-network-failures", { body: JSON.stringify(failures), contentType: "application/json" });
  await expect(page.locator('input[type="radio"]')).toHaveCount(14);
  for (const mask of [21, 42, 85, 106]) {
    const c = fixture.cases.find(c => c.id === `assessment_${String(mask).padStart(3, "0")}`);
    for (const [id, value] of Object.entries(c.answers)) {
      await page.locator(`input[name="${id}"][value="${value}"] + span`).click();
    }
    await page.getByRole("button", { name: "Ver orientación comercial" }).click();
    await expect(page.locator("#save-status")).toContainText("Evaluación guardada");
    await expect(page.locator("#probability-value")).toContainText((c.probability * 100).toFixed(1));
    await expect(page.locator("#results-title")).toBeFocused();
    const stored = await page.evaluate(() => new Promise<any[]>((resolve, reject) => {
      const open = indexedDB.open("tenate-history");
      open.onerror = () => reject(open.error);
      open.onsuccess = () => {
        const db = open.result;
        const tx = db.transaction("assessments");
        const req = tx.objectStore("assessments").index("createdAt").getAll();
        tx.oncomplete = () => { db.close(); resolve(req.result); };
        tx.onabort = () => { db.close(); reject(tx.error); };
      };
    }));
    const latest = stored.at(-1);
    expect(latest.answers).toEqual(c.answers);
    expect(latest.evidence).toEqual(c.evidence);
    expect(latest.model.sha256).toBe(fixture.model_sha256);
    expect(latest.result.probability).toBeCloseTo(c.probability, 12);
  }
  await expect(page.locator("#history-list > li")).toHaveCount(4);
  await expect(page.locator("body")).not.toContainText(/Q[1-8]_/);
});

test("keyboard evaluation, stale-result hiding and reset retain the original snapshot", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Saltar al cuestionario" })).toBeFocused();
  await page.keyboard.press("Enter");
  // Focus a native group, then select its value through the keyboard.
  for (const radio of await page.locator('input[value="true"]').all()) {
    await radio.focus();
    await page.keyboard.press("Space");
    await expect(radio).toBeChecked();
  }
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Ver orientación comercial" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#save-status")).toContainText("Evaluación guardada");
  await expect(page.locator("#results-title")).toBeFocused();
  await page.locator('input[name="recommendation"][value="true"]').focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.locator('input[name="recommendation"][value="false"]')).toBeChecked();
  await expect(page.locator("#results")).toBeHidden();
  await expect(page.locator("#history-list > li")).toHaveCount(1);
  await page.getByRole("button", { name: "Ver orientación comercial" }).click();
  await expect(page.locator("#save-status")).toContainText("Evaluación guardada");
  await expect(page.locator("#probability-value")).toContainText("9.8");
  await expect(page.locator("#history-list > li")).toHaveCount(2);
  await expect(page.locator("#history-list summary").last()).toContainText("81.4");
  await page.getByRole("button", { name: "Realizar otra evaluación" }).click();
  await expect(page.locator("#assessment-title")).toBeFocused();
  await expect(page.locator("input:checked")).toHaveCount(0);
  await expect(page.locator("#history-list > li")).toHaveCount(2);
});
