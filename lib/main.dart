import 'package:flutter/material.dart';
import 'package:signalx/app/app.dart';
import 'package:signalx/core/services/notification_service.dart';
import 'package:signalx/injection_container.dart' as di;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // TODO: Initialize Firebase here
  // await Firebase.initializeApp();

  // Initialize dependency injection
  await di.init();

  // Initialize notification service
  final notificationService = NotificationService();
  await notificationService.init();
  // Automatically subscribe users to new signals topic
  await notificationService.subscribeToTopic('new_signals');

  runApp(const SignalXApp());
}
