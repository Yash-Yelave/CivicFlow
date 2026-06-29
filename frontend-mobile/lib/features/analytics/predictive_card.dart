import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class PredictiveCard extends StatefulWidget {
  final Map<String, dynamic> cluster;

  const PredictiveCard({super.key, required this.cluster});

  @override
  State<PredictiveCard> createState() => _PredictiveCardState();
}

class _PredictiveCardState extends State<PredictiveCard> {
  String _status = 'idle'; // 'idle' | 'approving' | 'approved'

  void _handleApprove() {
    if (_status != 'idle') return;
    setState(() => _status = 'approving');
    Future.delayed(const Duration(milliseconds: 1200), () {
      if (mounted) setState(() => _status = 'approved');
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.border),
        boxShadow: const [
          BoxShadow(
            color: Color(0x05000000),
            blurRadius: 4,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFEEF2FF), // indigo-50
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.auto_awesome, size: 20, color: Color(0xFF4F46E5)), // indigo-600
                  ),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Agent 3 Prediction',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                              color: AppTheme.textPrimary,
                            ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEEF2FF),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          'High Confidence (94%)',
                          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                color: const Color(0xFF4F46E5),
                                fontWeight: FontWeight.w600,
                              ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEF2F2), // red-50
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.warning_amber_rounded, size: 20, color: Color(0xFFEF4444)), // red-500
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            widget.cluster['title'] ?? '',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Text(
            widget.cluster['description'] ?? '',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppTheme.textSecondary,
                  height: 1.5,
                ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text.rich(
                  TextSpan(
                    text: 'Impact: ',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppTheme.textTertiary),
                    children: [
                      TextSpan(
                        text: widget.cluster['impact'] ?? '',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: AppTheme.textPrimary,
                              fontWeight: FontWeight.w600,
                            ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 12),
              GestureDetector(
                onTap: _handleApprove,
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    color: _status == 'idle'
                        ? const Color(0xFF0F172A) // slate-900
                        : _status == 'approving'
                            ? const Color(0xFFEEF2FF) // indigo-50
                            : const Color(0xFF10B981), // emerald-500
                    borderRadius: BorderRadius.circular(12),
                    border: _status == 'approving'
                        ? Border.all(color: const Color(0xFFC7D2FE)) // indigo-200
                        : null,
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (_status == 'idle') ...[
                        Text(
                          'Approve',
                          style: Theme.of(context).textTheme.labelMedium?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.w600,
                              ),
                        ),
                        const SizedBox(width: 6),
                        const Icon(Icons.arrow_forward, size: 16, color: Colors.white),
                      ],
                      if (_status == 'approving') ...[
                        const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Color(0xFF4F46E5), // indigo-600
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'Approving...',
                          style: Theme.of(context).textTheme.labelMedium?.copyWith(
                                color: const Color(0xFF4F46E5),
                                fontWeight: FontWeight.w600,
                              ),
                        ),
                      ],
                      if (_status == 'approved') ...[
                        const Icon(Icons.check, size: 16, color: Colors.white),
                        const SizedBox(width: 6),
                        Text(
                          'Approved',
                          style: Theme.of(context).textTheme.labelMedium?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.w600,
                              ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
