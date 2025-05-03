import eventlet
# Đặt monkey_patch trước tiên
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import random
import time
from datetime import datetime, timedelta
import os
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('app')

app = Flask(__name__)
# Cấu hình SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Data ranges for each environmental parameter
PARAM_RANGES = {
    "pm10": {"min": 0, "max": 150, "unit": "μg/m³", "warning": 50, "danger": 100},
    "pm25": {"min": 0, "max": 75, "unit": "μg/m³", "warning": 25, "danger": 50},
    "temperature": {"min": 15, "max": 40, "unit": "°C", "warning": 35, "danger": 40},
    "humidity": {"min": 20, "max": 90, "unit": "%", "warning": 70, "danger": 85},
    "noise": {"min": 30, "max": 100, "unit": "dB", "warning": 70, "danger": 85},
    "co": {"min": 0, "max": 50, "unit": "ppm", "warning": 25, "danger": 40},
    "aqi": {"min": 0, "max": 300, "unit": "", "warning": 100, "danger": 150}
}

# Cache to store historical data (sẽ được sử dụng nếu không thể kết nối với ThingsBoard)
historical_data = {param: [] for param in PARAM_RANGES}

# Kiểm tra xem có nên sử dụng ThingsBoard hay không
USE_THINGSBOARD = True

def generate_reading(param_info):
    """Generate a realistic reading for the given parameter"""
    return round(random.uniform(param_info["min"], param_info["max"]), 1)

def get_status(value, param_info):
    """Determine status based on thresholds"""
    if value >= param_info["danger"]:
        return "danger"
    elif value >= param_info["warning"]:
        return "warning"
    return "normal"

def get_current_readings():
    """Get current readings for all parameters, either from ThingsBoard or generated"""
    if USE_THINGSBOARD:
        try:
            # Import khi cần thiết để tránh circular imports
            import thingsboard_client
            return thingsboard_client.get_current_readings()
        except Exception as e:
            logger.error(f"Error getting data from ThingsBoard: {str(e)}")
            logger.info("Falling back to generated data")
    
    # Nếu không dùng ThingsBoard hoặc có lỗi, tạo dữ liệu giả
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
        
        # Store in historical data (limit to 100 data points)
        historical_data[param].append({
            "value": value,
            "timestamp": timestamp
        })
        if len(historical_data[param]) > 100:
            historical_data[param].pop(0)
    
    return readings

def get_historical_data(hours=1):
    """Get historical data for charts, either from ThingsBoard or generated"""
    if USE_THINGSBOARD:
        try:
            # Import khi cần thiết để tránh circular imports
            import thingsboard_client
            return thingsboard_client.get_historical_data(hours)
        except Exception as e:
            logger.error(f"Error getting historical data from ThingsBoard: {str(e)}")
            logger.info("Falling back to generated historical data")
    
    # Nếu không dùng ThingsBoard hoặc có lỗi, tạo dữ liệu giả
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
    
    return data

@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html', parameters=PARAM_RANGES)

@app.route('/parameter/<param_name>')
def parameter_detail(param_name):
    """Render the detailed view for a specific parameter"""
    if param_name not in PARAM_RANGES:
        return "Parameter not found", 404
    
    param_info = PARAM_RANGES[param_name]
    param_info["name"] = param_name
    return render_template('parameter.html', parameter=param_info)

@app.route('/api/current')
def api_current():
    """API endpoint for current readings"""
    return jsonify(get_current_readings())

@app.route('/api/historical')
def api_historical():
    """API endpoint for historical data"""
    return jsonify(get_historical_data())

@app.route('/api/historical/<param_name>')
def api_param_historical(param_name):
    """API endpoint for historical data of a specific parameter"""
    if param_name not in PARAM_RANGES:
        return jsonify({"error": "Parameter not found"}), 404
    
    history = get_historical_data()
    return jsonify(history[param_name])

@app.route('/api/status')
def api_status():
    """API endpoint for ThingsBoard connection status"""
    try:
        import thingsboard_mqtt_client
        import thingsboard_client
        
        # Thử kết nối bằng cả hai cách
        mqtt_status = thingsboard_mqtt_client.test_connection()
        jwt_status = thingsboard_client.test_connection()
        
        # Nếu một trong hai kết nối thành công thì coi như kết nối được
        connection_status = mqtt_status or jwt_status
        
        return jsonify({
            "thingsboard_connected": connection_status,
            "device_id": thingsboard_mqtt_client.THINGSBOARD_CONFIG['device_id'],
            "dashboard_url": f"https://{thingsboard_mqtt_client.THINGSBOARD_CONFIG['host']}/dashboards/0c0e97d0-bd24-11ef-af67-a38a7671daf5",
            "data_source": "ThingsBoard API" if connection_status else "Dữ liệu giả lập"
        })
    except Exception as e:
        logger.error(f"Error checking ThingsBoard status: {str(e)}")
        return jsonify({
            "thingsboard_connected": False,
            "error": str(e),
            "data_source": "Dữ liệu giả lập"
        })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
