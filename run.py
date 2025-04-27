import os
import time
import threading
import logging
from app import app, socketio
import thingsboard_client as tb_jwt

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('run')

# Hàm gửi dữ liệu cập nhật qua SocketIO
def send_updates():
    """
    Gửi cập nhật dữ liệu theo thời gian thực qua SocketIO
    """
    print("Bắt đầu luồng cập nhật dữ liệu thời gian thực...")
    
    while True:
        try:
            # Lấy dữ liệu hiện tại từ JWT client
            data = tb_jwt.get_current_readings()
            
            # Gửi dữ liệu qua SocketIO
            socketio.emit('data_update', {'data': data, 'timestamp': time.time()})
            
            # Kiểm tra trạng thái kết nối ThingsBoard
            tb_status = tb_jwt.test_connection()   
            socketio.emit('thingsboard_status', {'connected': tb_status})
            
            # Đợi 5 giây trước khi cập nhật tiếp
            time.sleep(5)
        except Exception as e:
            logger.error(f"Lỗi khi gửi cập nhật: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    # Đảm bảo chạy trên cổng 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Bắt đầu luồng cập nhật dữ liệu
    update_thread = threading.Thread(target=send_updates)
    update_thread.daemon = True
    update_thread.start()
    
    # Chạy ứng dụng với socketio thay vì app.run
    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False, log_output=True)