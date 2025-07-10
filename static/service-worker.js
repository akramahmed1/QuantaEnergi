self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open("energyopti-pro-v48").then((cache) => {
            return cache.addAll([
                "/static/index.html",
                "/static/manifest.json"
            ]);
        })
    );
});

self.addEventListener("fetch", (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
