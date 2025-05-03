package com.envmonitor.models

/**
 * Mô hình dữ liệu cho một thông số môi trường
 * 
 * @property value Giá trị của thông số
 * @property unit Đơn vị đo lường
 * @property status Trạng thái dựa trên ngưỡng (normal, warning, kém, danger)
 * @property timestamp Thời gian cập nhật (format HH:mm:ss)
 * @property lastUpdate Thời điểm cập nhật cuối cùng (timestamp Unix hoặc null)
 */
data class EnvParameter(
    val value: Double,
    val unit: String,
    val status: String,
    val timestamp: String,
    val lastUpdate: Long? = null
) {

    /**
     * Lấy văn bản trạng thái phù hợp dựa trên status
     */
    fun getStatusText(): String {
        return when (status) {
            "normal" -> "Tốt"
            "warning" -> "Trung bình"
            "kém" -> "Kém"
            "danger" -> "Xấu"
            "offline" -> "Offline"
            else -> "Không xác định"
        }
    }
    
    /**
     * Kiểm tra xem thông số có vượt quá ngưỡng cảnh báo hay không
     * @return true nếu thông số vượt quá ngưỡng cảnh báo
     */
    fun isWarningOrAbove(): Boolean {
        return status == "warning" || status == "kém" || status == "danger"
    }
    
    /**
     * Kiểm tra xem thông số có vượt quá ngưỡng nguy hiểm hay không
     * @return true nếu thông số vượt quá ngưỡng nguy hiểm
     */
    fun isDanger(): Boolean {
        return status == "danger"
    }
}