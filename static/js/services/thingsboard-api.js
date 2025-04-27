/**
 * Module kết nối với ThingsBoard IoT Platform
 * Cung cấp các phương thức để truy xuất dữ liệu từ ThingsBoard
 */

// Cấu hình ThingsBoard
const THINGSBOARD_CONFIG = {
    url: 'https://demo.thingsboard.io',
    dashboardId: '0c0e97d0-bd24-11ef-af67-a38a7671daf5',
    accessToken: '024j84osb9p2p90b0ex6',
    deviceId: '66ae3560-bd24-11ef-af67-a38a7671daf5'
};

/**
 * Lấy dữ liệu hiện tại từ ThingsBoard
 * @returns {Promise} - Promise chứa dữ liệu mới nhất từ thiết bị
 */
async function getCurrentThingsboardData() {
    try {
        // Sử dụng URL API của ThingsBoard dựa trên ID thiết bị
        const url = `${THINGSBOARD_CONFIG.url}/api/plugins/telemetry/DEVICE/${THINGSBOARD_CONFIG.deviceId}/values/timeseries`;
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Authorization': `Bearer ${THINGSBOARD_CONFIG.accessToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`Không thể kết nối đến ThingsBoard: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Chuyển đổi dữ liệu từ ThingsBoard sang định dạng ứng dụng
        return formatThingsboardData(data);
    } catch (error) {
        console.error('Lỗi khi lấy dữ liệu từ ThingsBoard:', error);
        // Trả về null để biết rằng có lỗi xảy ra
        return null;
    }
}

/**
 * Lấy dữ liệu lịch sử từ ThingsBoard
 * @param {number} hours - Số giờ cần lấy dữ liệu lịch sử (mặc định: 1 giờ)
 * @returns {Promise} - Promise chứa dữ liệu lịch sử từ thiết bị
 */
async function getHistoricalThingsboardData(hours = 1) {
    try {
        // Tính toán khoảng thời gian
        const endTime = Date.now();
        const startTime = endTime - (hours * 60 * 60 * 1000); // Số milliseconds trong số giờ
        
        // Sử dụng URL API của ThingsBoard dựa trên ID thiết bị
        const url = `${THINGSBOARD_CONFIG.url}/api/plugins/telemetry/DEVICE/${THINGSBOARD_CONFIG.deviceId}/values/timeseries?startTs=${startTime}&endTs=${endTime}`;
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Authorization': `Bearer ${THINGSBOARD_CONFIG.accessToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`Không thể kết nối đến ThingsBoard: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Chuyển đổi dữ liệu lịch sử từ ThingsBoard sang định dạng ứng dụng
        return formatHistoricalData(data);
    } catch (error) {
        console.error('Lỗi khi lấy dữ liệu lịch sử từ ThingsBoard:', error);
        // Trả về null để biết rằng có lỗi xảy ra
        return null;
    }
}

/**
 * Chuyển đổi dữ liệu hiện tại từ ThingsBoard sang định dạng ứng dụng
 * @param {Object} data - Dữ liệu thô từ ThingsBoard
 * @returns {Object} - Dữ liệu đã được định dạng lại
 */
function formatThingsboardData(data) {
    // Ánh xạ tên thông số từ ThingsBoard sang ứng dụng
    const parameterMapping = {
        'temperature': 'temperature',
        'humidity': 'humidity',
        'pm10': 'pm10',
        'pm25': 'pm25',
        'co': 'co',
        'noise': 'noise'
    };
    
    // Xác định giới hạn cảnh báo và nguy hiểm
    // Sử dụng các giá trị giống như trong app.py
    const paramRanges = {
        "pm10": {"warning": 50, "danger": 100, "unit": "μg/m³"},
        "pm25": {"warning": 25, "danger": 50, "unit": "μg/m³"},
        "temperature": {"warning": 30, "danger": 33, "unit": "°C"},
        "humidity": {"warning": 70, "danger": 85, "unit": "%"},
        "noise": {"warning": 70, "danger": 85, "unit": "dB"},
        "co": {"warning": 25, "danger": 40, "unit": "ppm"},
        "aqi": {"warning": 100, "danger": 150, "unit": ""}
    };
    
    // Dữ liệu đã được định dạng
    const formattedData = {};
    const timestamp = new Date().toLocaleTimeString('vi-VN', {hour: '2-digit', minute:'2-digit', second:'2-digit'});
    
    // Lặp qua tất cả các thông số từ ThingsBoard
    for (const [tbParam, appParam] of Object.entries(parameterMapping)) {
        // Nếu có dữ liệu cho thông số này từ ThingsBoard
        if (data[tbParam] && data[tbParam][0]) {
            const value = parseFloat(data[tbParam][0].value);
            
            // Xác định trạng thái dựa trên giá trị và ngưỡng
            let status = 'normal';
            if (value >= paramRanges[appParam].danger) {
                status = 'danger';
            } else if (value >= paramRanges[appParam].warning) {
                status = 'warning';
            }
            
            // Tạo đối tượng dữ liệu cho thông số này
            formattedData[appParam] = {
                value: value,
                unit: paramRanges[appParam].unit,
                status: status,
                timestamp: timestamp
            };
        }
    }
    
    return formattedData;
}

/**
 * Chuyển đổi dữ liệu lịch sử từ ThingsBoard sang định dạng ứng dụng
 * @param {Object} data - Dữ liệu lịch sử thô từ ThingsBoard
 * @returns {Object} - Dữ liệu lịch sử đã được định dạng lại
 */
function formatHistoricalData(data) {
    // Ánh xạ tên thông số từ ThingsBoard sang ứng dụng
    const parameterMapping = {
        'temperature': 'temperature',
        'humidity': 'humidity',
        'pm10': 'pm10',
        'pm25': 'pm25',
        'co': 'co',
        'noise': 'noise'
    };
    
    // Dữ liệu lịch sử đã được định dạng
    const formattedData = {};
    
    // Lặp qua tất cả các thông số từ ThingsBoard
    for (const [tbParam, appParam] of Object.entries(parameterMapping)) {
        // Nếu có dữ liệu lịch sử cho thông số này từ ThingsBoard
        if (data[tbParam]) {
            // Tạo mảng dữ liệu lịch sử cho thông số này
            formattedData[appParam] = data[tbParam].map(item => {
                return {
                    timestamp: new Date(item.ts).toLocaleTimeString('vi-VN', {hour: '2-digit', minute:'2-digit'}),
                    value: parseFloat(item.value)
                };
            });
            
            // Sắp xếp dữ liệu theo thời gian tăng dần
            formattedData[appParam].sort((a, b) => {
                return new Date(a.timestamp) - new Date(b.timestamp);
            });
        } else {
            // Nếu không có dữ liệu cho thông số này, trả về mảng rỗng
            formattedData[appParam] = [];
        }
    }
    
    return formattedData;
}

/**
 * Kiểm tra kết nối đến ThingsBoard
 * @returns {Promise<boolean>} - True nếu kết nối thành công, ngược lại là False
 */
async function testThingsboardConnection() {
    try {
        const url = `${THINGSBOARD_CONFIG.url}/api/plugins/telemetry/DEVICE/${THINGSBOARD_CONFIG.deviceId}/values/timeseries`;
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Authorization': `Bearer ${THINGSBOARD_CONFIG.accessToken}`
            }
        });
        
        if (!response.ok) {
            console.error(`Kiểm tra kết nối ThingsBoard thất bại: ${response.status}`);
            return false;
        }
        
        const data = await response.json();
        if (Object.keys(data).length > 0) {
            console.log('Kết nối ThingsBoard thành công:', data);
            return true;
        } else {
            console.warn('Kết nối ThingsBoard thành công nhưng không nhận được dữ liệu');
            return false;
        }
    } catch (error) {
        console.error('Lỗi khi kiểm tra kết nối ThingsBoard:', error);
        return false;
    }
}

// Xuất các hàm để có thể sử dụng từ các module khác
export {
    getCurrentThingsboardData,
    getHistoricalThingsboardData,
    testThingsboardConnection,
    THINGSBOARD_CONFIG
};