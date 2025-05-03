package com.envmonitor.api

import com.google.gson.GsonBuilder
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Client Retrofit để giao tiếp với API
 */
object RetrofitClient {
    
    // Địa chỉ cơ sở của API
    private const val BASE_URL = "http://localhost:5000"
    
    /**
     * OkHttpClient được cấu hình với timeout
     */
    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    /**
     * Gson converter để chuyển đổi JSON sang đối tượng
     */
    private val gson = GsonBuilder()
        .setLenient()
        .create()
    
    /**
     * Instance của Retrofit
     */
    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create(gson))
        .build()
    
    /**
     * Instance của ApiService
     */
    val apiService: ApiService = retrofit.create(ApiService::class.java)
    
    /**
     * Khởi tạo hoặc cấu hình lại client với một URL khác
     * 
     * @param baseUrl URL cơ sở mới
     * @return ApiService được cấu hình với URL mới
     */
    fun reconfigureClient(baseUrl: String): ApiService {
        val newRetrofit = Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
        
        return newRetrofit.create(ApiService::class.java)
    }
}