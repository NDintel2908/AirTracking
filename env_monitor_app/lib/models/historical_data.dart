class HistoricalData {
  final Map<String, List<HistoricalDataPoint>> data;
  
  HistoricalData({
    required this.data,
  });
  
  // Lấy dữ liệu lịch sử cho một thông số cụ thể
  List<HistoricalDataPoint> getParameterData(String paramName) {
    return data[paramName] ?? [];
  }
  
  // Lấy danh sách thời gian (timestamp) chung
  List<String> getTimeLabels() {
    if (data.isEmpty) return [];
    
    // Lấy timestamp từ thông số đầu tiên (nếu có)
    final firstParam = data.keys.first;
    final points = data[firstParam] ?? [];
    
    return points.map((point) => point.timestamp).toList();
  }
}

class HistoricalDataPoint {
  final double value;
  final String timestamp;
  final String status;
  
  HistoricalDataPoint({
    required this.value,
    required this.timestamp,
    required this.status,
  });
  
  factory HistoricalDataPoint.fromJson(Map<String, dynamic> json) {
    return HistoricalDataPoint(
      value: (json['value'] as num).toDouble(),
      timestamp: json['timestamp'] as String,
      status: json['status'] as String? ?? 'normal',
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'value': value,
      'timestamp': timestamp,
      'status': status,
    };
  }
}

// Hàm phân tích dữ liệu lịch sử từ API
HistoricalData parseHistoricalData(Map<String, dynamic> json) {
  final Map<String, List<HistoricalDataPoint>> data = {};
  
  json.forEach((key, value) {
    if (value is List) {
      data[key] = value
          .map((item) => HistoricalDataPoint.fromJson(item as Map<String, dynamic>))
          .toList();
    }
  });
  
  return HistoricalData(data: data);
}