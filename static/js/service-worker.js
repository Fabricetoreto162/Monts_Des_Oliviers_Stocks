self.addEventListener('install', () => {
    console.log('Service Worker installé');
});

self.addEventListener('activate', () => {
    console.log('Service Worker activé');
});
