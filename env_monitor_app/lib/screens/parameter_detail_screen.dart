import 'dart:async';
import 'package:flutter/material.dart';
import '../models/historical_data.dart';
import '../models/parameter_card_item.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/line_chart.dart';
import '../widgets/status_badge.dart';

class ParameterDetailScreen extends StatefulWidget {
  final ParameterCardItem parameter;

  const ParameterDetailScreen({super.key, required this.parameter});

  @override
  State<ParameterDetailScreen> createState() => _ParameterDetailScreenState();
}

class _ParameterDetailScreenState extends State<ParameterDetailScreen> {
  final ApiService _apiService = ApiService();
  List<HistoricalDataPoint> _historicalData = [];
  bool _isLoading = true;
  int _selectedTimeRange = 1; // Mặc định 1 giờ
  Timer? _refreshTimer;
  
  @override
  void initState() {
    super.initState();
    _loadData();
    
    // Thiết lập timer để tự động cập nhật dữ liệu mỗi phút
    _refreshTimer = Timer.periodic(const Duration(minutes: 1), (timer) {
      _loadData();
    });
  }
  
  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }
  
  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });
    
    try {
      final data = await _apiService.getParameterHistoricalData(
        widget.parameter.id,
        hours: _selectedTimeRange,
      );
      
      setState(() {
        _historicalData = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Lỗi khi tải dữ liệu: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
  
  void _changeTimeRange(int hours) {
    setState(() {
      _selectedTimeRange = hours;
    });
    _loadData();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.parameter.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _loadData,
            tooltip: 'Làm mới dữ liệu',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildBody(),
    );
  }
  
  Widget _buildBody() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Thẻ thông tin hiện tại
          _buildCurrentInfoCard(),
          
          // Điều khiển phạm vi thời gian
          _buildTimeRangeControls(),
          
          // Biểu đồ
          _buildChartSection(),
          
          // Thông tin thêm
          _buildAdditionalInfo(),
        ],
      ),
    );
  }
  
  Widget _buildCurrentInfoCard() {
    final statusColor = AppTheme.getStatusColor(widget.parameter.status);
    
    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Giá trị hiện tại',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                StatusBadge(
                  status: widget.parameter.status,
                  statusText: widget.parameter.statusText,
                  fontSize: 14.0,
                ),
              ],
            ),
            const SizedBox(height: 16.0),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  widget.parameter.formattedValue,
                  style: Theme.of(context).textTheme.headlineMedium!.copyWith(
                    fontSize: 32.0,
                    fontWeight: FontWeight.bold,
                    color: statusColor,
                  ),
                ),
                const SizedBox(width: 8.0),
                Padding(
                  padding: const EdgeInsets.only(bottom: 4.0),
                  child: Text(
                    widget.parameter.unit,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildTimeRangeControls() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Lịch sử dữ liệu',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8.0),
          Row(
            children: [
              _buildTimeRangeButton(1, 'Giờ qua'),
              const SizedBox(width: 8.0),
              _buildTimeRangeButton(6, '6 Giờ'),
              const SizedBox(width: 8.0),
              _buildTimeRangeButton(24, '24 Giờ'),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildTimeRangeButton(int hours, String label) {
    final isSelected = _selectedTimeRange == hours;
    
    return Expanded(
      child: ElevatedButton(
        onPressed: () => _changeTimeRange(hours),
        style: ElevatedButton.styleFrom(
          backgroundColor: isSelected ? AppTheme.primaryColor : Colors.grey[200],
          foregroundColor: isSelected ? Colors.white : Colors.black87,
        ),
        child: Text(label),
      ),
    );
  }
  
  Widget _buildChartSection() {
    return _historicalData.isEmpty
        ? const Center(
            child: Padding(
              padding: EdgeInsets.all(32.0),
              child: Text('Không có dữ liệu lịch sử'),
            ),
          )
        : ParameterLineChart(
            data: _historicalData,
            paramName: widget.parameter.name,
            unit: widget.parameter.unit,
          );
  }
  
  Widget _buildAdditionalInfo() {
    // Thông tin thêm về thông số này
    String infoText = '';
    
    switch (widget.parameter.id) {
      case 'temperature':
        infoText = 'Nhiệt độ môi trường được đo bằng cảm biến độ chính xác cao. '
            'Nhiệt độ ảnh hưởng trực tiếp đến sức khỏe và cảm giác của con người. '
            'Ngưỡng cảnh báo: ≥ 35°C. Ngưỡng nguy hiểm: ≥ 40°C.';
        break;
      case 'humidity':
        infoText = 'Độ ẩm là lượng hơi nước trong không khí. '
            'Độ ẩm ảnh hưởng đến cảm giác nhiệt độ và sức khỏe. '
            'Mức độ thoải mái thông thường nằm trong khoảng 40-60%. '
            'Ngưỡng cảnh báo: ≤ 20% hoặc ≥ 70%. Ngưỡng nguy hiểm: ≤ 10% hoặc ≥ 90%.';
        break;
      case 'pm25':
        infoText = 'PM2.5 là các hạt bụi mịn có đường kính nhỏ hơn 2.5 micromet, '
            'có thể xâm nhập sâu vào phổi và hệ tuần hoàn. '
            'Ngưỡng cảnh báo: ≥ 25 μg/m³. Ngưỡng nguy hiểm: ≥ 50 μg/m³.';
        break;
      case 'pm10':
        infoText = 'PM10 là các hạt bụi có đường kính nhỏ hơn 10 micromet, '
            'có thể xâm nhập vào hệ hô hấp. '
            'Ngưỡng cảnh báo: ≥ 50 μg/m³. Ngưỡng nguy hiểm: ≥ 150 μg/m³.';
        break;
      case 'co':
        infoText = 'CO (Carbon Monoxide) là khí không màu, không mùi và rất độc. '
            'Có thể gây ngộ độc hoặc tử vong ở nồng độ cao. '
            'Ngưỡng cảnh báo: ≥ 30 ppm. Ngưỡng nguy hiểm: ≥ 60 ppm.';
        break;
      case 'noise':
        infoText = 'Tiếng ồn là mức độ âm thanh trong môi trường. '
            'Tiếng ồn kéo dài có thể gây căng thẳng và các vấn đề sức khỏe. '
            'Ngưỡng cảnh báo: ≥ 70 dB. Ngưỡng nguy hiểm: ≥ 90 dB.';
        break;
      case 'aqi':
        infoText = 'Chỉ số chất lượng không khí (AQI) là chỉ số tổng hợp đánh giá mức độ ô nhiễm không khí. '
            'Được tính toán từ các thông số PM2.5, PM10 và CO theo Quyết định 1459/QĐ-TCMT của Việt Nam. '
            'Được phân loại theo thang: '
            'Tốt (0-50), Trung bình (51-100), Kém (101-150), Xấu (151-200), '
            'Rất xấu (201-300), Nguy hiểm (301-500).';
        break;
    }
    
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Thông tin',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8.0),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                infoText,
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ),
          ),
        ],
      ),
    );
  }
}