package com.envmonitor.api

import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * Interface API Service cho giao tiếp với máy chủ
 */
interface ApiService {
    
    /**
     * Lấy dữ liệu hiện tại từ tất cả các cảm biến
     * 
     * @return Map chứa dữ liệu hiện tại
     */
    @GET("/api/current")
    suspend fun getCurrentData(): Map<String, Any>
    
    /**
     * Lấy dữ liệu lịch sử từ tất cả các cảm biến
     * 
     * @param hours Số giờ cần lấy dữ liệu lịch sử
     * @return Map chứa dữ liệu lịch sử
     */
    @GET("/api/historical")
    suspend fun getHistoricalData(@Query("hours") hours: Int = 1): Map<String, List<Map<String, Any>>>
    
    /**
     * Lấy dữ liệu lịch sử cho một thông số cụ thể
     * 
     * @param paramName Tên của thông số cần lấy dữ liệu
     * @param hours Số giờ cần lấy dữ liệu lịch sử
     * @return Danh sách các điểm dữ liệu lịch sử
     */
    @GET("/api/historical/{param}")
    suspend fun getParameterHistoricalData(
        @Path("param") paramName: String,
        @Query("hours") hours: Int = 1
    ): List<Map<String, Any>>
    
    /**
     * Kiểm tra trạng thái kết nối với ThingsBoard
     * 
     * @return Map chứa thông tin trạng thái kết nối
     */
    @GET("/api/status")
    suspend fun getThingsboardStatus(): Map<String, Boolean>
}