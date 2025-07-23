import 'package:firebase_messaging/firebase_messaging.dart';

class NotificationService {
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;

  Future<void> init() async {
    // Request permission from the user
    await _requestPermission();

    // Get the FCM token for this device
    final String? fcmToken = await _getFcmToken();
    if (fcmToken != null) {
      print("FCM Token: $fcmToken");
      // TODO: Save this token to your user's document in Firestore
      // This allows you to send targeted notifications from your backend.
    }

    // Handle incoming messages while the app is in the foreground
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('Got a message whilst in the foreground!');
      print('Message data: ${message.data}');

      if (message.notification != null) {
        print('Message also contained a notification: ${message.notification}');
        // You can show a custom in-app notification here
      }
    });

    // Handle notifications when the app is opened from a terminated state
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('A new onMessageOpenedApp event was published!');
      // TODO: Navigate to a specific screen based on the notification data
    });
  }

  Future<void> _requestPermission() async {
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );

    print('User granted permission: ${settings.authorizationStatus}');
  }

  Future<String?> _getFcmToken() async {
    try {
      return await _firebaseMessaging.getToken();
    } catch (e) {
      print("Error getting FCM token: $e");
      return null;
    }
  }

  Future<void> subscribeToTopic(String topic) async {
    await _firebaseMessaging.subscribeToTopic(topic);
    print('Subscribed to topic: $topic');
  }

  Future<void> unsubscribeFromTopic(String topic) async {
    await _firebaseMessaging.unsubscribeFromTopic(topic);
    print('Unsubscribed from topic: $topic');
  }
}
