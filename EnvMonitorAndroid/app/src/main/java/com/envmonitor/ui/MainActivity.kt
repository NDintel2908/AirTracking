package com.envmonitor.ui

import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Spinner
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.envmonitor.R
import com.envmonitor.adapters.ParameterAdapter
import com.envmonitor.api.RetrofitClient
import com.envmonitor.models.CurrentData
import com.envmonitor.models.DeviceStatus
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
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Activity chính của ứng dụng, hiển thị bảng điều khiển các thông số môi trường
 */
class MainActivity : AppCompatActivity() {

    private lateinit var swipeRefreshLayout: SwipeRefreshLayout
    private lateinit var deviceStatusText: TextView
    private lateinit var lastUpdateText: TextView
    private lateinit var lastRefreshedText: TextView
    private lateinit var thingsboardStatus: TextView
    private lateinit var parameterCardsContainer: RecyclerView
    private lateinit var offlineIndicator: TextView
    private lateinit var chartParameterSpinner: Spinner
    private lateinit var overviewChart: LineChart
    private lateinit var chartProgressBar: View
    private lateinit var chartErrorText: TextView

    private val parameterAdapter by lazy { ParameterAdapter(this) }
    private val apiService = RetrofitClient.apiService

    private var currentData: CurrentData? = null
    private var historicalData: HistoricalData? = null
    private var selectedChartParameter = "temperature"

    private val parameterNames = mapOf(
        "temperature" to "Nhiệt độ",
        "humidity" to "Độ ẩm",
        "pm10" to "PM10",
        "pm25" to "PM2.5",
        "co" to "CO",
        "noise" to "Tiếng ồn",
        "aqi" to "AQI"
    )

    private val refreshCoroutineHandler = CoroutineExceptionHandler { _, throwable ->
        runOnUiThread {
            swipeRefreshLayout.isRefreshing = false
            offlineIndicator.visibility = View.VISIBLE
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initViews()
        setupRefreshLayout()
        setupRecyclerView()
        setupChartSpinner()
        setupChart()

        loadData()
        startAutoRefresh()
        checkThingsboardStatus()
    }

    private fun initViews() {
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout)
        deviceStatusText = findViewById(R.id.deviceStatusText)
        lastUpdateText = findViewById(R.id.lastUpdateText)
        lastRefreshedText = findViewById(R.id.lastRefreshedText)
        thingsboardStatus = findViewById(R.id.thingsboardStatus)
        parameterCardsContainer = findViewById(R.id.parameterCardsContainer)
        offlineIndicator = findViewById(R.id.offlineIndicator)
        chartParameterSpinner = findViewById(R.id.chartParameterSpinner)
        overviewChart = findViewById(R.id.overviewChart)
        chartProgressBar = findViewById(R.id.chartProgressBar)
        chartErrorText = findViewById(R.id.chartErrorText)
    }

    private fun setupRefreshLayout() {
        swipeRefreshLayout.setOnRefreshListener {
            loadData()
        }
    }

    private fun setupRecyclerView() {
        parameterCardsContainer.apply {
            layoutManager = GridLayoutManager(this@MainActivity, 2)
            adapter = parameterAdapter
        }
    }

    private fun setupChartSpinner() {
        val parameterList = parameterNames.values.toList()
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, parameterList)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        chartParameterSpinner.adapter = adapter

        chartParameterSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val selectedName = parameterList[position]
                selectedChartParameter = parameterNames.entries.find { it.value == selectedName }?.key ?: "temperature"
                updateChart()
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }
    }

    private fun setupChart() {
        overviewChart.apply {
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
                        val data = historicalData?.get(selectedChartParameter) ?: return ""
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
                val newData = parseCurrentData(response)
                currentData = newData

                // Lấy dữ liệu lịch sử
                val historyResponse = apiService.getHistoricalData()
                historicalData = parseHistoricalData(historyResponse)

                withContext(Dispatchers.Main) {
                    updateUI(newData)
                    swipeRefreshLayout.isRefreshing = false
                    offlineIndicator.visibility = View.GONE
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    swipeRefreshLayout.isRefreshing = false
                    offlineIndicator.visibility = View.VISIBLE
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
        
        // Thêm các danh sách rỗng cho mỗi thông số
        parameterNames.keys.forEach { param ->
            result[param] = mutableListOf()
        }
        
        // Phân tích dữ liệu cho từng thông số
        response.forEach { (param, dataPoints) ->
            val points = dataPoints.map { point ->
                val timestamp = point["timestamp"] as String
                val value = (point["value"] as Double)
                com.envmonitor.models.HistoricalDataPoint(timestamp, value)
            }
            
            // Ánh xạ tên thông số từ API sang tên thông số trong ứng dụng
            when (param) {
                "temperature" -> result["temperature"]?.addAll(points)
                "humidity" -> result["humidity"]?.addAll(points)
                "pm10" -> result["pm10"]?.addAll(points)
                "pm25" -> result["pm25"]?.addAll(points)
                "co" -> result["co"]?.addAll(points)
                "noise" -> result["noise"]?.addAll(points)
                "aqi" -> result["aqi"]?.addAll(points)
            }
        }
        
        return result
    }

    private fun updateUI(data: CurrentData) {
        // Cập nhật danh sách thông số
        parameterAdapter.updateItems(data.toParameterList())
        
        // Cập nhật trạng thái thiết bị
        val deviceStatus = data.getDeviceStatusObject()
        updateDeviceStatus(deviceStatus)
        
        // Cập nhật thời gian cập nhật cuối cùng
        updateLastRefreshedTime()
        
        // Cập nhật biểu đồ
        updateChart()
    }

    private fun updateDeviceStatus(deviceStatus: DeviceStatus) {
        deviceStatusText.text = deviceStatus.getStatusMessage()
        lastUpdateText.text = deviceStatus.getLastUpdateText()
        
        // Hiển thị thông báo offline nếu cần
        offlineIndicator.visibility = if (deviceStatus.status == "offline") View.VISIBLE else View.GONE
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
        
        val dataPoints = historicalData!![selectedChartParameter]
        if (dataPoints.isNullOrEmpty()) {
            showChartError()
            return
        }
        
        // Tạo danh sách Entry cho biểu đồ
        val entries = dataPoints.mapIndexed { index, point ->
            Entry(index.toFloat(), point.value.toFloat())
        }
        
        // Thiết lập màu sắc dựa trên trạng thái hiện tại
        val color = getColorForParameter(selectedChartParameter)
        
        // Tạo tập dữ liệu
        val dataSet = LineDataSet(entries, selectedChartParameter).apply {
            this.color = color
            setDrawCircles(false)
            setDrawValues(false)
            lineWidth = 2f
            mode = LineDataSet.Mode.CUBIC_BEZIER
        }
        
        // Cập nhật biểu đồ
        overviewChart.data = LineData(dataSet)
        overviewChart.invalidate()
        
        // Hiển thị biểu đồ
        showChart()
    }

    private fun getColorForParameter(paramName: String): Int {
        val currentParam = when (paramName) {
            "temperature" -> currentData?.temperature
            "humidity" -> currentData?.humidity
            "pm10" -> currentData?.pm10
            "pm25" -> currentData?.pm25
            "co" -> currentData?.co
            "noise" -> currentData?.noise
            "aqi" -> currentData?.aqi
            else -> null
        }
        
        return when (currentParam?.status) {
            "normal" -> getColor(R.color.status_normal)
            "warning" -> getColor(R.color.status_warning)
            "kém" -> getColor(R.color.status_kem)
            "danger" -> getColor(R.color.status_danger)
            else -> getColor(R.color.primary)
        }
    }

    private fun showChart() {
        overviewChart.visibility = View.VISIBLE
        chartProgressBar.visibility = View.GONE
        chartErrorText.visibility = View.GONE
    }

    private fun showChartError() {
        overviewChart.visibility = View.GONE
        chartProgressBar.visibility = View.GONE
        chartErrorText.visibility = View.VISIBLE
    }

    private fun showChartLoading() {
        overviewChart.visibility = View.GONE
        chartProgressBar.visibility = View.VISIBLE
        chartErrorText.visibility = View.GONE
    }

    private fun startAutoRefresh() {
        lifecycleScope.launch(Dispatchers.IO) {
            while (isActive) {
                delay(30000) // Cập nhật mỗi 30 giây
                loadData()
            }
        }
    }

    private fun checkThingsboardStatus() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val response = apiService.getThingsboardStatus()
                val connected = response["connected"] ?: false
                
                withContext(Dispatchers.Main) {
                    thingsboardStatus.text = if (connected as Boolean) {
                        getString(R.string.thingsboard_connected)
                    } else {
                        getString(R.string.thingsboard_disconnected)
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    thingsboardStatus.text = getString(R.string.thingsboard_error)
                }
            }
        }
    }
}