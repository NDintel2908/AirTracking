import requests
import time
from datetime import datetime, timedelta
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('thingsboard_client')

# Cấu hình ThingsBoard
import os

THINGSBOARD_CONFIG = {
    'url': 'https://demo.thingsboard.io',
    'dashboard_id': '0c0e97d0-bd24-11ef-af67-a38a7671daf5',
    'access_token': os.environ.get('THINGSBOARD_ACCESS_TOKEN', ''),
    'device_id': '66ae3560-bd24-11ef-af67-a38a7671daf5'
}

# Cache để lưu trữ dữ liệu lịch sử và tránh gọi API quá nhiều
_data_cache = {
    'current': {'data': None, 'timestamp': 0},
    'historical': {'data': None, 'timestamp': 0}
}

# Thời gian hết hạn cache (60 giây)
CACHE_EXPIRY = 60


def get_current_readings():
    """
    Lấy dữ liệu hiện tại từ ThingsBoard, sử dụng cache nếu có thể
    """
    # Kiểm tra xem cache có còn hiệu lực không
    current_time = time.time()
    if _data_cache['current']['data'] is not None and \
       (current_time - _data_cache['current']['timestamp']) < CACHE_EXPIRY:
        logger.info("Returning cached current data")
        return _data_cache['current']['data']
    
    # Không có cache hợp lệ, gọi API
    try:
        # Sử dụng token trực tiếp trong URL thay vì header
        url = f"{THINGSBOARD_CONFIG['url']}/api/plugins/telemetry/DEVICE/{THINGSBOARD_CONFIG['device_id']}/values/timeseries?token={THINGSBOARD_CONFIG['access_token']}"
        
        logger.info(f"Requesting current data from URL: {url}")
        response = requests.get(url)
        
        # Kiểm tra lỗi HTTP
        if response.status_code != 200:
            logger.error(f"HTTP error {response.status_code}: {response.text}")
            raise requests.exceptions.RequestException(f"HTTP error {response.status_code}")
        
        data = response.json()
        logger.info(f"Received current data from ThingsBoard: {data}")
        
        # Chuyển đổi dữ liệu sang định dạng của ứng dụng
        formatted_data = format_current_data(data)
        
        # Cập nhật cache
        _data_cache['current']['data'] = formatted_data
        _data_cache['current']['timestamp'] = current_time
        
        return formatted_data
    except Exception as e:
        logger.error(f"Error fetching current data from ThingsBoard: {str(e)}")
        # Nếu có lỗi và có cache cũ, trả về cache đó
        if _data_cache['current']['data'] is not None:
            logger.info("Returning stale cached data due to API error")
            return _data_cache['current']['data']
        
        # Nếu không có cache, tạo dữ liệu giả (tương tự như code cũ)
        from app import PARAM_RANGES, generate_reading, get_status
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        readings = {}
        
        for param, param_info in PARAM_RANGES.items():
            value = generate_reading(param_info)
            status = get_status(value, param_info)
            
            readings[param] = {
                "value": value,
                "unit": param_info["unit"],
                "status": status,
                "timestamp": timestamp
            }
        
        logger.info("Generated fallback data due to API error")
        return readings


def get_historical_data(hours=1):
    """
    Lấy dữ liệu lịch sử từ ThingsBoard, sử dụng cache nếu có thể
    """
    # Kiểm tra xem cache có còn hiệu lực không
    current_time = time.time()
    if _data_cache['historical']['data'] is not None and \
       (current_time - _data_cache['historical']['timestamp']) < CACHE_EXPIRY:
        logger.info("Returning cached historical data")
        return _data_cache['historical']['data']
    
    # Không có cache hợp lệ, gọi API
    try:
        end_ts = int(time.time() * 1000)  # Thời gian hiện tại tính bằng mili giây
        start_ts = end_ts - (hours * 60 * 60 * 1000)  # hours giờ trước
        
        # Sử dụng token trực tiếp trong URL thay vì header
        url = f"{THINGSBOARD_CONFIG['url']}/api/plugins/telemetry/DEVICE/{THINGSBOARD_CONFIG['device_id']}/values/timeseries?startTs={start_ts}&endTs={end_ts}&token={THINGSBOARD_CONFIG['access_token']}"
        
        logger.info(f"Requesting historical data from URL: {url}")
        response = requests.get(url)
        
        # Kiểm tra lỗi HTTP
        if response.status_code != 200:
            logger.error(f"HTTP error {response.status_code}: {response.text}")
            raise requests.exceptions.RequestException(f"HTTP error {response.status_code}")
        
        data = response.json()
        logger.info(f"Received historical data from ThingsBoard with {len(data.keys())} parameters")
        
        # Chuyển đổi dữ liệu sang định dạng của ứng dụng
        formatted_data = format_historical_data(data)
        
        # Cập nhật cache
        _data_cache['historical']['data'] = formatted_data
        _data_cache['historical']['timestamp'] = current_time
        
        return formatted_data
    except Exception as e:
        logger.error(f"Error fetching historical data from ThingsBoard: {str(e)}")
        # Nếu có lỗi và có cache cũ, trả về cache đó
        if _data_cache['historical']['data'] is not None:
            logger.info("Returning stale cached historical data due to API error")
            return _data_cache['historical']['data']
        
        # Nếu không có cache, tạo dữ liệu giả (tương tự như code cũ)
        from app import PARAM_RANGES, generate_reading
        
        now = datetime.now()
        data = {}
        
        for param in PARAM_RANGES:
            param_data = []
            for i in range(60):  # 60 data points (1 per minute for the last hour)
                time_point = now - timedelta(minutes=i)
                value = generate_reading(PARAM_RANGES[param])
                param_data.append({
                    "timestamp": time_point.strftime("%H:%M"),
                    "value": value
                })
            # Reverse to have chronological order
            data[param] = list(reversed(param_data))
        
        logger.info("Generated fallback historical data due to API error")
        return data


def format_current_data(data):
    """
    Chuyển đổi dữ liệu hiện tại từ ThingsBoard sang định dạng của ứng dụng
    """
    from app import PARAM_RANGES, get_status
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    readings = {}
    
    # Ánh xạ giữa tên tham số ThingsBoard và ứng dụng
    param_mapping = {
        'temperature': 'temperature',
        'humidity': 'humidity',
        'pm10': 'pm10',
        'pm25': 'pm25',
        'co': 'co',
        'co2': 'co2',
        'noise': 'noise'
    }
    
    # Chuyển đổi dữ liệu
    for tb_param, app_param in param_mapping.items():
        if tb_param in data and data[tb_param] and len(data[tb_param]) > 0:
            try:
                value = float(data[tb_param][0]['value'])
                param_info = PARAM_RANGES[app_param]
                status = get_status(value, param_info)
                
                readings[app_param] = {
                    "value": value,
                    "unit": param_info["unit"],
                    "status": status,
                    "timestamp": timestamp
                }
            except (KeyError, ValueError, IndexError) as e:
                logger.error(f"Error processing {tb_param} data: {str(e)}")
    
    # Nếu không có dữ liệu từ ThingsBoard, tạo dữ liệu giả cho các tham số còn thiếu
    from app import generate_reading
    
    for param, param_info in PARAM_RANGES.items():
        if param not in readings:
            value = generate_reading(param_info)
            status = get_status(value, param_info)
            
            readings[param] = {
                "value": value,
                "unit": param_info["unit"],
                "status": status,
                "timestamp": timestamp
            }
    
    return readings


def format_historical_data(data):
    """
    Chuyển đổi dữ liệu lịch sử từ ThingsBoard sang định dạng của ứng dụng
    """
    from app import PARAM_RANGES
    
    formatted_data = {}
    
    # Ánh xạ giữa tên tham số ThingsBoard và ứng dụng
    param_mapping = {
        'temperature': 'temperature',
        'humidity': 'humidity',
        'pm10': 'pm10',
        'pm25': 'pm25',
        'co': 'co',
        'co2': 'co2',
        'noise': 'noise'
    }
    
    # Chuyển đổi dữ liệu lịch sử
    for tb_param, app_param in param_mapping.items():
        if tb_param in data and data[tb_param]:
            try:
                param_data = []
                for item in data[tb_param]:
                    timestamp = datetime.fromtimestamp(item['ts'] / 1000).strftime("%H:%M")
                    value = float(item['value'])
                    
                    param_data.append({
                        "timestamp": timestamp,
                        "value": value
                    })
                
                # Sắp xếp theo thời gian tăng dần
                param_data.sort(key=lambda x: x['timestamp'])
                formatted_data[app_param] = param_data
            except (KeyError, ValueError) as e:
                logger.error(f"Error processing historical {tb_param} data: {str(e)}")
    
    # Tạo dữ liệu giả cho các tham số còn thiếu
    from app import generate_reading
    
    now = datetime.now()
    
    for param in PARAM_RANGES:
        if param not in formatted_data:
            param_data = []
            for i in range(60):  # 60 data points (1 per minute for the last hour)
                time_point = now - timedelta(minutes=i)
                value = generate_reading(PARAM_RANGES[param])
                param_data.append({
                    "timestamp": time_point.strftime("%H:%M"),
                    "value": value
                })
            # Reverse to have chronological order
            formatted_data[param] = list(reversed(param_data))
    
    return formatted_data


def test_connection():
    """
    Kiểm tra kết nối với ThingsBoard
    """
    try:
        # Sử dụng token trực tiếp trong URL thay vì header
        url = f"{THINGSBOARD_CONFIG['url']}/api/plugins/telemetry/DEVICE/{THINGSBOARD_CONFIG['device_id']}/values/timeseries?token={THINGSBOARD_CONFIG['access_token']}"
        
        logger.info(f"Testing connection to: {url}")
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"ThingsBoard connection test failed: HTTP {response.status_code}, Response: {response.text}")
            return False
        
        data = response.json()
        if not data:
            logger.warning("ThingsBoard connection successful but no data received")
            return True
        
        logger.info(f"ThingsBoard connection successful. Received data for {len(data.keys())} parameters")
        return True
    except Exception as e:
        logger.error(f"ThingsBoard connection test error: {str(e)}")
        return False