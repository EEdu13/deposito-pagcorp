// Service Worker para PWA Auto-Update
const CACHE_NAME = 'pagcorp-v' + Date.now();
const urlsToCache = [
    '/dashboard-pedidos-real.html',
    '/manifest.json',
    '/icon-72x72.png',
    '/icon-96x96.png',
    '/icon-128x128.png',
    '/icon-144x144.png',
    '/icon-152x152.png',
    '/icon-192x192.png',
    '/icon-384x384.png',
    '/icon-512x512.png',
    '/icon-192x192-maskable.png',
    '/icon-512x512-maskable.png',
    '/LARSIL_branco_fundo_transparente.png'
];

// Instalar Service Worker
self.addEventListener('install', function(event) {
    console.log('🔧 Service Worker instalando...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('📦 Cache aberto');
                return cache.addAll(urlsToCache);
            })
    );
    
    // Força o novo Service Worker a se tornar ativo imediatamente
    self.skipWaiting();
});

// Ativar Service Worker
self.addEventListener('activate', function(event) {
    console.log('✅ Service Worker ativado');
    
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    // Remove caches antigos
                    if (cacheName !== CACHE_NAME) {
                        console.log('🗑️ Removendo cache antigo:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    
    // Força o Service Worker a controlar todas as páginas imediatamente
    return self.clients.claim();
});

// Interceptar requisições
self.addEventListener('fetch', function(event) {
    // Para requisições da API, sempre buscar da rede (dados em tempo real)
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .catch(function() {
                    console.log('🌐 API offline, tentando cache...');
                    return caches.match(event.request);
                })
        );
        return;
    }
    
    // Para outros arquivos, tentar cache primeiro
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Se encontrou no cache, retorna
                if (response) {
                    // Mas também busca da rede em paralelo para atualizar o cache
                    fetch(event.request).then(function(fetchResponse) {
                        if (fetchResponse && fetchResponse.status === 200) {
                            const responseToCache = fetchResponse.clone();
                            caches.open(CACHE_NAME).then(function(cache) {
                                cache.put(event.request, responseToCache);
                            });
                        }
                    }).catch(() => {
                        console.log('🌐 Rede indisponível, usando cache');
                    });
                    
                    return response;
                }
                
                // Se não encontrou no cache, busca da rede
                return fetch(event.request);
            }
        )
    );
});

// Receber mensagens do cliente
self.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
