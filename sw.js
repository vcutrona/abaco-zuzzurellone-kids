// Service worker: lets the game work offline.
// The cache name follows the game version, so every release replaces the old cache.
const VERSION = "1.2.0";
const CACHE = `abaco-v${VERSION}`;
const FILES = [
  "./",
  "manifest.webmanifest",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/apple-touch-icon.png",
  "fonts/baloo-2-latin-500-normal.woff2",
  "fonts/baloo-2-latin-700-normal.woff2",
  "fonts/baloo-2-latin-800-normal.woff2"
];

// cache: "reload" skips the browser's HTTP cache (GitHub Pages keeps files for 10 minutes),
// so a new version never stores the previous release's files
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE)
    .then(c => c.addAll(FILES.map(f => new Request(f, { cache: "reload" }))))
    .then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// The page: network first, so online players always get the latest version; the cache when offline,
// or when the network is too slow (after NETWORK_WAIT ms the cached copy is served, and the network
// answer, if it arrives, still refreshes the cache for next time).
// Everything else (fonts, icons): cache first, since those files only change with a new release.
const NETWORK_WAIT = 3000;
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  if (req.mode === "navigate") {
    const network = fetch(req).then(res => {
      if (res.ok) {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put("./", copy));
      }
      return res;
    });
    e.waitUntil(network.catch(() => {}));
    const slow = new Promise(resolve => setTimeout(resolve, NETWORK_WAIT))
      .then(async () => (await caches.match("./")) || network);
    e.respondWith(Promise.race([network, slow])
      .catch(async () => (await caches.match("./")) || Response.error()));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
});
