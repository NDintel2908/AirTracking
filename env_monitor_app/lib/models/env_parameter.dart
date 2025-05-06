class EnvParameter {
  final double value;
  final String unit;
  final String status;
  final String timestamp;
  final int? lastUpdate;

  EnvParameter({
    required this.value,
    required this.unit,
    required this.status,
    required this.timestamp,
    this.lastUpdate,
  });

  factory EnvParameter.fromJson(Map<String, dynamic> json) {
    return EnvParameter(
      value: json['value'] is int 
          ? (json['value'] as int).toDouble() 
          : json['value'] as double,
      unit: json['unit'] as String,
      status: json['status'] as String,
      timestamp: json['timestamp'] as String,
      lastUpdate: json['last_update'] as int?,
    );
  }

  /// Lấy văn bản trạng thái hiển thị
  String getStatusText() {
    switch (status) {
      case 'normal':
        return 'Tốt';
      case 'warning':
        return 'Trung bình';
      case 'kém':
        return 'Kém';
      case 'danger':
        return 'Xấu';
      default:
        return 'Không xác định';
    }
  }

  /// Kiểm tra xem thông số có ở trạng thái nguy hiểm không
  bool isDanger() {
    return status == 'danger';
  }

  /// Kiểm tra xem thông số có ở trạng thái cảnh báo không
  bool isWarning() {
    return status == 'warning' || status == 'kém';
  }
}