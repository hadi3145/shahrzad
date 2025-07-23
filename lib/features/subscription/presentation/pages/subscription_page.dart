import 'package:cafe_bazaar_iab/cafe_bazaar_iab.dart';
import 'package:flutter/material.dart';
import 'package:signalx/features/subscription/data/services/bazaar_payment_service.dart';

class SubscriptionPage extends StatefulWidget {
  const SubscriptionPage({super.key});

  @override
  State<SubscriptionPage> createState() => _SubscriptionPageState();
}

class _SubscriptionPageState extends State<SubscriptionPage> {
  final BazaarPaymentService _paymentService = BazaarPaymentService();
  List<BazaarProduct> _products = [];
  bool _isLoading = true;

  // Replace with your actual SKU IDs from Cafe Bazaar developer panel
  final List<String> _skuIds = [
    'monthly_subscription',
    'quarterly_subscription',
    'yearly_subscription',
  ];

  @override
  void initState() {
    super.initState();
    _paymentService.init();
    _loadProducts();
  }

  Future<void> _loadProducts() async {
    setState(() {
      _isLoading = true;
    });
    final products = await _paymentService.getSkus(_skuIds);
    setState(() {
      _products = products;
      _isLoading = false;
    });
  }

  @override
  void dispose() {
    _paymentService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Upgrade to Premium'),
        centerTitle: true,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildProductList(),
    );
  }

  Widget _buildProductList() {
    if (_products.isEmpty) {
      return const Center(
        child: Text('Could not load subscription plans. Please try again later.'),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16.0),
      itemCount: _products.length,
      itemBuilder: (context, index) {
        final product = _products[index];
        return Card(
          margin: const EdgeInsets.symmetric(vertical: 8.0),
          child: ListTile(
            title: Text(product.title ?? 'No Title'),
            subtitle: Text(product.description ?? 'No Description'),
            trailing: ElevatedButton(
              onPressed: () {
                _paymentService.purchase(product.sku);
              },
              child: Text(product.price ?? 'Buy'),
            ),
          ),
        );
      },
    );
  }
}
