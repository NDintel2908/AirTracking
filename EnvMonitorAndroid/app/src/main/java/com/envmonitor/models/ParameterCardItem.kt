package com.envmonitor.models

/**
 * Mô hình dữ liệu cho một mục thẻ thông số môi trường
 * Được sử dụng để hiển thị trên RecyclerView
 * 
 * @property id Định danh của thông số
 * @property name Tên hiển thị của thông số
 * @property value Giá trị hiện tại
 * @property unit Đơn vị của thông số
 * @property status Trạng thái dựa trên ngưỡng (normal, warning, kém, danger)
 * @property statusText Văn bản trạng thái hiển thị (Tốt, Trung bình, Kém, Xấu)
 */
data class ParameterCardItem(
    val id: String,
    val name: String,
    val value: Double,
    val unit: String,
    val status: String,
    val statusText: String
) {
    companion object {
        /**
         * Tạo danh sách các mục thẻ thông số từ dữ liệu hiện tại
         * 
         * @param currentData Dữ liệu hiện tại của các thông số
         * @param displayNames Map tên hiển thị cho các thông số
         * @return Danh sách các mục thẻ thông số
         */
        fun fromCurrentData(
            currentData: CurrentData,
            displayNames: Map<String, String>
        ): List<ParameterCardItem> {
            val items = mutableListOf<ParameterCardItem>()
            
            // Thêm các thông số theo thứ tự ưu tiên
            items.add(
                ParameterCardItem(
                    id = "aqi",
                    name = displayNames["aqi"] ?: "AQI",
                    value = currentData.aqi.value,
                    unit = currentData.aqi.unit,
                    status = currentData.aqi.status,
                    statusText = currentData.aqi.getStatusText()
                )
            )
            
            items.add(
                ParameterCardItem(
                    id = "pm25",
                    name = displayNames["pm25"] ?: "PM2.5",
                    value = currentData.pm25.value,
                    unit = currentData.pm25.unit,
                    status = currentData.pm25.status,
                    statusText = currentData.pm25.getStatusText()
                )
            )
            
            items.add(
                ParameterCardItem(
                    id = "pm10",
                    name = displayNames["pm10"] ?: "PM10",
                    value = currentData.pm10.value,
                    unit = currentData.pm10.unit,
                    status = currentData.pm10.status,
                    statusText = currentData.pm10.getStatusText()
                )
            )
            
            items.add(
                ParameterCardItem(
                    id = "temperature",
                    name = displayNames["temperature"] ?: "Nhiệt độ",
                    value = currentData.temperature.value,
                    unit = currentData.temperature.unit,
                    status = currentData.temperature.status,
                    statusText = currentData.temperature.getStatusText()
                )
            )
            
            items.add(
                ParameterCardItem(
                    id = "humidity",
                    name = displayNames["humidity"] ?: "Độ ẩm",
                    value = currentData.humidity.value,
                    unit = currentData.humidity.unit,
                    status = currentData.humidity.status,
                    statusText = currentData.humidity.getStatusText()
                )
            )
            
            items.add(
                ParameterCardItem(
                    id = "co",
                    name = displayNames["co"] ?: "CO",
                    value = currentData.co.value,
                    unit = currentData.co.unit,
                    status = currentData.co.status,
                    statusText = currentData.co.getStatusText()
                )
            )
            
            items.add(
                ParameterCardItem(
                    id = "noise",
                    name = displayNames["noise"] ?: "Tiếng ồn",
                    value = currentData.noise.value,
                    unit = currentData.noise.unit,
                    status = currentData.noise.status,
                    statusText = currentData.noise.getStatusText()
                )
            )
            
            return items
        }
    }
}