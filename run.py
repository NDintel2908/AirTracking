import os
from app import app

if __name__ == "__main__":
    # Đảm bảo chạy trên cổng 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)