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
    'device_id': '66ae3560-bd24-11ef-af67-a38a7671daf5',
    'jwt_token': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyMDEzOTAwMkBzdHVkZW50LmhjbXV0ZS5lZHUudm4iLCJ1c2VySWQiOiI2MzdlMjA5MC1iZDIzLTExZWYtYWY2Ny1hMzhhNzY3MWRhZjUiLCJzY29wZXMiOlsiVEVOQU5UX0FETUlOIl0sInNlc3Npb25JZCI6ImU2NDI4YTdiLTVmNWYtNGY5Yi1hOThkLWZlMDJmMjFiNjMxNCIsImV4cCI6MTc0NzA0ODEwOCwiaXNzIjoidGhpbmdzYm9hcmQuaW8iLCJpYXQiOjE3NDUyNDgxMDgsImZpcnN0TmFtZSI6IlVFVCIsImxhc3ROYW1lIjoiVUVUIiwiZW5hYmxlZCI6dHJ1ZSwicHJpdmFjeVBvbGljeUFjY2VwdGVkIjp0cnVlLCJpc1B1YmxpYyI6ZmFsc2UsInRlbmFudElkIjoiNjE4YzYyYjAtYmQyMy0xMWVmLWFmNjctYTM4YTc2NzFkYWY1IiwiY3VzdG9tZXJJZCI6IjEzODE0MDAwLTFkZDItMTFiMi04MDgwLTgwODA4MDgwODA4MCJ9.EEEHbpy53WcvvxjDLwUV_xQaBXSNJgvINru2GEwjxAaGPToJtRP53mL7uYbYfNKvoRcCvZaKOVLImLT9ikmReg'
}

# Cache để lưu trữ dữ liệu lịch sử và tránh gọi API quá nhiều
_data_cache = {
    'current': {'data': None, 'timestamp': 0},
    'historical': {'data': None, 'timestamp': 0}
}

# Thời gian hết hạn cache (4 giây)
CACHE_EXPIRY = 4


def _generate_fallback_readings():
    """
    Tạo dữ liệu giả khi không thể kết nối với ThingsBoard
    """
    import random
    timestamp = datetime.now().strftime("%H:%M:%S")
    readings = {}
    
    # Dữ liệu phạm vi cho các tham số
    param_ranges = {
        "pm10": {"min": 0, "max": 150, "unit": "μg/m³", "warning": 50, "danger": 100},
        "pm25": {"min": 0, "max": 75, "unit": "μg/m³", "warning": 25, "danger": 50},
        "temperature": {"min": 15, "max": 35, "unit": "°C", "warning": 30, "danger": 33},
        "humidity": {"min": 20, "max": 90, "unit": "%", "warning": 70, "danger": 85},
        "noise": {"min": 30, "max": 100, "unit": "dB", "warning": 70, "danger": 85},
        "co": {"min": 0, "max": 50, "unit": "ppm", "warning": 25, "danger": 40},
        "co2": {"min": 300, "max": 2000, "unit": "ppm", "warning": 1000, "danger": 1500}
    }
    
    for param, param_info in param_ranges.items():
        value = round(random.uniform(param_info["min"], param_info["max"]), 1)
        
        # Xác định trạng thái
        if value >= param_info["danger"]:
            status = "danger"
        elif value >= param_info["warning"]:
            status = "warning"
        else:
            status = "normal"
        
        readings[param] = {
            "value": value,
            "unit": param_info["unit"],
            "status": status,
            "timestamp": timestamp
        }
    
    return readings

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
        # Sử dụng JWT token trong header thay vì token trong URL
        url = f"{THINGSBOARD_CONFIG['url']}/api/plugins/telemetry/DEVICE/{THINGSBOARD_CONFIG['device_id']}/values/timeseries"
        headers = {
            'X-Authorization': THINGSBOARD_CONFIG['jwt_token'],
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Requesting current data with JWT from URL: {url}")
        response = requests.get(url, headers=headers)
        
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
        
        # Nếu không có cache, tạo dữ liệu giả
        readings = _generate_fallback_readings()
        
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
        
        # Sử dụng JWT token trong header thay vì token trong URL
        url = f"{THINGSBOARD_CONFIG['url']}/api/plugins/telemetry/DEVICE/{THINGSBOARD_CONFIG['device_id']}/values/timeseries?startTs={start_ts}&endTs={end_ts}"
        headers = {
            'X-Authorization': THINGSBOARD_CONFIG['jwt_token'],
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Requesting historical data with JWT from URL: {url}")
        response = requests.get(url, headers=headers)
        
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


def _get_status(value, param_info):
    """Hàm nội bộ để xác định trạng thái dựa trên ngưỡng"""
    if value >= param_info["danger"]:
        return "danger"
    elif value >= param_info["warning"]:
        return "warning"
    return "normal"

def format_current_data(data):
    """
    Chuyển đổi dữ liệu hiện tại từ ThingsBoard sang định dạng của ứng dụng
    """
    # Sử dụng các phạm vi cục bộ thay vì import PARAM_RANGES từ app
    param_ranges = {
        "pm10": {"min": 0, "max": 150, "unit": "μg/m³", "warning": 50, "danger": 100},
        "pm25": {"min": 0, "max": 75, "unit": "μg/m³", "warning": 25, "danger": 50},
        "temperature": {"min": 15, "max": 35, "unit": "°C", "warning": 30, "danger": 33},
        "humidity": {"min": 20, "max": 90, "unit": "%", "warning": 70, "danger": 85},
        "noise": {"min": 30, "max": 100, "unit": "dB", "warning": 70, "danger": 85},
        "co": {"min": 0, "max": 50, "unit": "ppm", "warning": 25, "danger": 40},
        "co2": {"min": 300, "max": 2000, "unit": "ppm", "warning": 1000, "danger": 1500}
    }
    
    # Lấy thời gian hiện tại
    current_time = datetime.now().strftime("%H:%M:%S")
    readings = {}
    device_status = "online"
    last_data_update = None
    
    # Ánh xạ giữa tên tham số ThingsBoard và ứng dụng
    param_mapping = {
        'Temperature': 'temperature',
        'Humidity': 'humidity',
        'PM10': 'pm10',
        'PM2.5': 'pm25',
        'CO': 'co',
        'CO2': 'co2',
        'Sound': 'noise'
    }
    
    # Chuyển đổi dữ liệu
    for tb_param, app_param in param_mapping.items():
        if tb_param in data and data[tb_param] and len(data[tb_param]) > 0:
            try:
                ts = data[tb_param][0]['ts']
                # Lưu lại timestamp mới nhất
                if last_data_update is None or ts > last_data_update:
                    last_data_update = ts
                
                value = float(data[tb_param][0]['value'])
                param_info = param_ranges[app_param]
                status = _get_status(value, param_info)
                
                # Chuyển đổi timestamp của ThingsBoard sang định dạng giờ:phút:giây
                tb_timestamp = datetime.fromtimestamp(ts / 1000).strftime("%H:%M:%S")
                
                readings[app_param] = {
                    "value": value,
                    "unit": param_info["unit"],
                    "status": status,
                    "timestamp": tb_timestamp,
                    "last_update": ts
                }
            except (KeyError, ValueError, IndexError) as e:
                logger.error(f"Error processing {tb_param} data: {str(e)}")
    
    # Kiểm tra xem thiết bị có hoạt động không dựa trên thời gian dữ liệu mới nhất
    if last_data_update:
        # Tính thời gian trễ (phút) giữa thời gian hiện tại và thời gian cập nhật dữ liệu gần nhất
        current_ts = datetime.now().timestamp() * 1000  # Chuyển đổi sang milliseconds
        time_diff_minutes = (current_ts - last_data_update) / (1000 * 60)  # Chuyển đổi sang phút
        
        # Nếu dữ liệu không được cập nhật trong 15 phút, coi như thiết bị offline
        if time_diff_minutes > 15:
            device_status = "offline"
        # Nếu dữ liệu không được cập nhật trong 5 phút, coi như thiết bị không hoạt động
        elif time_diff_minutes > 5:
            device_status = "inactive"
    else:
        device_status = "unknown"
    
    # Thêm các tham số còn thiếu với thông báo không có dữ liệu
    for param, param_info in param_ranges.items():
        if param not in readings:
            readings[param] = {
                "value": None,
                "unit": param_info["unit"],
                "status": "unknown",
                "timestamp": current_time,
                "message": "Không có dữ liệu"
            }
            
    # Thêm trạng thái thiết bị vào kết quả
    readings['device_status'] = device_status
    readings['last_data_timestamp'] = last_data_update
    
    return readings


def format_historical_data(data):
    """
    Chuyển đổi dữ liệu lịch sử từ ThingsBoard sang định dạng của ứng dụng
    """
    # Sử dụng các phạm vi cục bộ thay vì import từ app
    param_ranges = {
        "pm10": {"min": 0, "max": 150, "unit": "μg/m³", "warning": 50, "danger": 100},
        "pm25": {"min": 0, "max": 75, "unit": "μg/m³", "warning": 25, "danger": 50},
        "temperature": {"min": 15, "max": 35, "unit": "°C", "warning": 30, "danger": 33},
        "humidity": {"min": 20, "max": 90, "unit": "%", "warning": 70, "danger": 85},
        "noise": {"min": 30, "max": 100, "unit": "dB", "warning": 70, "danger": 85},
        "co": {"min": 0, "max": 50, "unit": "ppm", "warning": 25, "danger": 40},
        "co2": {"min": 300, "max": 2000, "unit": "ppm", "warning": 1000, "danger": 1500}
    }
    
    formatted_data = {}
    
    # Ánh xạ giữa tên tham số ThingsBoard và ứng dụng
    param_mapping = {
        'Temperature': 'temperature',
        'Humidity': 'humidity',
        'PM10': 'pm10',
        'PM2.5': 'pm25',
        'CO': 'co',
        'CO2': 'co2',
        'Sound': 'noise'
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
    import random
    
    now = datetime.now()
    
    for param, param_info in param_ranges.items():
        if param not in formatted_data:
            param_data = []
            for i in range(60):  # 60 data points (1 per minute for the last hour)
                time_point = now - timedelta(minutes=i)
                value = round(random.uniform(param_info["min"], param_info["max"]), 1)
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
        # Sử dụng JWT token trong header thay vì token trong URL
        url = f"{THINGSBOARD_CONFIG['url']}/api/plugins/telemetry/DEVICE/{THINGSBOARD_CONFIG['device_id']}/values/timeseries"
        headers = {
            'X-Authorization': THINGSBOARD_CONFIG['jwt_token'],
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Testing connection to ThingsBoard with JWT token")
        response = requests.get(url, headers=headers)
        
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