import 'package:flutter/material.dart';

class AppTheme {
  // Màu sắc chính
  static const Color primaryColor = Color(0xFF1976D2);
  static const Color secondaryColor = Color(0xFF03A9F4);
  static const Color accentColor = Color(0xFF00BCD4);
  
  // Màu trạng thái
  static const Color normalColor = Color(0xFF00E400); // Xanh lá - Tốt
  static const Color warningColor = Color(0xFFFFFF00); // Vàng - Trung bình
  static const Color kemColor = Color(0xFFFF7E00); // Cam - Kém 
  static const Color dangerColor = Color(0xFFFF0000); // Đỏ - Xấu
  static const Color veryBadColor = Color(0xFF99004C); // Tím - Rất xấu
  static const Color hazardousColor = Color(0xFF7E0023); // Nâu đỏ - Nguy hiểm
  
  // Màu văn bản
  static const Color warningTextColor = Colors.black; // Màu chữ trên nền vàng
  static const Color lightTextColor = Colors.white; // Màu chữ trên nền tối
  
  // Màu cho biểu đồ
  static const List<Color> chartColors = [
    primaryColor,
    Color(0xFF4CAF50),
    Color(0xFFFFC107),
    Color(0xFFE91E63),
    Color(0xFF9C27B0),
  ];
  
  // Light theme
  static final ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    primaryColor: primaryColor,
    appBarTheme: const AppBarTheme(
      backgroundColor: primaryColor,
      foregroundColor: Colors.white,
      elevation: 0,
    ),
    scaffoldBackgroundColor: Colors.grey[50],
    cardTheme: CardTheme(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
    colorScheme: ColorScheme.fromSwatch().copyWith(
      primary: primaryColor,
      secondary: secondaryColor,
    ),
    textTheme: const TextTheme(
      titleLarge: TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.bold,
        color: Colors.black87,
      ),
      bodyLarge: TextStyle(
        fontSize: 16,
        color: Colors.black87,
      ),
      bodyMedium: TextStyle(
        fontSize: 14,
        color: Colors.black54,
      ),
    ),
    dividerTheme: const DividerThemeData(
      color: Colors.black12,
      thickness: 1,
    ),
  );
  
  // Lấy màu trạng thái dựa trên status
  static Color getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'normal':
      case 'tốt':
        return normalColor;
      case 'warning':
      case 'trung bình':
        return warningColor;
      case 'kém':
        return kemColor;
      case 'danger':
      case 'xấu':
        return dangerColor;
      case 'rất xấu':
        return veryBadColor;
      case 'nguy hiểm':
        return hazardousColor;
      default:
        return Colors.grey;
    }
  }
  
  // Lấy màu chữ cho trạng thái
  static Color getStatusTextColor(String status) {
    switch (status.toLowerCase()) {
      case 'warning':
      case 'trung bình':
        return warningTextColor;
      default:
        return lightTextColor;
    }
  }
}