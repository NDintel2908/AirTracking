package com.envmonitor.ui.parameter

import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Spinner
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.envmonitor.R
import com.envmonitor.api.RetrofitClient
import com.envmonitor.models.CurrentData
import com.envmonitor.models.EnvParameter
import com.envmonitor.models.HistoricalData
import com.github.mikephil.charting.charts.LineChart
import com.github.mikephil.charting.components.XAxis
import com.github.mikephil.charting.data.Entry
import com.github.mikephil.charting.data.LineData
import com.github.mikephil.charting.data.LineDataSet
import com.github.mikephil.charting.formatter.ValueFormatter
import kotlinx.coroutines.CoroutineExceptionHandler
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Activity hiển thị chi tiết một thông số môi trường
 */
class ParameterDetailActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_PARAMETER_ID = "extra_parameter_id"
        const val EXTRA_PARAMETER_NAME = "extra_parameter_name"
        
        private val TIME_RANGES = mapOf(
            "1 giờ" to 1,
            "3 giờ" to 3,
            "6 giờ" to 6,
            "12 giờ" to 12,
            "24 giờ" to 24
        )
        
        private val PARAMETER_DESCRIPTIONS = mapOf(
            "temperature" to "Nhiệt độ không khí xung quanh, đo bằng độ C. Nhiệt độ cao có thể ảnh hưởng đến sức khỏe, đặc biệt là người già và trẻ em.",
            "humidity" to "Độ ẩm không khí, đo bằng phần trăm (%). Độ ẩm quá cao hoặc quá thấp có thể gây khó chịu và ảnh hưởng đến hệ hô hấp.",
            "pm10" to "Các hạt bụi có đường kính dưới 10 micromet, đo bằng μg/m³. PM10 có thể xâm nhập vào phổi và gây ra các vấn đề hô hấp.",
            "pm25" to "Các hạt bụi mịn có đường kính dưới 2.5 micromet, đo bằng μg/m³. PM2.5 rất nguy hiểm vì có thể xâm nhập sâu vào phổi và đi vào máu.",
            "co" to "Khí Carbon Monoxide (CO), đo bằng ppm. CO là khí không màu, không mùi nhưng rất độc, có thể gây ngộ độc nếu hít phải nồng độ cao.",
            "noise" to "Mức độ tiếng ồn xung quanh, đo bằng decibel (dB). Tiếng ồn lớn kéo dài có thể gây stress và ảnh hưởng thính giác.",
            "aqi" to "Chỉ số chất lượng không khí (Air Quality Index). Tính toán dựa trên nồng độ của các chất ô nhiễm chính theo tiêu chuẩn Việt Nam."
        )
        
        private val PARAMETER_THRESHOLDS = mapOf(
            "temperature" to Pair(35.0, 40.0), // warning, danger
            "humidity" to Pair(75.0, 85.0),
            "pm10" to Pair(50.0, 150.0),
            "pm25" to Pair(25.0, 50.0),
            "co" to Pair(30.0, 60.0),
            "noise" to Pair(70.0, 85.0),
            "aqi" to Pair(100.0, 150.0)
        )
    }

    private lateinit var swipeRefreshLayout: SwipeRefreshLayout
    private lateinit var toolbar: Toolbar
    private lateinit var parameterName: TextView
    private lateinit var parameterDescription: TextView
    private lateinit var parameterValue: TextView
    private lateinit var parameterUnit: TextView
    private lateinit var parameterStatus: TextView
    private lateinit var thresholdWarningValue: TextView
    private lateinit var thresholdDangerValue: TextView
    private lateinit var timeRangeSpinner: Spinner
    private lateinit var historicalChart: LineChart
    private lateinit var chartProgressBar: View
    private lateinit var chartErrorText: TextView
    private lateinit var lastRefreshedText: TextView
    private lateinit var offlineIndicator: TextView

    private val apiService = RetrofitClient.apiService
    private var parameterId = ""
    private var selectedTimeRange = 1 // mặc định 1 giờ
    
    private var currentParameter: EnvParameter? = null
    private var historicalData: HistoricalData? = null

    private val refreshCoroutineHandler = CoroutineExceptionHandler { _, throwable ->
        runOnUiThread {
            swipeRefreshLayout.isRefreshing = false
            offlineIndicator.visibility = View.VISIBLE
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_parameter_detail)

        // Lấy thông tin từ intent
        parameterId = intent.getStringExtra(EXTRA_PARAMETER_ID) ?: ""
        val parameterDisplayName = intent.getStringExtra(EXTRA_PARAMETER_NAME) ?: ""
        
        initViews()
        setupActionBar(parameterDisplayName)
        setupSpinner()
        setupChart()
        
        loadData()
    }
    
    private fun initViews() {
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout)
        toolbar = findViewById(R.id.toolbar)
        parameterName = findViewById(R.id.parameterName)
        parameterDescription = findViewById(R.id.parameterDescription)
        parameterValue = findViewById(R.id.parameterValue)
        parameterUnit = findViewById(R.id.parameterUnit)
        parameterStatus = findViewById(R.id.parameterStatus)
        thresholdWarningValue = findViewById(R.id.thresholdWarningValue)
        thresholdDangerValue = findViewById(R.id.thresholdDangerValue)
        timeRangeSpinner = findViewById(R.id.timeRangeSpinner)
        historicalChart = findViewById(R.id.historicalChart)
        chartProgressBar = findViewById(R.id.chartProgressBar)
        chartErrorText = findViewById(R.id.chartErrorText)
        lastRefreshedText = findViewById(R.id.lastRefreshedText)
        offlineIndicator = findViewById(R.id.offlineIndicator)
        
        swipeRefreshLayout.setOnRefreshListener {
            loadData()
        }
        
        // Thiết lập mô tả thông số
        parameterDescription.text = PARAMETER_DESCRIPTIONS[parameterId] ?: ""
        
        // Thiết lập ngưỡng
        val thresholds = PARAMETER_THRESHOLDS[parameterId]
        if (thresholds != null) {
            val warningThreshold = thresholds.first
            val dangerThreshold = thresholds.second
            
            thresholdWarningValue.text = formatValue(warningThreshold)
            thresholdDangerValue.text = formatValue(dangerThreshold)
        }
    }
    
    private fun setupActionBar(title: String) {
        setSupportActionBar(toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = title
        
        toolbar.setNavigationOnClickListener {
            onBackPressed()
        }
    }
    
    private fun setupSpinner() {
        val timeRanges = TIME_RANGES.keys.toList()
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, timeRanges)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        timeRangeSpinner.adapter = adapter
        
        timeRangeSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val selectedRange = timeRanges[position]
                selectedTimeRange = TIME_RANGES[selectedRange] ?: 1
                loadHistoricalData()
            }
            
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }
    }
    
    private fun setupChart() {
        historicalChart.apply {
            description.isEnabled = false
            legend.isEnabled = false
            setTouchEnabled(true)
            setScaleEnabled(true)
            setPinchZoom(true)
            
            xAxis.apply {
                position = XAxis.Position.BOTTOM
                setDrawGridLines(false)
                granularity = 1f
                labelRotationAngle = -45f
                valueFormatter = object : ValueFormatter() {
                    override fun getFormattedValue(value: Float): String {
                        val index = value.toInt()
                        val data = historicalData?.get(parameterId) ?: return ""
                        return if (index >= 0 && index < data.size) data[index].timestamp else ""
                    }
                }
            }
            
            axisLeft.apply {
                setDrawGridLines(true)
                setDrawZeroLine(false)
            }
            
            axisRight.isEnabled = false
        }
    }
    
    private fun loadData() {
        lifecycleScope.launch(Dispatchers.IO + refreshCoroutineHandler) {
            try {
                // Lấy dữ liệu hiện tại
                val response = apiService.getCurrentData()
                val currentData = parseCurrentData(response)
                
                // Lấy thông số hiện tại
                currentParameter = when (parameterId) {
                    "temperature" -> currentData.temperature
                    "humidity" -> currentData.humidity
                    "pm10" -> currentData.pm10
                    "pm25" -> currentData.pm25
                    "co" -> currentData.co
                    "noise" -> currentData.noise
                    "aqi" -> currentData.aqi
                    else -> null
                }
                
                // Cập nhật UI
                withContext(Dispatchers.Main) {
                    updateUIWithCurrentData()
                    swipeRefreshLayout.isRefreshing = false
                    offlineIndicator.visibility = View.GONE
                }
                
                // Tải dữ liệu lịch sử
                loadHistoricalData()
                
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    swipeRefreshLayout.isRefreshing = false
                    offlineIndicator.visibility = View.VISIBLE
                }
            }
        }
    }
    
    private fun loadHistoricalData() {
        lifecycleScope.launch(Dispatchers.IO + refreshCoroutineHandler) {
            try {
                showChartLoading()
                
                // Lấy dữ liệu lịch sử
                val response = apiService.getHistoricalData(selectedTimeRange)
                historicalData = parseHistoricalData(response)
                
                withContext(Dispatchers.Main) {
                    updateChart()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    showChartError()
                }
            }
        }
    }
    
    private fun parseCurrentData(response: Map<String, Any>): CurrentData {
        // Phân tích dữ liệu từ JSON
        val data = response["data"] as Map<String, Any>
        
        // Phân tích các thông số
        fun parseParameter(paramData: Map<String, Any>): EnvParameter {
            return EnvParameter(
                value = (paramData["value"] as Double),
                unit = paramData["unit"] as String,
                status = paramData["status"] as String,
                timestamp = paramData["timestamp"] as String,
                lastUpdate = paramData["last_update"] as Long?
            )
        }
        
        // Phân tích từng thông số
        val temperature = parseParameter(data["temperature"] as Map<String, Any>)
        val humidity = parseParameter(data["humidity"] as Map<String, Any>)
        val pm10 = parseParameter(data["pm10"] as Map<String, Any>)
        val pm25 = parseParameter(data["pm25"] as Map<String, Any>)
        val co = parseParameter(data["co"] as Map<String, Any>)
        val noise = parseParameter(data["noise"] as Map<String, Any>)
        val aqi = parseParameter(data["aqi"] as Map<String, Any>)
        
        // Lấy trạng thái thiết bị
        val deviceStatus = data["device_status"] as String
        val lastDataTimestamp = data["last_data_timestamp"] as Long
        
        return CurrentData(
            temperature = temperature,
            humidity = humidity,
            pm10 = pm10,
            pm25 = pm25,
            co = co,
            noise = noise,
            aqi = aqi,
            deviceStatus = deviceStatus,
            lastDataTimestamp = lastDataTimestamp
        )
    }
    
    private fun parseHistoricalData(response: Map<String, List<Map<String, Any>>>): HistoricalData {
        // Phân tích dữ liệu lịch sử từ JSON
        val result = mutableMapOf<String, MutableList<com.envmonitor.models.HistoricalDataPoint>>()
        
        // Phân tích dữ liệu cho từng thông số
        response.forEach { (param, dataPoints) ->
            val points = dataPoints.map { point ->
                val timestamp = point["timestamp"] as String
                val value = (point["value"] as Double)
                com.envmonitor.models.HistoricalDataPoint(timestamp, value)
            }
            
            // Ánh xạ tên thông số từ API sang tên thông số trong ứng dụng
            val normalizedParam = when (param) {
                "temperature" -> "temperature"
                "humidity" -> "humidity"
                "pm10" -> "pm10" 
                "pm25" -> "pm25"
                "co" -> "co"
                "noise" -> "noise"
                "aqi" -> "aqi"
                else -> null
            }
            
            if (normalizedParam != null) {
                result[normalizedParam] = points.toMutableList()
            }
        }
        
        return result
    }
    
    private fun updateUIWithCurrentData() {
        val parameter = currentParameter ?: return
        
        // Cập nhật giá trị
        parameterValue.text = formatValue(parameter.value)
        parameterUnit.text = parameter.unit
        
        // Cập nhật trạng thái
        parameterStatus.text = parameter.getStatusText()
        
        // Đặt màu nền và văn bản theo trạng thái
        when (parameter.status) {
            "normal" -> {
                parameterStatus.setBackgroundColor(ContextCompat.getColor(this, R.color.status_normal))
                parameterStatus.setTextColor(Color.WHITE)
            }
            "warning" -> {
                parameterStatus.setBackgroundColor(ContextCompat.getColor(this, R.color.status_warning))
                parameterStatus.setTextColor(Color.BLACK)
            }
            "kém" -> {
                parameterStatus.setBackgroundColor(ContextCompat.getColor(this, R.color.status_kem))
                parameterStatus.setTextColor(Color.WHITE)
            }
            "danger" -> {
                parameterStatus.setBackgroundColor(ContextCompat.getColor(this, R.color.status_danger))
                parameterStatus.setTextColor(Color.WHITE)
            }
        }
        
        // Cập nhật thời gian cập nhật
        updateLastRefreshedTime()
    }
    
    private fun updateLastRefreshedTime() {
        val dateFormat = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
        val currentTime = dateFormat.format(Date())
        lastRefreshedText.text = getString(R.string.last_updated_time, currentTime)
    }
    
    private fun updateChart() {
        if (historicalData == null || historicalData!!.isEmpty()) {
            showChartError()
            return
        }
        
        val dataPoints = historicalData!![parameterId]
        if (dataPoints.isNullOrEmpty()) {
            showChartError()
            return
        }
        
        // Tạo danh sách Entry cho biểu đồ
        val entries = dataPoints.mapIndexed { index, point ->
            Entry(index.toFloat(), point.value.toFloat())
        }
        
        // Thiết lập màu sắc dựa trên trạng thái hiện tại
        val colorRes = when (currentParameter?.status) {
            "normal" -> R.color.status_normal
            "warning" -> R.color.status_warning
            "kém" -> R.color.status_kem
            "danger" -> R.color.status_danger
            else -> R.color.primary
        }
        
        // Tạo tập dữ liệu
        val dataSet = LineDataSet(entries, parameterId).apply {
            color = ContextCompat.getColor(this@ParameterDetailActivity, colorRes)
            setDrawCircles(false)
            setDrawValues(false)
            lineWidth = 2f
            mode = LineDataSet.Mode.CUBIC_BEZIER
        }
        
        // Cập nhật biểu đồ
        historicalChart.data = LineData(dataSet)
        historicalChart.invalidate()
        
        // Hiển thị biểu đồ
        showChart()
    }
    
    private fun formatValue(value: Double): String {
        return if (value == value.toInt().toDouble()) {
            value.toInt().toString()
        } else {
            String.format("%.1f", value)
        }
    }
    
    private fun showChart() {
        withContext(Dispatchers.Main) {
            historicalChart.visibility = View.VISIBLE
            chartProgressBar.visibility = View.GONE
            chartErrorText.visibility = View.GONE
        }
    }
    
    private fun showChartError() {
        withContext(Dispatchers.Main) {
            historicalChart.visibility = View.GONE
            chartProgressBar.visibility = View.GONE
            chartErrorText.visibility = View.VISIBLE
        }
    }
    
    private fun showChartLoading() {
        withContext(Dispatchers.Main) {
            historicalChart.visibility = View.GONE
            chartProgressBar.visibility = View.VISIBLE
            chartErrorText.visibility = View.GONE
        }
    }
}