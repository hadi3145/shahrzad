import 'package:flutter/material.dart';
import 'package:signalx/app/theme/app_theme.dart';
import 'package:signalx/features/auth/presentation/pages/login_page.dart';

class SignalXApp extends StatelessWidget {
  const SignalXApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SignalX',
      theme: AppTheme.darkTheme,
      debugShowCheckedModeBanner: false,
      home: const LoginPage(),
    );
  }
}
