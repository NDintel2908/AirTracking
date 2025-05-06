import 'dart:convert';
import 'package:http/http.dart' as http;

import '../models/current_data.dart';
import '../models/historical_data.dart';

class ApiService {
  // API base URL - sử dụng URL của Replit hoặc server của bạn
  // Lưu ý: URL này cần được thay đổi khi triển khai
  static const String baseUrl = 'https://a7dc8ca9-0605-486f-b306-92aeef424639-00-2jq9zk4avsodf.janeway.replit.dev:5000';
  
  // Singleton instance
  static final ApiService _instance = ApiService._internal();
  
  factory ApiService() {
    return _instance;
  }
  
  ApiService._internal();

  /// Lấy dữ liệu hiện tại từ server
  Future<CurrentData> getCurrentData() async {
    final response = await http.get(Uri.parse('$baseUrl/api/current'));
    
    if (response.statusCode == 200) {
      return CurrentData.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load current data');
    }
  }

  /// Lấy dữ liệu lịch sử từ server
  Future<HistoricalData> getHistoricalData({int hours = 1}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/historical${hours > 1 ? "?hours=$hours" : ""}')
    );
    
    if (response.statusCode == 200) {
      return parseHistoricalData(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load historical data');
    }
  }

  /// Lấy dữ liệu lịch sử cho một thông số cụ thể
  Future<List<HistoricalDataPoint>> getParameterHistoricalData(
    String paramName, {
    int hours = 1,
  }) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/historical/$paramName${hours > 1 ? "?hours=$hours" : ""}')
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as List;
      return data
          .map((item) => HistoricalDataPoint.fromJson(item as Map<String, dynamic>))
          .toList();
    } else {
      throw Exception('Failed to load parameter historical data');
    }
  }

  /// Kiểm tra trạng thái kết nối với ThingsBoard
  Future<bool> checkThingsboardStatus() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/status'));
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['connected'] as bool;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}