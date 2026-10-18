// Service worker: lets the game work offline.
// The cache name follows the game version, so every release replaces the old cache.
const VERSION = "1.0.2";
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

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// The page: network first, so online players always get the latest version; the cache when offline.
// Everything else (fonts, icons): cache first, since those files only change with a new release.
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  if (req.mode === "navigate") {
    e.respondWith(fetch(req)
      .then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put("./", copy));
        return res;
      })
      .catch(() => caches.match("./")));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
});
