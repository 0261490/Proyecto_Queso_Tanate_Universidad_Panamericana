const CACHE_NAME = "__CACHE_NAME__";
const APP_SHELL = __APP_SHELL__;
const PRECACHED_URLS = new Set(APP_SHELL.map((path) => new URL(path, self.location.href).href));

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((key) => key.startsWith("tenate-") && key !== CACHE_NAME)
          .map((key) => caches.delete(key)),
      ))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET" || new URL(event.request.url).origin !== self.location.origin) {
    return;
  }

  if (event.request.mode === "navigate") {
    event.respondWith(
      caches.open(CACHE_NAME).then(async (cache) =>
        (await cache.match("./index.html")) ?? fetch(event.request)),
    );
    return;
  }

  event.respondWith(
    // These versioned, static same-origin files do not vary by request headers.
    // Preview servers may add Vary: Origin; module/CSS requests then differ from
    // addAll's requests and would miss the precache on the very first offline load.
    caches.open(CACHE_NAME).then(async (cache) => (await cache.match(event.request, {
      ignoreVary: PRECACHED_URLS.has(event.request.url),
    })) ?? fetch(event.request).then((response) => {
      if (response.ok) {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
      }
      return response;
    })),
  );
});
