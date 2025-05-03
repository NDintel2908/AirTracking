package com.envmonitor.utils

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.os.Build

/**
 * Tiện ích kiểm tra kết nối mạng
 */
object NetworkUtils {
    
    /**
     * Kiểm tra xem thiết bị có kết nối Internet hay không
     * 
     * @param context Context của ứng dụng
     * @return true nếu có kết nối Internet, false nếu không
     */
    fun isNetworkAvailable(context: Context): Boolean {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val network = connectivityManager.activeNetwork ?: return false
            val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
            
            return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
                   capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
        } else {
            // For older versions
            @Suppress("DEPRECATION")
            val networkInfo = connectivityManager.activeNetworkInfo
            @Suppress("DEPRECATION")
            return networkInfo != null && networkInfo.isConnected
        }
    }
    
    /**
     * Lấy loại mạng đang được sử dụng (Wi-Fi, di động, v.v.)
     * 
     * @param context Context của ứng dụng
     * @return Chuỗi mô tả loại mạng
     */
    fun getNetworkType(context: Context): String {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val network = connectivityManager.activeNetwork ?: return "Không có mạng"
            val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return "Không xác định"
            
            return when {
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "Wi-Fi"
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "Di động"
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> "Ethernet"
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_BLUETOOTH) -> "Bluetooth"
                else -> "Khác"
            }
        } else {
            // For older versions
            @Suppress("DEPRECATION")
            val networkInfo = connectivityManager.activeNetworkInfo ?: return "Không có mạng"
            
            @Suppress("DEPRECATION")
            return when (networkInfo.type) {
                ConnectivityManager.TYPE_WIFI -> "Wi-Fi"
                ConnectivityManager.TYPE_MOBILE -> "Di động"
                ConnectivityManager.TYPE_ETHERNET -> "Ethernet"
                ConnectivityManager.TYPE_BLUETOOTH -> "Bluetooth"
                else -> "Khác"
            }
        }
    }
    
    /**
     * Đăng ký lắng nghe sự thay đổi kết nối mạng
     * 
     * @param context Context của ứng dụng
     * @param callback Hàm callback được gọi khi trạng thái mạng thay đổi
     * @return NetworkCallback đã đăng ký
     */
    fun registerNetworkCallback(context: Context, callback: (Boolean) -> Unit): ConnectivityManager.NetworkCallback? {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            
            val networkCallback = object : ConnectivityManager.NetworkCallback() {
                override fun onAvailable(network: Network) {
                    callback(true)
                }
                
                override fun onLost(network: Network) {
                    callback(false)
                }
            }
            
            connectivityManager.registerDefaultNetworkCallback(networkCallback)
            return networkCallback
        }
        
        return null
    }
    
    /**
     * Hủy đăng ký lắng nghe sự thay đổi kết nối mạng
     * 
     * @param context Context của ứng dụng
     * @param callback NetworkCallback đã đăng ký
     */
    fun unregisterNetworkCallback(context: Context, callback: ConnectivityManager.NetworkCallback?) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N && callback != null) {
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            connectivityManager.unregisterNetworkCallback(callback)
        }
    }
}