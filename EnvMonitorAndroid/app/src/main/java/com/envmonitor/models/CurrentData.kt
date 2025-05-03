package com.envmonitor.models

/**
 * Mô hình dữ liệu hiện tại từ thiết bị giám sát
 * 
 * @property temperature Dữ liệu nhiệt độ
 * @property humidity Dữ liệu độ ẩm
 * @property pm10 Dữ liệu bụi PM10
 * @property pm25 Dữ liệu bụi PM2.5
 * @property co Dữ liệu khí CO
 * @property noise Dữ liệu tiếng ồn
 * @property aqi Dữ liệu chỉ số chất lượng không khí (AQI)
 * @property deviceStatus Trạng thái thiết bị (online, inactive, offline)
 * @property lastDataTimestamp Thời điểm nhận dữ liệu mới nhất
 */
data class CurrentData(
    val temperature: EnvParameter,
    val humidity: EnvParameter,
    val pm10: EnvParameter,
    val pm25: EnvParameter,
    val co: EnvParameter,
    val noise: EnvParameter,
    val aqi: EnvParameter,
    val deviceStatus: String,
    val lastDataTimestamp: Long
) {
    
    /**
     * Lấy danh sách các thông số dưới dạng các mục để hiển thị trên giao diện
     * 
     * @return Danh sách các thông số có thể hiển thị trên UI
     */
    fun toParameterList(): List<ParameterCardItem> {
        val displayNames = mapOf(
            "temperature" to "Nhiệt độ",
            "humidity" to "Độ ẩm",
            "pm10" to "PM10",
            "pm25" to "PM2.5",
            "co" to "CO",
            "noise" to "Tiếng ồn",
            "aqi" to "AQI"
        )
        
        return ParameterCardItem.fromCurrentData(this, displayNames)
    }
    
    /**
     * Lấy đối tượng trạng thái thiết bị
     * 
     * @return Đối tượng DeviceStatus chứa thông tin trạng thái thiết bị
     */
    fun getDeviceStatusObject(): DeviceStatus {
        return DeviceStatus.fromServerStatus(deviceStatus, lastDataTimestamp)
    }
    
    /**
     * Kiểm tra xem có thông số nào vượt ngưỡng cảnh báo hay không
     * 
     * @return true nếu có ít nhất một thông số vượt ngưỡng cảnh báo
     */
    fun hasAnyWarning(): Boolean {
        return temperature.isWarningOrAbove() || 
               humidity.isWarningOrAbove() || 
               pm10.isWarningOrAbove() || 
               pm25.isWarningOrAbove() || 
               co.isWarningOrAbove() || 
               noise.isWarningOrAbove() ||
               aqi.isWarningOrAbove()
    }
    
    /**
     * Kiểm tra xem có thông số nào vượt ngưỡng nguy hiểm hay không
     * 
     * @return true nếu có ít nhất một thông số vượt ngưỡng nguy hiểm
     */
    fun hasAnyDanger(): Boolean {
        return temperature.isDanger() || 
               humidity.isDanger() || 
               pm10.isDanger() || 
               pm25.isDanger() || 
               co.isDanger() || 
               noise.isDanger() ||
               aqi.isDanger()
    }
}