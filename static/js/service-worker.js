// Tên của cache
const CACHE_NAME = 'env-monitor-cache-v1';

// Danh sách các URL cần cache
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/js/charts.js',
  '/static/icons/icon-192x192.svg',
  '/static/icons/icon-512x512.svg',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
];

// Cài đặt service worker và cache tất cả nội dung
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache opened');
        return cache.addAll(urlsToCache);
      })
  );
});

// Truy xuất tài nguyên từ cache hoặc internet
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }

        // Clone request để có thể tái sử dụng
        const fetchRequest = event.request.clone();

        // Đặc biệt xử lý cho API endpoints
        if (fetchRequest.url.includes('/api/')) {
          return fetch(fetchRequest).catch(() => {
            // Nếu fetch thất bại (không có internet), trả về dữ liệu đã cache
            if (fetchRequest.url.includes('/api/current')) {
              return new Response(JSON.stringify({
                "status": "offline",
                "timestamp": new Date().toLocaleTimeString('vi-VN', {hour: '2-digit', minute:'2-digit'}),
                "message": "Dữ liệu offline"
              }), {
                headers: { 'Content-Type': 'application/json' }
              });
            }
            
            return new Response(JSON.stringify([]), {
              headers: { 'Content-Type': 'application/json' }
            });
          });
        }

        return fetch(fetchRequest).then(response => {
          // Kiểm tra xem có phản hồi hợp lệ không
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone response để cache
          const responseToCache = response.clone();

          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });

          return response;
        });
      })
  );
});

// Xóa cache cũ khi có phiên bản mới
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];

  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});