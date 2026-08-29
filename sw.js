const CACHE_NAME = 'pomocnik-strazaka-v3';
const SHELL_FILES = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-180.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/favicon-32.png',
  './images/vehicles_v1_zone_map_d1.jpg',
  './images/vehicles_v1_zone_map_d2.jpg',
  './images/vehicles_v1_zone_map_d3.jpg',
  './images/vehicles_v1_zone_map_k1.jpg',
  './images/vehicles_v1_zone_map_k2.jpg',
  './images/vehicles_v1_zone_map_k3.jpg',
  './images/vehicles_v2_zone_map_d1.jpg',
  './images/vehicles_v2_zone_map_d2.jpg',
  './images/vehicles_v2_zone_map_d3.jpg',
  './images/vehicles_v2_zone_map_k2.jpg',
  './images/vehicles_v2_zone_map_k3.jpg',
  './images/vehicles_v3_zone_map_d1.jpg',
  './images/vehicles_v3_zone_map_d2.jpg',
  './images/vehicles_v3_zone_map_d3.jpg',
  './images/vehicles_v3_zone_map_d4.jpg',
  './images/vehicles_v3_zone_map_k1.jpg',
  './images/vehicles_v3_zone_map_k2.jpg',
  './images/vehicles_v3_zone_map_k3.jpg',
  './images/vehicles_v3_zone_map_k4.jpg'
];

/* Instalacja — zapisz powłokę aplikacji (kod + zdjęcia skrytek) do pamięci telefonu,
   żeby dało się otworzyć i przeczytać dane techniczne nawet bez zasięgu. */
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(SHELL_FILES))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

/* Firebase/Firestore ma własną obsługę offline (kolejkowanie zapisów, cache odczytów) —
   nie ingerujemy w te żądania, niech idą normalnie do sieci. */
function isFirebaseRequest(url) {
  return url.includes('firestore.googleapis.com')
    || url.includes('googleapis.com')
    || url.includes('gstatic.com')
    || url.includes('identitytoolkit')
    || url.includes('firebaseapp.com');
}

/* Sieć zawsze na pierwszym miejscu — dzięki temu przy normalnym zasięgu zawsze widzisz
   najnowszą wersję. Zapisana kopia (cache) używana jest TYLKO gdy sieć naprawdę zawiedzie
   (brak zasięgu) — dokładnie po to zbudowany jest tryb offline, nie po to żeby pokazywać
   starszą wersję kiedy internet działa. */
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  const url = event.request.url;
  if (isFirebaseRequest(url)) return;

  event.respondWith(
    fetch(event.request).then((response) => {
      if (response && response.status === 200) {
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
      }
      return response;
    }).catch(() => caches.match(event.request))
  );
});
