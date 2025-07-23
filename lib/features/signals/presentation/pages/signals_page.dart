import 'package:flutter/material.dart';
import 'package:signalx/features/signals/domain/entities/signal.dart';
import 'package:signalx/features/signals/presentation/widgets/signal_card.dart';

class SignalsPage extends StatelessWidget {
  const SignalsPage({super.key});

  // Mock data for demonstration purposes
  static final List<Signal> _mockSignals = [
    Signal(
      id: '1',
      symbol: 'BTC/USDT',
      market: 'crypto',
      direction: 'long',
      entryPoint: [65000, 65500],
      targets: [67000, 69000],
      stopLoss: 63500,
      status: 'active',
      createdAt: DateTime.now().subtract(const Duration(hours: 2)),
    ),
    Signal(
      id: '2',
      symbol: 'EUR/USD',
      market: 'forex',
      direction: 'short',
      entryPoint: [1.0750],
      targets: [1.0700, 1.0650],
      stopLoss: 1.0800,
      status: 'hit_target',
      createdAt: DateTime.now().subtract(const Duration(days: 1)),
    ),
    Signal(
      id: '3',
      symbol: 'ETH/USDT',
      market: 'crypto',
      direction: 'long',
      entryPoint: [3500],
      targets: [3600, 3700],
      stopLoss: 3400,
      status: 'stopped',
      createdAt: DateTime.now().subtract(const Duration(days: 3)),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final cryptoSignals = _mockSignals.where((s) => s.market == 'crypto').toList();
    final forexSignals = _mockSignals.where((s) => s.market == 'forex').toList();

    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Trade Signals'),
          centerTitle: true,
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Crypto'),
              Tab(text: 'Forex'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildSignalList(cryptoSignals),
            _buildSignalList(forexSignals),
          ],
        ),
      ),
    );
  }

  Widget _buildSignalList(List<Signal> signals) {
    if (signals.isEmpty) {
      return const Center(
        child: Text('No signals available in this market.'),
      );
    }
    return ListView.builder(
      itemCount: signals.length,
      itemBuilder: (context, index) {
        return SignalCard(signal: signals[index]);
      },
    );
  }
}
