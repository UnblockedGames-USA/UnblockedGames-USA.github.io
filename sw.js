/* Unblocked Games USA PWA service worker.
   Caches the app shell and previously visited same-origin pages.
   External game hosts still require an internet connection. */
const SHELL_CACHE = 'ugusa-pwa-shell-v2';
const PAGE_CACHE = 'ugusa-pwa-pages-v2';
const PRECACHE_URLS = [
  '/',
  '/offline.html',
  '/manifest.webmanifest',
  '/assets/favicon.svg',
  '/assets/pwa-icon.svg',
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
      .then(function (cache) {
        var requests = PRECACHE_URLS.map(function (url) {
          return new Request(url, { cache: 'reload' });
        });
        return cache.addAll(requests);
      })
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
  var request = event.request;
  if (request.method !== 'GET') return;

  var url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).then(function (response) {
        if (response && response.ok && response.type === 'basic' && !url.search) {
          var copy = response.clone();
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
          return caches.match(url.origin + url.pathname).then(function (cleanCached) {
            return cleanCached || caches.match('/offline.html');
          });
        });
      })
    );
    return;
  }

  if (url.pathname.indexOf('/assets/') === 0 || url.pathname === '/manifest.webmanifest') {
    event.respondWith(
      fetch(new Request(request, { cache: 'no-cache' })).then(function (response) {
        if (response && response.ok && response.type === 'basic') {
          var copy = response.clone();
          caches.open(SHELL_CACHE).then(function (cache) { cache.put(request, copy); });
        }
        return response;
      }).catch(function () {
        return caches.match(request).then(function (cached) { return cached || Response.error(); });
      })
    );
  }
});
