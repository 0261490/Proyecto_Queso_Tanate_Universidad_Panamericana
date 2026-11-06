import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import test from "node:test";

function worker() {
  const handlers: Record<string, (event: any) => void> = {};
  const files = new Map<string, Response>();
  const removed: string[] = [];
  let online = true;
  const cache = {
    async addAll(paths: string[]) {
      for (const path of paths) files.set(path, new Response(`cached:${path}`));
    },
    async match(request: string | { url: string }) {
      return files.get(typeof request === "string" ? request : `.${new URL(request.url).pathname}`)?.clone();
    },
    async put(request: { url: string }, response: Response) {
      files.set(`.${new URL(request.url).pathname}`, response);
    },
  };
  const source = readFileSync(new URL("../scripts/sw-template.js", import.meta.url), "utf8")
    .replace("__CACHE_NAME__", "tenate-test")
    .replace("__APP_SHELL__", JSON.stringify(["./index.html", "./assets/app.js", "./assets/app.css"]));
  runInNewContext(source, {
    URL,
    self: {
      location: { origin: "https://tenate.test" },
      addEventListener: (name: string, handler: any) => { handlers[name] = handler; },
      skipWaiting: async () => {},
      clients: { claim: async () => {} },
    },
    caches: {
      open: async () => cache,
      keys: async () => ["tenate-old", "tenate-test", "other-app"],
      delete: async (name: string) => { removed.push(name); return true; },
    },
    fetch: async () => {
      if (!online) throw new Error("Network unavailable");
      return new Response("new server version");
    },
  });
  return {
    removed,
    offline() { online = false; },
    async lifecycle(name: string) {
      let pending: Promise<unknown> | undefined;
      handlers[name]({ waitUntil: (promise: Promise<unknown>) => { pending = promise; } });
      await pending;
    },
    async request(path: string, mode = "same-origin", method = "GET") {
      let response: Promise<Response> | undefined;
      handlers.fetch({
        request: { url: new URL(path, "https://tenate.test").href, mode, method },
        respondWith: (promise: Promise<Response>) => { response = promise; },
      });
      return await response;
    },
  };
}

test("offline navigation and assets survive after installation", async () => {
  const sw = worker();
  await sw.lifecycle("install");
  sw.offline();
  assert.equal(await (await sw.request("/?evaluation=1", "navigate"))?.text(), "cached:./index.html");
  assert.equal(await (await sw.request("/assets/app.js"))?.text(), "cached:./assets/app.js");
  assert.equal(await (await sw.request("/assets/app.css"))?.text(), "cached:./assets/app.css");
});

test("navigation keeps the cached build together when a newer server build exists", async () => {
  const sw = worker();
  await sw.lifecycle("install");
  assert.equal(await (await sw.request("/", "navigate"))?.text(), "cached:./index.html");
});

test("activation removes only previous Tenate caches and ignores unrelated requests", async () => {
  const sw = worker();
  await sw.lifecycle("activate");
  assert.deepEqual(sw.removed, ["tenate-old"]);
  assert.equal(await sw.request("https://other.test/image.png"), undefined);
  assert.equal(await sw.request("/", "same-origin", "POST"), undefined);
});
