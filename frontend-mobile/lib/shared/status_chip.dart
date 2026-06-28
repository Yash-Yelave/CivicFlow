import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';

class StatusChip extends StatelessWidget {
  final String status;

  const StatusChip({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    Color bgColor;
    Color textColor;

    switch (status.toLowerCase()) {
      case 'resolved':
      case 'completed':
        bgColor = AppTheme.successLight;
        textColor = AppTheme.success;
        break;
      case 'in progress':
        bgColor = AppTheme.warningLight;
        textColor = AppTheme.warning;
        break;
      case 'pending':
      case 'open':
      default:
        bgColor = AppTheme.accentLight;
        textColor = AppTheme.accent;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Text(
        status.toUpperCase(),
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: textColor,
              fontWeight: FontWeight.w700,
            ),
      ),
    );
  }
}
