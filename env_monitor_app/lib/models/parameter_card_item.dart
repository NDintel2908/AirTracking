class ParameterCardItem {
  final String id;
  final String name;
  final double value;
  final String unit;
  final String status;
  final String statusText;
  final String timestamp;
  
  ParameterCardItem({
    required this.id,
    required this.name,
    required this.value,
    required this.unit,
    required this.status,
    required this.statusText,
    required this.timestamp,
  });
  
  factory ParameterCardItem.fromJson(String id, Map<String, dynamic> json) {
    // Xác định tên hiển thị
    String displayName;
    switch (id) {
      case 'temperature':
        displayName = 'Nhiệt độ';
        break;
      case 'humidity':
        displayName = 'Độ ẩm';
        break;
      case 'pm25':
        displayName = 'PM2.5';
        break;
      case 'pm10':
        displayName = 'PM10';
        break;
      case 'co':
        displayName = 'CO';
        break;
      case 'noise':
        displayName = 'Tiếng ồn';
        break;
      case 'aqi':
        displayName = 'AQI';
        break;
      default:
        displayName = id;
    }
    
    // Chuyển đổi trạng thái sang tiếng Việt
    String statusTextVi;
    switch (json['status']) {
      case 'normal':
        statusTextVi = 'Tốt';
        break;
      case 'warning':
        statusTextVi = 'Trung bình';
        break;
      case 'kém':
        statusTextVi = 'Kém';
        break;
      case 'danger':
        statusTextVi = 'Xấu';
        break;
      case 'rất xấu':
        statusTextVi = 'Rất xấu';
        break;
      case 'nguy hiểm':
        statusTextVi = 'Nguy hiểm';
        break;
      default:
        statusTextVi = json['status'] as String;
    }
    
    return ParameterCardItem(
      id: id,
      name: displayName,
      value: (json['value'] as num).toDouble(),
      unit: json['unit'] as String,
      status: json['status'] as String,
      statusText: statusTextVi,
      timestamp: json['timestamp'] as String,
    );
  }
  
  String get formattedValue {
    if (id == 'aqi') {
      return value.toInt().toString();
    } else if (id == 'pm25' || id == 'pm10' || id == 'co') {
      return value.toStringAsFixed(1);
    } else if (id == 'temperature') {
      return value.toStringAsFixed(1);
    } else if (id == 'humidity') {
      return value.toStringAsFixed(1);
    } else {
      return value.toStringAsFixed(1);
    }
  }
}