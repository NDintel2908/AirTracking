// Kiểm tra xem trình duyệt có hỗ trợ Service Worker không
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/js/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker registered successfully with scope: ', registration.scope);
      })
      .catch(error => {
        console.log('ServiceWorker registration failed: ', error);
      });
  });
}

// Xử lý cài đặt ứng dụng lên màn hình chính
let deferredPrompt;
const addBtn = document.createElement('button');
addBtn.style.display = 'none';
addBtn.classList.add('install-button');
addBtn.textContent = 'Cài đặt ứng dụng';

window.addEventListener('beforeinstallprompt', (e) => {
  // Ngăn Chrome hiển thị cửa sổ cài đặt tự động
  e.preventDefault();
  // Lưu sự kiện để sử dụng sau
  deferredPrompt = e;
  // Cập nhật UI để thông báo cho người dùng có thể cài đặt ứng dụng
  addBtn.style.display = 'block';
  
  // Thêm nút cài đặt vào header
  document.querySelector('header').appendChild(addBtn);
});

// Xử lý khi người dùng nhấp vào nút cài đặt
addBtn.addEventListener('click', (e) => {
  // Ẩn nút cài đặt
  addBtn.style.display = 'none';
  // Hiển thị lời nhắc cài đặt
  deferredPrompt.prompt();
  // Chờ người dùng phản hồi lời nhắc
  deferredPrompt.userChoice.then((choiceResult) => {
    if (choiceResult.outcome === 'accepted') {
      console.log('Người dùng đã chấp nhận cài đặt A2HS');
    } else {
      console.log('Người dùng đã từ chối cài đặt A2HS');
    }
    deferredPrompt = null;
  });
});