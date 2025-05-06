import 'dart:async';
import 'package:flutter/material.dart';
import '../models/current_data.dart';
import '../models/device_status.dart';
import '../services/api_service.dart';
import '../widgets/parameter_card.dart';
import '../widgets/status_badge.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = ApiService();
  CurrentData? _currentData;
  bool _isLoading = true;
  bool _isConnected = true;
  String _lastUpdated = '';
  Timer? _refreshTimer;
  
  @override
  void initState() {
    super.initState();
    _loadData();
    
    // Thiết lập timer để tự động cập nhật dữ liệu mỗi 10 giây
    _refreshTimer = Timer.periodic(const Duration(seconds: 10), (timer) {
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
      final data = await _apiService.getCurrentData();
      setState(() {
        _currentData = data;
        _isLoading = false;
        _lastUpdated = DateTime.now().toString().substring(11, 19);
      });
      
      // Kiểm tra kết nối ThingsBoard
      final tbStatus = await _apiService.checkThingsboardStatus();
      setState(() {
        _isConnected = tbStatus;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _isConnected = false;
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
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Giám sát Môi trường'),
        actions: [
          IconButton(
            icon: Icon(
              _isConnected ? Icons.cloud_done : Icons.cloud_off,
              color: _isConnected ? Colors.green : Colors.red,
            ),
            onPressed: null,
            tooltip: _isConnected
                ? 'Đã kết nối với ThingsBoard'
                : 'Mất kết nối với ThingsBoard',
          ),
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
    if (_currentData == null) {
      return const Center(
        child: Text('Không có dữ liệu'),
      );
    }
    
    final parameters = _currentData!.toParameterList();
    final deviceStatus = _currentData!.getDeviceStatusObject();
    
    return RefreshIndicator(
      onRefresh: _loadData,
      child: Column(
        children: [
          // Thông tin thiết bị và cập nhật
          _buildDeviceStatusBar(deviceStatus),
          
          // Danh sách thông số
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(8.0),
              itemCount: parameters.length,
              itemBuilder: (context, index) {
                final param = parameters[index];
                return ParameterCard(
                  parameter: param,
                  onTap: () {
                    // Điều hướng đến trang chi tiết thông số
                    Navigator.pushNamed(
                      context,
                      '/parameter/${param.id}',
                      arguments: param,
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildDeviceStatusBar(DeviceStatus status) {
    return Container(
      padding: const EdgeInsets.all(12.0),
      color: Colors.grey[200],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                status.status == 'online' ? Icons.sensors : Icons.sensors_off,
                color: status.status == 'online' ? Colors.green : Colors.red,
              ),
              const SizedBox(width: 8.0),
              Expanded(
                child: Text(
                  status.getStatusMessage(),
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: status.status == 'online' ? Colors.green : Colors.red,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4.0),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                status.getLastUpdateText(),
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              Text(
                'Cập nhật lúc: $_lastUpdated',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
          ),
        ],
      ),
    );
  }
}