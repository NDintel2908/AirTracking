import paho.mqtt.client as mqtt
import json
import time
import logging
from datetime import datetime, timedelta
import os
import ssl
import requests

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('thingsboard_mqtt_client')

# Cấu hình ThingsBoard
THINGSBOARD_CONFIG = {
    'host': 'demo.thingsboard.io',
    'port': 443,  # HTTPS port for REST API
    'device_id': '66ae3560-bd24-11ef-af67-a38a7671daf5',
    'access_token': os.environ.get('THINGSBOARD_ACCESS_TOKEN', 'DATN'),
    'dashboard_id': '0c0e97d0-bd24-11ef-af67-a38a7671daf5'
}

# Cache để lưu trữ dữ liệu và tránh gọi MQTT quá nhiều
_data_cache = {
    'current': {'data': None, 'timestamp': 0},
    'historical': {'data': None, 'timestamp': 0}
}

# Phạm vi cục bộ cho các tham số
PARAM_RANGES = {
    "pm10": {"min": 0, "max": 150, "unit": "μg/m³", "warning": 50, "danger": 100},
    "pm25": {"min": 0, "max": 75, "unit": "μg/m³", "warning": 25, "danger": 50},
    "temperature": {"min": 15, "max": 35, "unit": "°C", "warning": 30, "danger": 33},
    "humidity": {"min": 20, "max": 90, "unit": "%", "warning": 70, "danger": 85},
    "noise": {"min": 30, "max": 100, "unit": "dB", "warning": 70, "danger": 85},
    "co": {"min": 0, "max": 50, "unit": "ppm", "warning": 25, "danger": 40},
    "co2": {"min": 300, "max": 2000, "unit": "ppm", "warning": 1000, "danger": 1500}
}

# Ánh xạ giữa tên tham số ThingsBoard và ứng dụng
PARAM_MAPPING = {
    'Temperature': 'temperature',
    'Humidity': 'humidity',
    'PM10': 'pm10',
    'PM2.5': 'pm25',
    'CO': 'co',
    'CO2': 'co2',
    'Sound': 'noise'
}

# Lưu trữ dữ liệu nhận được từ MQTT
mqtt_data_store = {
    'telemetry': {},
    'attributes': {},
    'connected': False,
    'last_received': 0
}

# Callback khi kết nối thành công đến MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to ThingsBoard MQTT broker")
        mqtt_data_store['connected'] = True
        
        # Đăng ký các topic cần thiết
        client.subscribe(f"v1/devices/me/attributes")  # Nhận các thuộc tính thiết bị
        client.subscribe(f"v1/devices/me/attributes/response/+")  # Phản hồi từ yêu cầu thuộc tính
        client.subscribe(f"v1/devices/me/telemetry")  # Nhận dữ liệu telemetry
        
        # Yêu cầu tất cả các thuộc tính
        request_id = int(time.time())
        client.publish("v1/devices/me/attributes/request/" + str(request_id), json.dumps({"clientKeys": "", "sharedKeys": ""}))
    else:
        logger.error(f"Failed to connect to ThingsBoard MQTT broker, return code: {rc}")
        mqtt_data_store['connected'] = False

# Callback khi mất kết nối
def on_disconnect(client, userdata, rc):
    logger.warning(f"Disconnected from ThingsBoard MQTT broker with code: {rc}")
    mqtt_data_store['connected'] = False

# Callback khi nhận được message
def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        logger.debug(f"Received message on topic {topic}: {payload}")
        
        # Cập nhật thời gian nhận dữ liệu gần nhất
        mqtt_data_store['last_received'] = time.time()
        
        # Xử lý dữ liệu telemetry
        if topic == "v1/devices/me/telemetry":
            for param, value in payload.items():
                if param not in mqtt_data_store['telemetry']:
                    mqtt_data_store['telemetry'][param] = []
                
                # Thêm timestamp vào dữ liệu
                data_point = {
                    "ts": int(time.time() * 1000),  # milliseconds
                    "value": value
                }
                
                # Giữ tối đa 100 điểm dữ liệu cho mỗi tham số
                mqtt_data_store['telemetry'][param] = [data_point] + mqtt_data_store['telemetry'][param][:99]
        
        # Xử lý dữ liệu attributes
        elif topic.startswith("v1/devices/me/attributes"):
            for key, value in payload.items():
                mqtt_data_store['attributes'][key] = value
    
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}")

# Khởi tạo MQTT client
mqtt_client = None

def initialize_mqtt_client():
    """
    Khởi tạo kết nối HTTP API với ThingsBoard thay vì MQTT
    Vì môi trường Replit không cho phép kết nối MQTT, chúng ta sẽ sử dụng HTTP API
    """
    try:
        # Sử dụng API truy cập thiết bị trực tiếp với token "DATN"
        token = "DATN"  # Sử dụng trực tiếp token mà không thông qua biến môi trường
        url = f"https://{THINGSBOARD_CONFIG['host']}/api/v1/{token}/telemetry"
        
        logger.info(f"Testing device HTTP API connection to ThingsBoard: {url}")
        
        # Gửi ping dữ liệu để kiểm tra kết nối
        ping_data = {
            "ping": True,
            "timestamp": int(time.time() * 1000)
        }
        
        response = requests.post(url, json=ping_data)
        
        if response.status_code == 200:
            mqtt_data_store['connected'] = True
            logger.info("Successfully connected to ThingsBoard device HTTP API")
            
            # Lấy dữ liệu hiện tại
            current_url = f"https://{THINGSBOARD_CONFIG['host']}/api/v1/{token}/attributes"
            attr_response = requests.get(current_url)
            
            if attr_response.status_code == 200:
                data = attr_response.json()
                logger.info(f"Received attributes from ThingsBoard: {data}")
                
                # Cập nhật thời gian nhận dữ liệu
                mqtt_data_store['last_received'] = time.time()
            
            return True
        else:
            logger.error(f"Failed to connect to ThingsBoard device HTTP API: HTTP {response.status_code}")
            mqtt_data_store['connected'] = False
            return False
    except Exception as e:
        logger.error(f"Error connecting to ThingsBoard device HTTP API: {e}")
        mqtt_data_store['connected'] = False
        return False

def stop_mqtt_client():
    """
    Function này được giữ lại để tương thích với mã nguồn cũ
    Không còn thực sự cần thiết vì chúng ta đã chuyển sang sử dụng HTTP API
    """
    logger.info("HTTP API client does not need to be stopped")

def _get_status(value, param_info):
    """Hàm nội bộ để xác định trạng thái dựa trên ngưỡng"""
    if value is None:
        return "unknown"
    if value >= param_info["danger"]:
        return "danger"
    elif value >= param_info["warning"]:
        return "warning"
    return "normal"

def get_current_readings():
    """
    Lấy dữ liệu hiện tại từ ThingsBoard HTTP API thông qua token thiết bị
    """
    # Kiểm tra xem cache có còn hiệu lực không (4 giây)
    current_time = time.time()
    if _data_cache['current']['data'] is not None and (current_time - _data_cache['current']['timestamp']) < 4:
        logger.info("Returning cached current data")
        return _data_cache['current']['data']
    
    try:
        # Sử dụng token trực tiếp
        token = "DATN"
        url = f"https://{THINGSBOARD_CONFIG['host']}/api/v1/{token}/telemetry"
        
        logger.info(f"Requesting current data from ThingsBoard device API: {url}")
        
        # Gửi lệnh ping để lấy dữ liệu hiện tại
        ping_data = {
            "ts": int(current_time * 1000),
            "values": {
                "ping": True,
                "requestData": True
            }
        }
        
        # Gửi ping để cập nhật dữ liệu mới nhất
        ping_response = requests.post(url, json=ping_data)
        
        if ping_response.status_code == 200:
            # Lấy dữ liệu hiện tại
            latest_url = f"https://{THINGSBOARD_CONFIG['host']}/api/v1/{token}/attributes"
            response = requests.get(latest_url)
            
            if response.status_code == 200:
                # Đánh dấu đã kết nối thành công
                mqtt_data_store['connected'] = True
                
                # Lấy dữ liệu
                data = response.json()
                logger.info(f"Received current data from ThingsBoard device API with {len(data.keys())} parameters")
                
                # Chuyển đổi định dạng dữ liệu
                telemetry_data = {}
                for key, value in data.get('client', {}).items():
                    if key in PARAM_MAPPING.keys() or key in PARAM_MAPPING.values():
                        telemetry_data[key] = [{
                            'ts': int(current_time * 1000),
                            'value': str(value)
                        }]
                
                # Nếu không có dữ liệu telemetry, thử lấy thêm từ shared attributes
                if len(telemetry_data) == 0:
                    for key, value in data.get('shared', {}).items():
                        if key in PARAM_MAPPING.keys() or key in PARAM_MAPPING.values():
                            telemetry_data[key] = [{
                                'ts': int(current_time * 1000),
                                'value': str(value)
                            }]
                
                # Chuyển đổi dữ liệu sang định dạng của ứng dụng
                formatted_data = format_current_data(telemetry_data)
                
                # Cập nhật cache
                _data_cache['current']['data'] = formatted_data
                _data_cache['current']['timestamp'] = current_time
                
                return formatted_data
            else:
                logger.error(f"Failed to get attributes from ThingsBoard device API: HTTP {response.status_code}")
        else:
            logger.error(f"Failed to ping ThingsBoard device API: HTTP {ping_response.status_code}")
        
        mqtt_data_store['connected'] = False
        
        # Nếu có cache cũ, trả về cache đó
        if _data_cache['current']['data'] is not None:
            logger.info("Returning stale cached data due to API error")
            return _data_cache['current']['data']
    
    except Exception as e:
        logger.error(f"Error getting current data from ThingsBoard device API: {e}")
        mqtt_data_store['connected'] = False
        
        # Nếu có lỗi và có cache cũ, trả về cache đó
        if _data_cache['current']['data'] is not None:
            logger.info("Returning stale cached data due to error")
            return _data_cache['current']['data']
    
    # Nếu không lấy được dữ liệu và không có cache, tạo dữ liệu trống
    current_time = datetime.now().strftime("%H:%M:%S")
    readings = {}
    
    for param, param_info in PARAM_RANGES.items():
        readings[param] = {
            "value": None,
            "unit": param_info["unit"],
            "status": "unknown",
            "timestamp": current_time,
            "message": "Không có dữ liệu"
        }
    
    # Thêm trạng thái thiết bị
    readings['device_status'] = "unknown"
    readings['last_data_timestamp'] = None
    
    return readings

def get_historical_data(hours=1):
    """
    Lấy dữ liệu lịch sử từ ThingsBoard HTTP API thông qua token thiết bị
    """
    # Kiểm tra xem cache có còn hiệu lực không (4 giây)
    current_time = time.time()
    if _data_cache['historical']['data'] is not None and (current_time - _data_cache['historical']['timestamp']) < 4:
        logger.info("Returning cached historical data")
        return _data_cache['historical']['data']
    
    try:
        # Sử dụng token trực tiếp
        token = "DATN"
        
        # Sử dụng API của thiết bị để lấy dữ liệu lịch sử
        end_ts = int(current_time * 1000)  # Thời gian hiện tại tính bằng mili giây
        start_ts = end_ts - (hours * 60 * 60 * 1000)  # hours giờ trước
        
        url = f"https://{THINGSBOARD_CONFIG['host']}/api/v1/{token}/telemetry?startTs={start_ts}&endTs={end_ts}"
        
        logger.info(f"Requesting historical data from ThingsBoard device API: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            # Đánh dấu đã kết nối thành công
            mqtt_data_store['connected'] = True
            
            # Lấy dữ liệu
            data = response.json()
            logger.info(f"Received historical data from ThingsBoard device API")
            
            # Cấu trúc lại dữ liệu để phù hợp với định dạng cần thiết
            telemetry_data = {}
            for record in data:
                ts = record.get('ts')
                for key, value in record.get('values', {}).items():
                    if key not in telemetry_data:
                        telemetry_data[key] = []
                    
                    telemetry_data[key].append({
                        'ts': ts,
                        'value': str(value)
                    })
            
            # Chuyển đổi dữ liệu
            formatted_data = format_historical_data(telemetry_data)
            
            # Cập nhật cache
            _data_cache['historical']['data'] = formatted_data
            _data_cache['historical']['timestamp'] = current_time
            
            return formatted_data
        else:
            logger.error(f"Failed to get historical data from ThingsBoard device API: HTTP {response.status_code}")
            mqtt_data_store['connected'] = False
            
            # Nếu có cache cũ, trả về cache đó
            if _data_cache['historical']['data'] is not None:
                logger.info("Returning stale cached historical data due to API error")
                return _data_cache['historical']['data']
    
    except Exception as e:
        logger.error(f"Error getting historical data from ThingsBoard device API: {e}")
        mqtt_data_store['connected'] = False
        
        # Nếu có lỗi và có cache cũ, trả về cache đó
        if _data_cache['historical']['data'] is not None:
            logger.info("Returning stale cached historical data due to error")
            return _data_cache['historical']['data']
    
    # Nếu không lấy được dữ liệu và không có cache, tạo dữ liệu với các điểm dữ liệu trống
    now = datetime.now()
    formatted_data = {}
    
    for param in PARAM_RANGES:
        param_data = []
        for i in range(60):  # 60 data points (1 per minute for the last hour)
            time_point = now - timedelta(minutes=i)
            param_data.append({
                "timestamp": time_point.strftime("%H:%M"),
                "value": None
            })
        # Đảo ngược để có thứ tự thời gian tăng dần
        formatted_data[param] = list(reversed(param_data))
    
    return formatted_data

def format_current_data(data):
    """
    Chuyển đổi dữ liệu hiện tại từ ThingsBoard MQTT sang định dạng của ứng dụng
    """
    # Lấy thời gian hiện tại
    current_time = datetime.now().strftime("%H:%M:%S")
    readings = {}
    device_status = "online"
    last_data_update = None
    
    # Chuyển đổi dữ liệu
    for tb_param, app_param in PARAM_MAPPING.items():
        if tb_param in data and data[tb_param] and len(data[tb_param]) > 0:
            try:
                ts = data[tb_param][0]['ts']
                # Lưu lại timestamp mới nhất
                if last_data_update is None or ts > last_data_update:
                    last_data_update = ts
                
                value = float(data[tb_param][0]['value'])
                param_info = PARAM_RANGES[app_param]
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
    for param, param_info in PARAM_RANGES.items():
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
    Chuyển đổi dữ liệu lịch sử từ ThingsBoard MQTT sang định dạng của ứng dụng
    """
    formatted_data = {}
    
    # Chuyển đổi dữ liệu lịch sử
    for tb_param, app_param in PARAM_MAPPING.items():
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
    
    # Thêm các tham số còn thiếu với dữ liệu trống
    now = datetime.now()
    
    for param in PARAM_RANGES:
        if param not in formatted_data:
            param_data = []
            for i in range(60):  # 60 data points (1 per minute for the last hour)
                time_point = now - timedelta(minutes=i)
                param_data.append({
                    "timestamp": time_point.strftime("%H:%M"),
                    "value": None
                })
            # Đảo ngược để có thứ tự thời gian tăng dần
            formatted_data[param] = list(reversed(param_data))
    
    return formatted_data

def test_connection():
    """
    Kiểm tra kết nối với ThingsBoard API thông qua token thiết bị
    """
    try:
        # Sử dụng token trực tiếp
        token = "DATN"
        
        # Kiểm tra kết nối bằng cách truy cập API thiết bị
        url = f"https://{THINGSBOARD_CONFIG['host']}/api/v1/{token}/attributes"
        
        logger.info(f"Testing device API connection to ThingsBoard: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            logger.info("ThingsBoard device API connection successful")
            # Đánh dấu đã kết nối thành công
            mqtt_data_store['connected'] = True
            return True
        else:
            logger.error(f"ThingsBoard device API connection failed: HTTP {response.status_code}")
            mqtt_data_store['connected'] = False
            return False
    except Exception as e:
        logger.error(f"Error testing ThingsBoard device API connection: {e}")
        mqtt_data_store['connected'] = False
        return False

# Khởi tạo kết nối HTTP API khi module được import
initialize_mqtt_client()