// Tệp này chứa các chức năng tiện ích liên quan đến biểu đồ và hiển thị
// có thể được sử dụng chung giữa trang chính và trang chi tiết thông số

/**
 * Lấy màu dựa trên giá trị thông số và các ngưỡng của nó
 * @param {string} param - Tên thông số
 * @param {number} value - Giá trị thông số
 * @returns {string} - Mã màu HEX hoặc RGBA
 */
function getColorForValue(param, value) {
    // Ngưỡng mặc định nếu không tìm thấy từ API
    const defaultThresholds = {
        'pm10': { warning: 50, danger: 100 },
        'pm25': { warning: 25, danger: 50 },
        'temperature': { warning: 30, danger: 33 },
        'humidity': { warning: 70, danger: 85 },
        'noise': { warning: 70, danger: 85 },
        'co': { warning: 25, danger: 40 },
        'co2': { warning: 1000, danger: 1500 }
    };

    const thresholds = defaultThresholds[param] || { warning: 50, danger: 75 };
    
    if (value >= thresholds.danger) {
        return '#e74c3c'; // Màu nguy hiểm
    } else if (value >= thresholds.warning) {
        return '#f39c12'; // Màu cảnh báo
    } else {
        return '#2ecc71'; // Màu bình thường
    }
}

/**
 * Tạo nền gradient cho biểu đồ
 * @param {CanvasRenderingContext2D} ctx - Context của canvas
 * @param {string} startColor - Màu bắt đầu gradient
 * @param {string} endColor - Màu kết thúc gradient
 * @returns {CanvasGradient}
 */
function createGradientBackground(ctx, startColor, endColor) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, startColor);
    gradient.addColorStop(1, endColor);
    return gradient;
}

/**
 * Định dạng thời gian cho hiển thị biểu đồ
 * @param {string} timestamp - Chuỗi thời gian
 * @returns {string} - Chuỗi thời gian đã định dạng
 */
function formatTimeForDisplay(timestamp) {
    // Chuyển đổi định dạng giờ từ "14:23" thành "14:23"
    // Sau này có thể mở rộng để hiển thị 2:23 PM hoặc các định dạng khác
    try {
        const parts = timestamp.split(':');
        if (parts.length === 2) {
            return `${parts[0]}:${parts[1]}`;
        }
    } catch (e) {
        console.error('Error formatting time:', e);
    }
    return timestamp;
}

/**
 * Tạo các tùy chọn chuẩn cho biểu đồ
 * @param {string} title - Tiêu đề biểu đồ
 * @param {boolean} includeTime - Có hiển thị thời gian trong tooltip hay không
 * @returns {object} - Đối tượng tùy chọn cho Chart.js
 */
function getStandardChartOptions(title, includeTime = true) {
    // Kiểm tra nếu đang trên thiết bị di động
    const isMobile = window.innerWidth < 768;
    
    return {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 750, // Thời gian hiệu ứng khi tải biểu đồ
            easing: 'easeOutQuart'
        },
        interaction: {
            mode: 'index',
            intersect: false
        },
        plugins: {
            title: {
                display: !!title,
                text: title,
                font: {
                    size: isMobile ? 14 : 16,
                    weight: 'bold'
                },
                padding: {
                    top: 10,
                    bottom: 10
                }
            },
            legend: {
                display: true,
                position: 'top',
                labels: {
                    boxWidth: isMobile ? 12 : 40,
                    font: {
                        size: isMobile ? 10 : 12
                    }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleFont: {
                    size: isMobile ? 12 : 14
                },
                bodyFont: {
                    size: isMobile ? 11 : 13
                },
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += context.parsed.y;
                        }
                        if (includeTime && context.label) {
                            label += ` (${context.label})`;
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: false,
                grid: {
                    color: 'rgba(200, 200, 200, 0.2)'
                },
                ticks: {
                    font: {
                        size: isMobile ? 10 : 12
                    },
                    padding: isMobile ? 5 : 8,
                    callback: function(value) {
                        return value;
                    }
                }
            },
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    font: {
                        size: isMobile ? 9 : 11
                    },
                    maxRotation: isMobile ? 45 : 30,
                    minRotation: isMobile ? 45 : 30,
                    autoSkip: true,
                    maxTicksLimit: isMobile ? 6 : 10
                }
            }
        }
    };
}

/**
 * Tạo hiệu ứng rung cho cảnh báo
 * @param {HTMLElement} element - Phần tử HTML cần tạo hiệu ứng
 */
function vibrateElement(element) {
    if (!element) return;
    
    // Thêm lớp rung
    element.classList.add('vibrate');
    
    // Kích hoạt rung trên thiết bị nếu có thể
    if (navigator.vibrate) {
        navigator.vibrate([100, 50, 100]);
    }
    
    // Xóa lớp rung sau 1 giây
    setTimeout(() => {
        element.classList.remove('vibrate');
    }, 1000);
}

/**
 * Kiểm tra xem ứng dụng có được cài đặt dưới dạng PWA hay không
 * @returns {boolean} - True nếu đang chạy dưới dạng PWA
 */
function isPWA() {
    return window.matchMedia('(display-mode: standalone)').matches || 
           window.navigator.standalone === true;
}

/**
 * Kiểm tra nếu thiết bị là thiết bị di động
 * @returns {boolean} - True nếu là thiết bị di động
 */
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || 
           window.innerWidth < 768;
}

// Thêm hiệu ứng rung cho CSS
if (!document.querySelector('#vibrate-style')) {
    const style = document.createElement('style');
    style.id = 'vibrate-style';
    style.textContent = `
        @keyframes vibrate {
            0% { transform: translate(0); }
            10% { transform: translate(-2px, -2px); }
            20% { transform: translate(2px, -2px); }
            30% { transform: translate(-2px, 2px); }
            40% { transform: translate(2px, 2px); }
            50% { transform: translate(-2px, -2px); }
            60% { transform: translate(2px, -2px); }
            70% { transform: translate(-2px, 2px); }
            80% { transform: translate(2px, 2px); }
            90% { transform: translate(-2px, -2px); }
            100% { transform: translate(0); }
        }
        .vibrate {
            animation: vibrate 0.5s linear;
        }
    `;
    document.head.appendChild(style);
}
