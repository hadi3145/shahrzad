import 'dart:async';
import 'package:cafe_bazaar_iab/cafe_bazaar_iab.dart';

class BazaarPaymentService {
  final _bazaar = CafeBazaarIab();
  StreamSubscription<dynamic>? _purchaseUpdateSubscription;
  StreamSubscription<dynamic>? _purchaseErrorSubscription;

  // Replace with your actual RSA key from Cafe Bazaar developer panel
  final String rsaPublicKey = "YOUR_RSA_PUBLIC_KEY_FROM_BAZAAR";

  Future<void> init() async {
    await _bazaar.init(rsaKey: rsaPublicKey);

    _purchaseUpdateSubscription = _bazaar.purchaseUpdateStream.listen((purchase) {
      // Handle successful purchase
      // 1. Verify the purchase with your backend server
      // 2. Update user's subscription status in your database (e.g., Firestore)
      // 3. Consume the purchase so the user can buy it again next month
      _consumePurchase(purchase);
    });

    _purchaseErrorSubscription = _bazaar.purchaseErrorStream.listen((error) {
      // Handle purchase errors
      print("Purchase Error: $error");
    });
  }

  Future<List<BazaarProduct>> getSkus(List<String> skuIds) async {
    try {
      final products = await _bazaar.getSkus(sku: skuIds);
      return products;
    } catch (e) {
      print("Error getting SKUs: $e");
      return [];
    }
  }

  Future<void> purchase(String sku) async {
    try {
      await _bazaar.purchase(sku: sku, payload: "payload_for_verification");
    } catch (e) {
      print("Error starting purchase: $e");
    }
  }

  Future<void> _consumePurchase(BazaarPurchase purchase) async {
    try {
      await _bazaar.consume(
        token: purchase.token,
        packageName: purchase.packageName,
        sku: purchase.sku,
      );
      print("Purchase consumed successfully");
    } catch (e) {
      print("Error consuming purchase: $e");
    }
  }

  void dispose() {
    _purchaseUpdateSubscription?.cancel();
    _purchaseErrorSubscription?.cancel();
    _bazaar.dispose();
  }
}
