import 'parameter_card_item.dart';
import 'device_status.dart';

class CurrentData {
  final Map<String, dynamic> data;
  final String timestamp;
  
  CurrentData({
    required this.data,
    required this.timestamp,
  });
  
  factory CurrentData.fromJson(Map<String, dynamic> json) {
    return CurrentData(
      data: json['data'] as Map<String, dynamic>,
      timestamp: json['timestamp'].toString(),
    );
  }
  
  List<ParameterCardItem> toParameterList() {
    final List<ParameterCardItem> result = [];
    
    // Các thông số có trong data
    if (data.containsKey('temperature')) {
      result.add(ParameterCardItem.fromJson('temperature', data['temperature'] as Map<String, dynamic>));
    }
    
    if (data.containsKey('humidity')) {
      result.add(ParameterCardItem.fromJson('humidity', data['humidity'] as Map<String, dynamic>));
    }
    
    if (data.containsKey('pm25')) {
      result.add(ParameterCardItem.fromJson('pm25', data['pm25'] as Map<String, dynamic>));
    }
    
    if (data.containsKey('pm10')) {
      result.add(ParameterCardItem.fromJson('pm10', data['pm10'] as Map<String, dynamic>));
    }
    
    if (data.containsKey('co')) {
      result.add(ParameterCardItem.fromJson('co', data['co'] as Map<String, dynamic>));
    }
    
    if (data.containsKey('noise')) {
      result.add(ParameterCardItem.fromJson('noise', data['noise'] as Map<String, dynamic>));
    }
    
    if (data.containsKey('aqi')) {
      result.add(ParameterCardItem.fromJson('aqi', data['aqi'] as Map<String, dynamic>));
    }
    
    return result;
  }
  
  DeviceStatus getDeviceStatusObject() {
    return DeviceStatus(
      status: data.containsKey('device_status') ? data['device_status'] as String : 'unknown',
      lastDataTimestamp: data.containsKey('last_data_timestamp') 
          ? (data['last_data_timestamp'] as num).toInt()
          : 0,
    );
  }
  
  bool isDeviceOnline() {
    return data.containsKey('device_status') && data['device_status'] == 'online';
  }
}