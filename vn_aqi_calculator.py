#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chương trình tính chỉ số chất lượng không khí VN_AQI theo thời gian thực
dựa trên Quyết định 1459/QĐ-TCMT của Việt Nam.

Tính toán AQI cho PM2.5, PM10, và CO từ dữ liệu cảm biến tức thời.
"""

import time
import random
import math
from datetime import datetime
from colorama import init, Fore, Style, Back

# Khởi tạo colorama
init(autoreset=True)

# Bảng quy chuẩn VN_AQI cho PM2.5 (μg/m³), dùng cho dữ liệu tức thời thay vì trung bình 24h
PM25_BREAKPOINTS = [
    {"c_low": 0, "c_high": 12, "i_low": 0, "i_high": 50},
    {"c_low": 12.1, "c_high": 35.4, "i_low": 51, "i_high": 100},
    {"c_low": 35.5, "c_high": 55.4, "i_low": 101, "i_high": 150},
    {"c_low": 55.5, "c_high": 150.4, "i_low": 151, "i_high": 200},
    {"c_low": 150.5, "c_high": 250.4, "i_low": 201, "i_high": 300},
    {"c_low": 250.5, "c_high": 350.4, "i_low": 301, "i_high": 400},
    {"c_low": 350.5, "c_high": 500.4, "i_low": 401, "i_high": 500}
]

# Bảng quy chuẩn VN_AQI cho PM10 (μg/m³), dùng cho dữ liệu tức thời thay vì trung bình 24h
PM10_BREAKPOINTS = [
    {"c_low": 0, "c_high": 54, "i_low": 0, "i_high": 50},
    {"c_low": 55, "c_high": 154, "i_low": 51, "i_high": 100},
    {"c_low": 155, "c_high": 254, "i_low": 101, "i_high": 150},
    {"c_low": 255, "c_high": 354, "i_low": 151, "i_high": 200},
    {"c_low": 355, "c_high": 424, "i_low": 201, "i_high": 300},
    {"c_low": 425, "c_high": 504, "i_low": 301, "i_high": 400},
    {"c_low": 505, "c_high": 604, "i_low": 401, "i_high": 500}
]

# Bảng quy chuẩn VN_AQI cho CO (mg/m³), dùng cho dữ liệu tức thời thay vì trung bình 8h
# Lưu ý: Đầu vào của CO được chuyển đổi từ ppm sang mg/m³
CO_BREAKPOINTS = [
    {"c_low": 0, "c_high": 10, "i_low": 0, "i_high": 50},
    {"c_low": 10.1, "c_high": 30, "i_low": 51, "i_high": 100},
    {"c_low": 30.1, "c_high": 45, "i_low": 101, "i_high": 150},
    {"c_low": 45.1, "c_high": 60, "i_low": 151, "i_high": 200},
    {"c_low": 60.1, "c_high": 90, "i_low": 201, "i_high": 300},
    {"c_low": 90.1, "c_high": 120, "i_low": 301, "i_high": 400},
    {"c_low": 120.1, "c_high": 150, "i_low": 401, "i_high": 500}
]

# Màu sắc và mô tả cho các mức AQI
AQI_LEVELS = [
    {"range": (0, 50), "color": Fore.GREEN, "bg": Back.GREEN, "label": "TỐT", "description": "Chất lượng không khí tốt"},
    {"range": (51, 100), "color": Fore.YELLOW, "bg": Back.YELLOW, "label": "TRUNG BÌNH", "description": "Chất lượng không khí trung bình"},
    {"range": (101, 150), "color": Fore.LIGHTYELLOW_EX, "bg": Back.LIGHTYELLOW_EX, "label": "KÉM", "description": "Nhóm nhạy cảm nên hạn chế thời gian ở ngoài trời"},
    {"range": (151, 200), "color": Fore.RED, "bg": Back.RED, "label": "XẤU", "description": "Nhóm nhạy cảm nên hạn chế ra ngoài"},
    {"range": (201, 300), "color": Fore.MAGENTA, "bg": Back.MAGENTA, "label": "RẤT XẤU", "description": "Nhóm nhạy cảm tránh ra ngoài trời"},
    {"range": (301, 500), "color": Fore.WHITE + Back.RED, "bg": Back.RED, "label": "NGUY HIỂM", "description": "Mọi người nên ở trong nhà"}
]

def get_aqi_level(aqi):
    """Trả về thông tin mức độ AQI dựa trên giá trị AQI"""
    for level in AQI_LEVELS:
        if level["range"][0] <= aqi <= level["range"][1]:
            return level
    return AQI_LEVELS[-1]  # Mặc định trả về mức nguy hiểm nếu vượt quá phạm vi

def calculate_iaqi(concentration, breakpoints):
    """Tính IAQI cho một thông số ô nhiễm cụ thể"""
    # Xử lý trường hợp không có dữ liệu
    if concentration is None or math.isnan(concentration):
        return None
    
    # Tìm điểm ngắt phù hợp
    for bp in breakpoints:
        if bp["c_low"] <= concentration <= bp["c_high"]:
            # Áp dụng công thức tính IAQI
            iaqi = ((bp["i_high"] - bp["i_low"]) / (bp["c_high"] - bp["c_low"])) * (concentration - bp["c_low"]) + bp["i_low"]
            return round(iaqi)
    
    # Nếu nồng độ vượt quá giới hạn cao nhất
    if concentration > breakpoints[-1]["c_high"]:
        return breakpoints[-1]["i_high"]
    
    # Nếu nồng độ thấp hơn giới hạn thấp nhất
    return breakpoints[0]["i_low"]

def convert_ppm_to_mgm3(ppm, molecular_weight=28.01, temperature=25, pressure=1):
    """
    Chuyển đổi từ ppm sang mg/m³ cho CO
    Sử dụng công thức: mg/m³ = (ppm × MW) ÷ (R × T)
    Trong đó MW là khối lượng phân tử (g/mol), R là hằng số khí lý tưởng,
    T là nhiệt độ tuyệt đối (K)
    
    Đơn giản hóa công thức cho CO ở điều kiện tiêu chuẩn:
    1 ppm CO ≈ 1.145 mg/m³
    """
    return ppm * 1.145

def generate_random_sensor_data():
    """Tạo dữ liệu ngẫu nhiên từ cảm biến để mô phỏng đọc dữ liệu thời gian thực"""
    # Các giá trị mô phỏng thực tế cho Việt Nam
    pm25 = random.uniform(5, 80)  # μg/m³
    pm10 = random.uniform(10, 120)  # μg/m³
    co_ppm = random.uniform(0.5, 15)  # ppm
    
    # Chuyển đổi CO từ ppm sang mg/m³
    co_mgm3 = convert_ppm_to_mgm3(co_ppm)
    
    return {
        "pm25": round(pm25, 1),
        "pm10": round(pm10, 1),
        "co_ppm": round(co_ppm, 2),
        "co_mgm3": round(co_mgm3, 2)
    }

def calculate_vn_aqi(sensor_data):
    """Tính chỉ số VN_AQI từ dữ liệu cảm biến"""
    # Tính IAQI cho từng thông số
    iaqi_pm25 = calculate_iaqi(sensor_data["pm25"], PM25_BREAKPOINTS)
    iaqi_pm10 = calculate_iaqi(sensor_data["pm10"], PM10_BREAKPOINTS)
    iaqi_co = calculate_iaqi(sensor_data["co_mgm3"], CO_BREAKPOINTS)
    
    # Lưu IAQI cho từng thông số để hiển thị
    iaqi_values = {
        "PM2.5": iaqi_pm25,
        "PM10": iaqi_pm10,
        "CO": iaqi_co
    }
    
    # Chỉ số AQI là giá trị lớn nhất của các IAQI
    valid_iaqis = [iaqi for iaqi in [iaqi_pm25, iaqi_pm10, iaqi_co] if iaqi is not None]
    
    if not valid_iaqis:
        return None, iaqi_values
    
    aqi = max(valid_iaqis)
    return aqi, iaqi_values

def display_aqi_info(aqi, iaqi_values, sensor_data):
    """Hiển thị thông tin AQI với màu sắc tương ứng"""
    aqi_level = get_aqi_level(aqi)
    
    # In thời gian hiện tại
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"\n{Style.BRIGHT}[{current_time}] Đang theo dõi chất lượng không khí theo thời gian thực...")
    
    # In thông tin dữ liệu đo từ cảm biến
    print(f"\n{Style.BRIGHT}Dữ liệu cảm biến:")
    print(f"  PM2.5: {sensor_data['pm25']} μg/m³")
    print(f"  PM10: {sensor_data['pm10']} μg/m³")
    print(f"  CO: {sensor_data['co_ppm']} ppm ({sensor_data['co_mgm3']} mg/m³)")
    
    # In chỉ số IAQI của từng tham số
    print(f"\n{Style.BRIGHT}Chỉ số IAQI cho từng thông số:")
    for param, value in iaqi_values.items():
        if value is not None:
            param_level = get_aqi_level(value)
            print(f"  {param}: {param_level['color']}{value} - {param_level['label']}")
    
    # In chỉ số AQI tổng hợp
    print(f"\n{Style.BRIGHT}Chỉ số AQI tổng hợp:")
    print(f"  {aqi_level['color']}{Style.BRIGHT}{aqi} - {aqi_level['label']}")
    print(f"  {aqi_level['color']}{aqi_level['description']}")
    
    # Hiển thị thanh trạng thái màu
    print(f"\n{Style.BRIGHT}Thang đo AQI:")
    bar_length = 50
    for level in AQI_LEVELS:
        level_range = level["range"][1] - level["range"][0]
        segment_length = int((level_range / 500) * bar_length)
        if segment_length < 1:
            segment_length = 1
        print(f"{level['bg']}{'':>{segment_length}}", end="")
    print(Style.RESET_ALL)
    
    # Vị trí con trỏ trong thanh trạng thái
    position = int((aqi / 500) * bar_length)
    pointer = " " * position + "▲"
    print(f"{pointer:>{bar_length+1}}")
    
    # In ghi chú về các mức AQI
    print(f"\n{Style.BRIGHT}Mức độ chất lượng không khí:")
    for level in AQI_LEVELS:
        print(f"  {level['color']}{level['range'][0]}-{level['range'][1]}: {level['label']} - {level['description']}")

# Sử dụng file để lưu trữ giá trị AQI mới nhất
def save_current_aqi(aqi_value, aqi_status):
    """Lưu giá trị AQI và trạng thái vào file để chia sẻ giữa các processes"""
    try:
        with open('current_aqi.txt', 'w') as f:
            f.write(f"{aqi_value}\n{aqi_status}")
        print(f"Đã lưu AQI: {aqi_value}, trạng thái: {aqi_status}")
    except Exception as e:
        print(f"Lỗi khi lưu AQI: {e}")

def get_current_aqi():
    """Đọc chỉ số AQI hiện tại và trạng thái từ file"""
    try:
        with open('current_aqi.txt', 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                aqi_value = float(lines[0].strip())
                aqi_status = lines[1].strip()
                return aqi_value, aqi_status
            return None, None
    except Exception as e:
        print(f"Lỗi khi đọc AQI: {e}")
        return None, None

def main():
    """Hàm chính thực hiện tính toán và hiển thị AQI theo thời gian thực"""
    print(f"{Style.BRIGHT}{Fore.CYAN}Bắt đầu chương trình tính chỉ số chất lượng không khí VN_AQI...")
    print(f"{Style.BRIGHT}{Fore.CYAN}Theo Quyết định 1459/QĐ-TCMT của Việt Nam\n")
    print(f"{Fore.YELLOW}Nhấn Ctrl+C để dừng chương trình\n")
    
    try:
        while True:
            # Mô phỏng đọc dữ liệu cảm biến
            sensor_data = generate_random_sensor_data()
            
            # Tính chỉ số AQI
            aqi, iaqi_values = calculate_vn_aqi(sensor_data)
            
            # Xác định trạng thái AQI
            if aqi is not None:
                aqi_level = get_aqi_level(aqi)
                aqi_status = aqi_level["label"].lower()  # Chuyển thành chữ thường để phù hợp với các trạng thái khác
                
                # Chuyển đổi trạng thái cho phù hợp với định dạng ứng dụng (normal, warning, danger)
                if aqi_status in ["tốt"]:
                    aqi_status = "normal"
                elif aqi_status in ["trung bình", "kém"]:
                    aqi_status = "warning"
                elif aqi_status in ["xấu", "rất xấu", "nguy hiểm"]:
                    aqi_status = "danger"
                
                # Lưu giá trị AQI và trạng thái vào file để chia sẻ với EnvMonitor
                save_current_aqi(aqi, aqi_status)
                
                # Hiển thị thông tin AQI
                display_aqi_info(aqi, iaqi_values, sensor_data)
            else:
                # Lưu giá trị AQI không xác định
                save_current_aqi(None, "unknown")
                print(f"\n{Fore.RED}Không thể tính AQI: Thiếu dữ liệu cảm biến!")
            
            # Chờ 5 giây trước khi cập nhật tiếp
            time.sleep(5)
    except KeyboardInterrupt:
        print(f"\n\n{Style.BRIGHT}{Fore.CYAN}Kết thúc chương trình tính chỉ số chất lượng không khí.")

if __name__ == "__main__":
    main()