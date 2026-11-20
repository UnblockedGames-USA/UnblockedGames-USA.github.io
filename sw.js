/* Unblocked Games USA PWA service worker. Only same-origin shell files and
   previously visited HTML pages are cached; third-party game embeds stay online. */
const SHELL_CACHE = 'ugusa-pwa-shell-v1';
const PAGE_CACHE = 'ugusa-pwa-pages-v1';
const PRECACHE_URLS = [
  '/',
  '/offline.html',
  '/manifest.webmanifest',
  '/assets/favicon.svg',
  '/assets/pwa-icon-192.png',
  '/assets/pwa-icon-512.png',
  '/assets/pwa-icon-maskable-512.png',
  '/assets/site.css?v=1',
  '/assets/site-extra.css?v=1',
  '/assets/js/site.js?v=1'
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(SHELL_CACHE)
      .then(function (cache) { return cache.addAll(PRECACHE_URLS); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (key) {
        return key.indexOf('ugusa-pwa-') === 0 && key !== SHELL_CACHE && key !== PAGE_CACHE;
      }).map(function (key) { return caches.delete(key); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (event) {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).then(function (response) {
        if (response && response.ok && response.type === 'basic' && !url.search) {
          const copy = response.clone();
          return caches.open(PAGE_CACHE).then(function (cache) {
            return cache.put(request, copy).then(function () {
              return cache.keys().then(function (keys) {
                if (keys.length > 30) return cache.delete(keys[0]).then(function () { return response; });
                return response;
              });
            });
          });
        }
        return response;
      }).catch(function () {
        return caches.match(request).then(function (cached) {
          if (cached) return cached;
          const cleanUrl = url.origin + url.pathname;
          return caches.match(cleanUrl).then(function (cleanCached) {
            return cleanCached || caches.match('/offline.html');
          });
        });
      })
    );
    return;
  }

  if (url.pathname.indexOf('/assets/') === 0 || url.pathname === '/manifest.webmanifest') {
    event.respondWith(
      fetch(request).then(function (response) {
        if (response && response.ok && response.type === 'basic') {
          const copy = response.clone();
          caches.open(SHELL_CACHE).then(function (cache) { cache.put(request, copy); });
        }
        return response;
      }).catch(function () {
        return caches.match(request).then(function (cached) { return cached || Response.error(); });
      })
    );
  }
});
