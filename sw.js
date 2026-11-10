// Cache supaya aplikasi bisa dibuka tanpa internet.
// Naikkan VERSION (dan APP_VERSION di index.html) setiap ada perubahan.
const VERSION = "v8";
const FILES = ["./", "./index.html", "./manifest.webmanifest", "./icon.svg"];
self.addEventListener("install", e => e.waitUntil(
  caches.open(VERSION).then(c => c.addAll(FILES.map(f => new Request(f, {cache: "reload"})))).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  // Hanya file aplikasi sendiri; request ke GitHub (sinkron) tidak disentuh dan tidak di-cache.
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  // Ada internet: selalu ambil dari server (lewati cache HTTP 10 menit GitHub Pages). Offline: pakai cache.
  e.respondWith(
    fetch(e.request, {cache: "no-store"}).then(r => {
      if (r.ok){ const c = r.clone(); caches.open(VERSION).then(x => x.put(e.request, c)); }
      return r;
    }).catch(() => caches.match(e.request, {ignoreSearch: true})));
});
