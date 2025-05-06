import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'screens/parameter_detail_screen.dart';
import 'models/parameter_card_item.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Giám sát Môi trường',
      theme: AppTheme.lightTheme,
      initialRoute: '/',
      onGenerateRoute: (settings) {
        if (settings.name == '/') {
          return MaterialPageRoute(
            builder: (context) => const HomeScreen(),
          );
        } else if (settings.name!.startsWith('/parameter/')) {
          final parameter = settings.arguments as ParameterCardItem;
          return MaterialPageRoute(
            builder: (context) => ParameterDetailScreen(parameter: parameter),
          );
        }
        return null;
      },
      // Cài đặt debug banner và các tùy chọn khác
      debugShowCheckedModeBanner: false,
    );
  }
}