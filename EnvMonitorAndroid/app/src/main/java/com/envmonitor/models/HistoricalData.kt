package com.envmonitor.models

/**
 * Mô hình dữ liệu lịch sử cho các thông số môi trường
 * Đây là một alias để đơn giản hóa việc tham chiếu đến cấu trúc dữ liệu phức tạp
 * Cấu trúc: Map<String, List<HistoricalDataPoint>>
 *   - Khóa: tên thông số (temperature, humidity, etc.)
 *   - Giá trị: danh sách các điểm dữ liệu lịch sử
 */
typealias HistoricalData = Map<String, List<HistoricalDataPoint>>

/**
 * Mô hình một điểm dữ liệu lịch sử
 * 
 * @property timestamp Thời gian của điểm dữ liệu (định dạng HH:mm:ss)
 * @property value Giá trị của thông số tại thời điểm đó
 */
data class HistoricalDataPoint(
    val timestamp: String,
    val value: Double
)