package com.envmonitor.models

import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.TimeUnit

/**
 * Mô hình trạng thái thiết bị giám sát
 * 
 * @property status Trạng thái của thiết bị (online, inactive, offline, unknown)
 * @property lastTimestamp Thời điểm dữ liệu mới nhất được ghi nhận
 */
data class DeviceStatus(
    val status: String,
    val lastTimestamp: Long?
) {

    companion object {
        private const val INACTIVE_THRESHOLD_MS = 15 * 60 * 1000 // 15 phút
        private const val OFFLINE_THRESHOLD_MS = 60 * 60 * 1000  // 1 giờ
        
        /**
         * Tạo đối tượng DeviceStatus từ trạng thái thiết bị và thời điểm cập nhật
         * 
         * @param deviceStatus Trạng thái thiết bị từ server
         * @param timestamp Thời điểm cập nhật cuối cùng
         * @return DeviceStatus được cập nhật
         */
        fun fromServerStatus(deviceStatus: String?, timestamp: Long?): DeviceStatus {
            // Nếu đã có trạng thái từ server, ưu tiên sử dụng
            if (deviceStatus != null && deviceStatus != "unknown") {
                return DeviceStatus(deviceStatus, timestamp)
            }
            
            // Nếu không có timestamp, coi như không xác định
            if (timestamp == null) {
                return DeviceStatus("unknown", null)
            }
            
            // Tính toán từ timestamp
            val now = System.currentTimeMillis()
            val diff = now - timestamp
            
            return when {
                diff < INACTIVE_THRESHOLD_MS -> DeviceStatus("online", timestamp)
                diff < OFFLINE_THRESHOLD_MS -> DeviceStatus("inactive", timestamp)
                else -> DeviceStatus("offline", timestamp)
            }
        }
    }
    
    /**
     * Lấy thông báo trạng thái thiết bị phù hợp
     * 
     * @return Chuỗi thông báo trạng thái
     */
    fun getStatusMessage(): String {
        return when (status) {
            "online" -> "Thiết bị đang hoạt động"
            "inactive" -> "Thiết bị không hoạt động trong thời gian ngắn"
            "offline" -> "Thiết bị ngừng hoạt động"
            else -> "Không xác định trạng thái thiết bị"
        }
    }
    
    /**
     * Lấy thông báo thời gian cập nhật cuối cùng
     * 
     * @return Chuỗi hiển thị thời gian cập nhật
     */
    fun getLastUpdateText(): String {
        if (lastTimestamp == null) {
            return "Không có dữ liệu"
        }
        
        val now = System.currentTimeMillis()
        val diff = now - lastTimestamp
        
        // Định dạng thời gian
        return when {
            diff < 60 * 1000 -> "Vừa cập nhật"
            diff < 60 * 60 * 1000 -> "${TimeUnit.MILLISECONDS.toMinutes(diff)} phút trước"
            diff < 24 * 60 * 60 * 1000 -> "${TimeUnit.MILLISECONDS.toHours(diff)} giờ trước"
            else -> {
                val dateFormat = SimpleDateFormat("dd/MM/yyyy HH:mm", Locale.getDefault())
                "Lần cuối: ${dateFormat.format(Date(lastTimestamp))}"
            }
        }
    }
}