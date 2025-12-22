// Service Worker para PWA - MINIMALISTA para Android
const CACHE_NAME = 'pagcorp-v1.0.0';
const urlsToCache = [
    '/dashboard-pedidos-real.html',
    '/manifest.json',
    '/icon-192x192.png',
    '/icon-512x512.png'
];

// Instalar Service Worker
self.addEventListener('install', function(event) {
    console.log('🔧 Service Worker instalando...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('📦 Cache básico criado');
                return cache.addAll(urlsToCache);
            })
            .catch(err => console.log('❌ Erro no cache:', err))
    );
    
    // Ativar imediatamente
    self.skipWaiting();
});

// Ativar Service Worker
self.addEventListener('activate', function(event) {
    console.log('✅ Service Worker ativado');
    
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('🗑️ Removendo cache antigo:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    
    return self.clients.claim();
});

// Fetch Strategy - Network First para PWA
self.addEventListener('fetch', function(event) {
    // API sempre da rede
    if (event.request.url.includes('/api/')) {
        event.respondWith(fetch(event.request));
        return;
    }
    
    // Outros recursos: Network First, Cache como fallback
    event.respondWith(
        fetch(event.request)
            .then(function(response) {
                // Se sucesso, salva no cache e retorna
                if (response.status === 200) {
                    const responseToCache = response.clone();
                    caches.open(CACHE_NAME).then(function(cache) {
                        cache.put(event.request, responseToCache);
                    });
                }
                return response;
            })
            .catch(function() {
                // Se falhou, tenta cache
                return caches.match(event.request);
            })
    );
});
