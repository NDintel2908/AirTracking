class HistoricalDataPoint {
  final String timestamp;
  final double value;

  HistoricalDataPoint({
    required this.timestamp,
    required this.value,
  });

  factory HistoricalDataPoint.fromJson(Map<String, dynamic> json) {
    return HistoricalDataPoint(
      timestamp: json['timestamp'] as String,
      value: json['value'] is int
          ? (json['value'] as int).toDouble()
          : json['value'] as double,
    );
  }
}

/// Map từ parameter ID sang danh sách các điểm dữ liệu lịch sử
typedef HistoricalData = Map<String, List<HistoricalDataPoint>>;

/// Hàm chuyển đổi từ JSON sang HistoricalData
HistoricalData parseHistoricalData(Map<String, dynamic> json) {
  final result = <String, List<HistoricalDataPoint>>{};
  
  json.forEach((key, value) {
    if (value is List) {
      result[key] = value
          .map((item) => HistoricalDataPoint.fromJson(item as Map<String, dynamic>))
          .toList();
    }
  });
  
  return result;
}