import 'package:equatable/equatable.dart';

class Signal extends Equatable {
  final String id;
  final String symbol;
  final String market; // "crypto" or "forex"
  final String direction; // "long" or "short"
  final List<double> entryPoint;
  final List<double> targets;
  final double stopLoss;
  final String status; // "active", "hit_target", "stopped"
  final DateTime createdAt;

  const Signal({
    required this.id,
    required this.symbol,
    required this.market,
    required this.direction,
    required this.entryPoint,
    required this.targets,
    required this.stopLoss,
    required this.status,
    required this.createdAt,
  });

  @override
  List<Object?> get props => [id, symbol, market, direction, entryPoint, targets, stopLoss, status, createdAt];
}
