import 'package:intl/intl.dart';

class DeviceStatus {
  final String status;
  final int lastDataTimestamp;
  
  DeviceStatus({
    required this.status,
    required this.lastDataTimestamp,
  });
  
  bool get isOnline => status == 'online';
  
  String getStatusMessage() {
    return isOnline ? 'Thiết bị đang hoạt động' : 'Thiết bị mất kết nối';
  }
  
  String getLastUpdateText() {
    if (lastDataTimestamp == 0) {
      return 'Chưa có dữ liệu';
    }
    
    final DateTime time = DateTime.fromMillisecondsSinceEpoch(lastDataTimestamp);
    final DateFormat formatter = DateFormat('HH:mm:ss dd/MM/yyyy');
    final String formatted = formatter.format(time);
    return 'Cập nhật cuối: $formatted';
  }
  
  Duration getTimeSinceLastUpdate() {
    if (lastDataTimestamp == 0) {
      return const Duration(days: 999); // Giá trị lớn để chỉ chưa bao giờ cập nhật
    }
    
    final DateTime time = DateTime.fromMillisecondsSinceEpoch(lastDataTimestamp);
    final DateTime now = DateTime.now();
    return now.difference(time);
  }
  
  String getTimeSinceLastUpdateFormatted() {
    final Duration diff = getTimeSinceLastUpdate();
    
    if (diff.inDays > 1) {
      return '${diff.inDays} ngày trước';
    } else if (diff.inHours > 0) {
      return '${diff.inHours} giờ trước';
    } else if (diff.inMinutes > 0) {
      return '${diff.inMinutes} phút trước';
    } else {
      return '${diff.inSeconds} giây trước';
    }
  }
}