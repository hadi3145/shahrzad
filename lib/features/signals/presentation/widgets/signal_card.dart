import 'package:flutter/material.dart';
import 'package:signalx/features/signals/domain/entities/signal.dart';
import 'package:intl/intl.dart';

class SignalCard extends StatelessWidget {
  final Signal signal;

  const SignalCard({
    super.key,
    required this.signal,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isLong = signal.direction == 'long';
    final directionColor = isLong ? const Color(0xFF26A69A) : const Color(0xFFEF5350);

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    // In a real app, you'd use an image asset or network image
                    CircleAvatar(
                      backgroundColor: theme.colorScheme.surface,
                      child: Text(
                        signal.symbol.substring(0, 1),
                        style: TextStyle(color: theme.colorScheme.onSurface),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(signal.symbol, style: theme.textTheme.titleLarge?.copyWith(fontSize: 18)),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: directionColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    signal.direction.toUpperCase(),
                    style: TextStyle(color: directionColor, fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              'Published: ${DateFormat.yMd().add_jm().format(signal.createdAt)}',
              style: theme.textTheme.bodySmall?.copyWith(color: Colors.white60),
            ),
            const SizedBox(height: 12),
            const Divider(color: Colors.white24, height: 1),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildInfoColumn("Entry", signal.entryPoint.join(' - '), theme),
                _buildInfoColumn("Stop Loss", signal.stopLoss.toString(), theme),
                _buildInfoColumn("Status", signal.status.toUpperCase(), theme, valueColor: _getStatusColor(signal.status)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'active':
        return Colors.orangeAccent;
      case 'hit_target':
        return Colors.greenAccent;
      case 'stopped':
        return Colors.redAccent;
      default:
        return Colors.grey;
    }
  }

  Widget _buildInfoColumn(String title, String value, ThemeData theme, {Color? valueColor}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: theme.textTheme.bodyMedium?.copyWith(color: Colors.white70)),
        const SizedBox(height: 4),
        Text(
          value,
          style: theme.textTheme.bodyLarge?.copyWith(
            fontWeight: FontWeight.bold,
            color: valueColor ?? theme.colorScheme.onSurface,
          ),
        ),
      ],
    );
  }
}
