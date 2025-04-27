document.addEventListener('DOMContentLoaded', function() {
    // Thêm hàm cập nhật dữ liệu để có thể sử dụng từ Socket.IO
    window.updateDataDisplay = function(data) {
        renderDataCards(data);
        updateLastUpdated();
    };
    // Kiểm tra trạng thái kết nối
    function updateOnlineStatus() {
        const offlineIndicator = document.getElementById('offline-indicator');
        if (navigator.onLine) {
            offlineIndicator.style.display = 'none';
        } else {
            offlineIndicator.style.display = 'block';
        }
    }

    // Lắng nghe sự kiện kết nối
    window.addEventListener('online', () => {
        updateOnlineStatus();
        fetchCurrentData();
        updateMainChart(document.getElementById('chart-param').value);
    });
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();

    // Xử lý kéo xuống để làm mới
    let touchStartY = 0;
    let touchEndY = 0;
    
    document.addEventListener('touchstart', e => {
        touchStartY = e.touches[0].clientY;
    }, { passive: true });
    
    document.addEventListener('touchmove', e => {
        touchEndY = e.touches[0].clientY;
        if (window.scrollY === 0 && touchEndY - touchStartY > 70) {
            document.body.classList.add('pull-active');
        }
    }, { passive: true });
    
    document.addEventListener('touchend', e => {
        if (document.body.classList.contains('pull-active')) {
            document.body.classList.remove('pull-active');
            refreshData();
        }
    });

    // Initialize
    updateLastUpdated();
    fetchCurrentData();
    initializeMainChart();
    checkThingsboardStatus();

    // Event listeners
    document.getElementById('refresh-btn').addEventListener('click', function() {
        const icon = document.querySelector('#refresh-btn i');
        icon.classList.add('spinning');
        
        refreshData();
        
        // Dừng hiệu ứng quay sau 1 giây
        setTimeout(() => {
            icon.classList.remove('spinning');
        }, 1000);
    });

    document.getElementById('chart-param').addEventListener('change', function() {
        updateMainChart(this.value);
    });

    // Xử lý chuyển tab qua bottom navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function() {
            const tabName = this.querySelector('.nav-label').textContent;
            
            if (tabName === 'Biểu đồ') {
                // Cuộn xuống phần biểu đồ
                document.querySelector('.chart-container').scrollIntoView({
                    behavior: 'smooth'
                });
            } 
            else if (tabName === 'Cài đặt') {
                // Tạm thời chỉ hiển thị thông báo
                alert('Tính năng đang phát triển');
            }
            
            // Cập nhật tab hoạt động
            document.querySelectorAll('.nav-item').forEach(navItem => {
                navItem.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    // Auto refresh data every 30 seconds
    setInterval(function() {
        if (navigator.onLine) {
            fetchCurrentData();
            updateMainChart(document.getElementById('chart-param').value);
        }
    }, 30000);

    // Functions
    function refreshData() {
        fetchCurrentData();
        updateMainChart(document.getElementById('chart-param').value);
    }

    function updateLastUpdated() {
        const now = new Date();
        document.getElementById('last-updated').textContent = 
            `Cập nhật lúc: ${now.toLocaleTimeString('vi-VN', {hour: '2-digit', minute:'2-digit'})}`;
    }

    function fetchCurrentData() {
        const refreshIcon = document.querySelector('#refresh-btn i');
        if (refreshIcon) {
            refreshIcon.classList.add('spinning');
        }
        
        fetch('/api/current')
            .then(response => response.json())
            .then(data => {
                updateDataDisplay(data);
                if (refreshIcon) {
                    refreshIcon.classList.remove('spinning');
                }
            })
            .catch(error => {
                console.error('Lỗi tải dữ liệu:', error);
                document.getElementById('data-grid').innerHTML = 
                    '<div class="error">Lỗi tải dữ liệu. Vui lòng thử lại.</div>';
                
                // Kiểm tra nếu đang offline
                if (!navigator.onLine) {
                    document.getElementById('data-grid').innerHTML = 
                        '<div class="error">Bạn đang ở chế độ ngoại tuyến. Vui lòng kiểm tra kết nối mạng.</div>';
                }
                
                if (refreshIcon) {
                    refreshIcon.classList.remove('spinning');
                }
            });
    }

    function renderDataCards(data) {
        const dataGrid = document.getElementById('data-grid');
        dataGrid.innerHTML = '';

        // Kiểm tra và hiển thị trạng thái thiết bị
        if (data.device_status) {
            // Tạo thẻ div hiển thị trạng thái thiết bị
            const deviceStatusCard = document.createElement('div');
            deviceStatusCard.className = 'device-status-card';
            
            let statusClass = '';
            let statusMessage = '';
            let statusIcon = '';
            
            switch(data.device_status) {
                case 'online':
                    statusClass = 'online';
                    statusMessage = 'Thiết bị đang hoạt động bình thường';
                    statusIcon = 'fa-check-circle';
                    break;
                case 'inactive':
                    statusClass = 'inactive';
                    statusMessage = 'Thiết bị không hoạt động (không có dữ liệu mới)';
                    statusIcon = 'fa-exclamation-circle';
                    break;
                case 'offline':
                    statusClass = 'offline';
                    statusMessage = 'Thiết bị ngắt kết nối';
                    statusIcon = 'fa-times-circle';
                    break;
                default:
                    statusClass = 'unknown';
                    statusMessage = 'Không xác định được trạng thái thiết bị';
                    statusIcon = 'fa-question-circle';
            }
            
            // Tính thời gian từ lần cập nhật cuối cùng
            let lastUpdateInfo = '';
            if (data.last_data_timestamp) {
                const lastUpdateTime = new Date(data.last_data_timestamp);
                const currentTime = new Date();
                const timeDiffMinutes = Math.floor((currentTime - lastUpdateTime) / (1000 * 60));
                
                if (timeDiffMinutes < 60) {
                    lastUpdateInfo = `Dữ liệu cuối cập nhật: ${timeDiffMinutes} phút trước`;
                } else {
                    const hours = Math.floor(timeDiffMinutes / 60);
                    const minutes = timeDiffMinutes % 60;
                    lastUpdateInfo = `Dữ liệu cuối cập nhật: ${hours} giờ ${minutes} phút trước`;
                }
            }
            
            deviceStatusCard.innerHTML = `
                <div class="status-icon ${statusClass}">
                    <i class="fas ${statusIcon}"></i>
                </div>
                <div class="status-info">
                    <div class="status-message ${statusClass}">${statusMessage}</div>
                    <div class="last-update-time">${lastUpdateInfo}</div>
                </div>
            `;
            
            dataGrid.appendChild(deviceStatusCard);
        }

        // Parameter to icon mapping
        const paramIcons = {
            'pm10': 'fa-cloud',
            'pm25': 'fa-smog',
            'temperature': 'fa-thermometer-half',
            'humidity': 'fa-water',
            'noise': 'fa-volume-up',
            'co': 'fa-wind',
            'aqi': 'fa-leaf'
        };

        // Parameter to display name mapping
        const paramNames = {
            'pm10': 'PM10',
            'pm25': 'PM2.5',
            'temperature': 'Nhiệt độ',
            'humidity': 'Độ ẩm',
            'noise': 'Tiếng ồn',
            'co': 'CO',
            'aqi': 'Chỉ số AQI'
        };
        
        // Status translation
        const statusTranslations = {
            'normal': 'BÌNH THƯỜNG',
            'warning': 'CẢNH BÁO',
            'danger': 'NGUY HIỂM',
            'offline': 'NGOẠI TUYẾN',
            'unknown': 'KHÔNG CÓ DỮ LIỆU'
        };

        // Xử lý dữ liệu từng tham số
        for (const [param, reading] of Object.entries(data)) {
            // Bỏ qua các trường đặc biệt không phải dữ liệu cảm biến
            if (param === 'device_status' || param === 'last_data_timestamp') {
                continue;
            }
            
            const card = document.createElement('div');
            card.className = 'data-card';
            
            const statusText = statusTranslations[reading.status] || reading.status.toUpperCase();
            
            // Thêm chỉ báo trạng thái
            let statusIndicator = '';
            if (reading.status === 'warning' || reading.status === 'danger') {
                statusIndicator = `<span class="status-badge ${reading.status}"></span>`;
            }
            
            // Kiểm tra nếu có thông báo thay vì giá trị
            let valueDisplay = '';
            if (reading.message) {
                valueDisplay = `<div class="card-message">${reading.message}</div>`;
            } else {
                valueDisplay = `
                    <div class="card-value">${reading.value !== null ? reading.value : '--'}</div>
                    <div class="card-unit">${reading.unit}</div>
                `;
            }
            
            card.innerHTML = `
                <div class="card-title">
                    <i class="fas ${paramIcons[param]}"></i> ${paramNames[param]}
                    ${statusIndicator}
                </div>
                ${valueDisplay}
                <div class="card-status ${reading.status}">
                    ${statusText}
                </div>
                <div class="card-timestamp">
                    Cập nhật: ${reading.timestamp}
                </div>
            `;
            
            // Add tap effect (for mobile devices)
            card.addEventListener('touchstart', function() {
                this.style.opacity = '0.7';
            });
            
            card.addEventListener('touchend', function() {
                this.style.opacity = '1';
                // Navigate after a short delay to show the tap effect
                setTimeout(() => {
                    window.location.href = `/parameter/${param}`;
                }, 150);
            });
            
            // For desktop users
            card.addEventListener('click', () => {
                window.location.href = `/parameter/${param}`;
            });
            
            dataGrid.appendChild(card);
        }
    }

    function initializeMainChart() {
        // Default to PM2.5 when loading the page
        updateMainChart('pm25');
    }

    function updateMainChart(parameter) {
        fetch('/api/historical')
            .then(response => response.json())
            .then(data => {
                const paramData = data[parameter];
                const labels = paramData.map(point => point.timestamp);
                const values = paramData.map(point => point.value);

                // Get the parameter unit from the current data
                return fetch('/api/current')
                    .then(response => response.json())
                    .then(currentData => {
                        const unit = currentData[parameter].unit;
                        const paramName = parameter.toUpperCase();
                        updateChart(labels, values, paramName, unit);
                    });
            })
            .catch(error => {
                console.error('Lỗi cập nhật biểu đồ:', error);
            });
    }

    function updateChart(labels, values, paramName, unit) {
        const ctx = document.getElementById('main-chart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (window.mainChart) {
            window.mainChart.destroy();
        }
        
        // Create gradient for better visual appearance
        const gradient = createGradientBackground(ctx, 'rgba(75, 192, 192, 0.7)', 'rgba(75, 192, 192, 0.1)');
        
        window.mainChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels.map(formatTimeForDisplay),
                datasets: [{
                    label: `${paramName} (${unit})`,
                    data: values,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: gradient,
                    tension: 0.3,
                    fill: true,
                    pointRadius: 3,
                    pointHoverRadius: 6
                }]
            },
            options: getStandardChartOptions(paramName)
        });
    }
    
    function checkThingsboardStatus() {
        const dataSourceStatus = document.getElementById('data-source-status');
        
        if (dataSourceStatus) {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    if (data.thingsboard_connected) {
                        dataSourceStatus.textContent = 'ThingsBoard API';
                        dataSourceStatus.className = 'connected';
                    } else {
                        dataSourceStatus.textContent = 'Dữ liệu giả lập (Không thể kết nối ThingsBoard)';
                        dataSourceStatus.className = 'disconnected';
                        console.warn('ThingsBoard không khả dụng:', data.error || 'Lỗi xác thực');
                    }
                })
                .catch(error => {
                    console.error('Lỗi kiểm tra trạng thái API:', error);
                    dataSourceStatus.textContent = 'Dữ liệu giả lập (Lỗi kết nối)';
                    dataSourceStatus.className = 'error';
                });
        }
        
        // Kiểm tra lại sau 2 phút
        setTimeout(checkThingsboardStatus, 2 * 60 * 1000);
    }
});
