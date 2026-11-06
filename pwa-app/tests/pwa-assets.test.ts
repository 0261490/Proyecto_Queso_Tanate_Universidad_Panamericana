import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

function read(relativePath: string): string {
  return readFileSync(new URL(`../${relativePath}`, import.meta.url), "utf8");
}

test("declares Spanish document landmarks and an accessible form", () => {
  const html = read("index.html");
  assert.match(html, /<html lang="es-MX">/);
  assert.match(html, /class="skip-link"/);
  assert.match(html, /<main id="top">/);
  assert.match(html, /<form id="assessment-form" novalidate>/);
  assert.match(html, /role="alert"/);
  assert.match(html, /aria-live="polite"/);
  assert.match(html, /role="meter"/);
  assert.match(html, /<noscript>/);
  assert.doesNotMatch(html, /Q[1-8](?:_|\b)/);
});

test("manifest supports standalone installation without absolute paths", () => {
  const manifest = JSON.parse(read("public/manifest.webmanifest"));
  assert.equal(manifest.lang, "es-MX");
  assert.equal(manifest.display, "standalone");
  assert.equal(manifest.id, "./");
  assert.equal(manifest.start_url, "./");
  assert.equal(manifest.scope, "./");
  assert.ok(manifest.icons.some((icon: { sizes?: string; type?: string }) =>
    icon.sizes === "192x192" && icon.type === "image/png"));
  assert.ok(manifest.icons.some((icon: { sizes?: string; type?: string; purpose?: string }) =>
    icon.sizes === "512x512" && icon.type === "image/png" && icon.purpose?.includes("maskable")));
  for (const icon of manifest.icons) assert.match(icon.src, /^\.\//);
});

test("styles expose keyboard focus and user preferences", () => {
  const styles = read("src/styles.css");
  assert.match(styles, /:focus-visible/);
  assert.match(styles, /prefers-reduced-motion/);
  assert.match(styles, /prefers-contrast: more/);
  assert.match(styles, /@media \(max-width: 560px\)/);
});

test("service worker template precaches and handles navigation offline", () => {
  const worker = read("scripts/sw-template.js");
  assert.match(worker, /cache\.addAll\(APP_SHELL\)/);
  assert.match(worker, /caches\.delete/);
  assert.match(worker, /event\.request\.mode === "navigate"/);
  assert.match(worker, /cache\.match\("\.\/index.html"\)/);
});
