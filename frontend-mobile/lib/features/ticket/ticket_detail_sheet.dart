import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../models/ticket_model.dart';
import '../../providers/ticket_provider.dart';
import '../../repositories/ticket_repository.dart';
import '../../providers/data_providers.dart';
import '../../core/theme/app_theme.dart';
import '../../shared/status_chip.dart';

// Maps category to color exactly like IssueDetailPanel.jsx
Color _categoryIconColor(String category) {
  switch (category) {
    case 'Water Leak':
      return const Color(0xFF3B82F6); // blue-500
    case 'Streetlight':
      return const Color(0xFFF59E0B); // amber-500
    case 'Structural Damage':
      return const Color(0xFFEF4444); // red-500
    default:
      return AppTheme.textSecondary;
  }
}

IconData _categoryIcon(String category) {
  switch (category) {
    case 'Water Leak':
      return Icons.water_drop_outlined;
    case 'Streetlight':
      return Icons.bolt_outlined;
    case 'Structural Damage':
      return Icons.business_outlined;
    default:
      return Icons.shield_outlined;
  }
}

// Maps severity_level (1-5) → status string matching React's severityToStatus
String _severityToStatus(int level) {
  if (level >= 5) return 'Critical';
  if (level >= 4) return 'Severe';
  if (level >= 3) return 'Pending';
  return 'Resolved';
}

// Maps ticket_priority → colors matching priorityColor in IssueDetailPanel.jsx
Color _priorityBg(String priority) {
  switch (priority) {
    case 'CRITICAL':
      return const Color(0xFFFEF2F2);
    case 'HIGH':
      return const Color(0xFFFFFBEB);
    case 'MEDIUM':
      return const Color(0xFFEFF6FF);
    default:
      return const Color(0xFFF1F5F9);
  }
}

Color _priorityText(String priority) {
  switch (priority) {
    case 'CRITICAL':
      return const Color(0xFFDC2626);
    case 'HIGH':
      return const Color(0xFFD97706);
    case 'MEDIUM':
      return const Color(0xFF2563EB);
    default:
      return AppTheme.textSecondary;
  }
}

void showTicketDetailSheet(BuildContext context, Ticket ticket) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => TicketDetailSheet(ticket: ticket),
  );
}

class TicketDetailSheet extends ConsumerStatefulWidget {
  final Ticket ticket;

  const TicketDetailSheet({super.key, required this.ticket});

  @override
  ConsumerState<TicketDetailSheet> createState() => _TicketDetailSheetState();
}

class _TicketDetailSheetState extends ConsumerState<TicketDetailSheet> {
  bool _isVerifying = false;
  bool _hasVerified = false;
  String? _verifyError;

  Future<void> _handleVerify() async {
    if (_hasVerified || _isVerifying) return;
    setState(() {
      _isVerifying = true;
      _verifyError = null;
    });
    try {
      final repository = ref.read(ticketRepositoryProvider);
      final newCount = await repository.verifyTicket(widget.ticket.ticketId);
      ref.read(ticketsProvider.notifier).updateUpvotes(widget.ticket.ticketId, newCount);
      if (mounted) setState(() => _hasVerified = true);
    } catch (_) {
      if (mounted) setState(() => _verifyError = 'Could not verify. Please try again.');
    } finally {
      if (mounted) setState(() => _isVerifying = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final a1 = widget.ticket.agent1Assessment;
    final a2 = widget.ticket.agent2Routing;
    final upvotes = widget.ticket.upvotes;

    return DraggableScrollableSheet(
      initialChildSize: 0.92,
      maxChildSize: 0.96,
      minChildSize: 0.5,
      builder: (_, controller) {
        return Container(
          decoration: const BoxDecoration(
            color: AppTheme.surface,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: Column(
            children: [
              // Drag handle
              Container(
                margin: const EdgeInsets.only(top: 12, bottom: 8),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: AppTheme.border,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              // ── Header ──────────────────────────────────────────────────
              Container(
                padding: const EdgeInsets.fromLTRB(20, 8, 16, 16),
                decoration: const BoxDecoration(
                  border: Border(bottom: BorderSide(color: AppTheme.border)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              StatusChip(status: _severityToStatus(a1.severityLevel)),
                              const SizedBox(width: 8),
                              Icon(
                                _categoryIcon(a1.category),
                                size: 14,
                                color: _categoryIconColor(a1.category),
                              ),
                              const SizedBox(width: 4),
                              Text(
                                a1.category,
                                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                  color: AppTheme.textSecondary,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            a1.issueTitle,
                            style: Theme.of(context).textTheme.headlineSmall,
                          ),
                        ],
                      ),
                    ),
                    InkWell(
                      onTap: () => Navigator.of(context).pop(),
                      borderRadius: BorderRadius.circular(20),
                      child: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: AppTheme.background,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.close, size: 20, color: AppTheme.textSecondary),
                      ),
                    ),
                  ],
                ),
              ),
              // ── Scrollable Content ───────────────────────────────────────
              Expanded(
                child: ListView(
                  controller: controller,
                  padding: const EdgeInsets.all(20),
                  children: [
                    // Image area
                    ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: AspectRatio(
                        aspectRatio: 16 / 9,
                        child: Stack(
                          fit: StackFit.expand,
                          children: [
                            widget.ticket.imageUrl.isNotEmpty
                                ? CachedNetworkImage(
                                    imageUrl: widget.ticket.imageUrl,
                                    fit: BoxFit.cover,
                                    placeholder: (_, __) => Container(color: const Color(0xFFE2E8F0)),
                                    errorWidget: (_, __, ___) => Container(
                                      color: const Color(0xFFE2E8F0),
                                      child: const Icon(Icons.shield_outlined, size: 48, color: Color(0xFFCBD5E1)),
                                    ),
                                  )
                                : Container(
                                    color: const Color(0xFFE2E8F0),
                                    child: const Icon(Icons.shield_outlined, size: 48, color: Color(0xFFCBD5E1)),
                                  ),
                            // Severity badge
                            Positioned(
                              top: 12,
                              left: 12,
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.9),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  'Severity ${a1.severityLevel}/5',
                                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                    fontWeight: FontWeight.w700,
                                    color: AppTheme.textPrimary,
                                  ),
                                ),
                              ),
                            ),
                            // AI assessed badge
                            Positioned(
                              bottom: 12,
                              right: 12,
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.9),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    const Icon(Icons.check_circle_outline, size: 11, color: Color(0xFF6366F1)),
                                    const SizedBox(width: 4),
                                    Text(
                                      'AI Assessed',
                                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                        color: const Color(0xFF6366F1),
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    // Visual summary
                    if (a1.visualSummary.isNotEmpty)
                      Text(
                        a1.visualSummary,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: const Color(0xFF475569),
                          height: 1.6,
                        ),
                      ),
                    const SizedBox(height: 16),
                    // Citizen description
                    if (widget.ticket.description != null && widget.ticket.description!.isNotEmpty) ...[
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AppTheme.background,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppTheme.border),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'CITIZEN REPORT',
                              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                color: AppTheme.textTertiary,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 1.2,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(widget.ticket.description!, style: Theme.of(context).textTheme.bodyMedium),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],
                    // Department Routing Card
                    if (a2.assignedDepartment.isNotEmpty) ...[
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AppTheme.surface,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppTheme.border),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    'ROUTED TO',
                                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                      color: AppTheme.textTertiary,
                                      fontWeight: FontWeight.w700,
                                      letterSpacing: 1.2,
                                    ),
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: _priorityBg(a2.ticketPriority),
                                    borderRadius: BorderRadius.circular(20),
                                  ),
                                  child: Text(
                                    a2.ticketPriority,
                                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                      color: _priorityText(a2.ticketPriority),
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              a2.assignedDepartment,
                              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                color: AppTheme.textPrimary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              a2.recommendedAction,
                              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: AppTheme.textSecondary,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                const Icon(Icons.schedule_outlined, size: 12, color: Color(0xFF6366F1)),
                                const SizedBox(width: 4),
                                Text(
                                  'ETA: ${a2.estimatedResolutionTime}',
                                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: const Color(0xFF6366F1),
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],
                    // Autonomous Triage Tracker
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: AppTheme.background,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppTheme.border),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.info_outline, size: 16, color: Color(0xFF6366F1)),
                              const SizedBox(width: 8),
                              Text(
                                'Autonomous Triage Path',
                                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          _TriageStep(
                            label: 'Report Received',
                            sub: 'Auto-geolocated & logged in Firestore',
                            isDone: true,
                          ),
                          const SizedBox(height: 16),
                          _TriageStep(
                            label: 'Agent 1: Visual Assessment',
                            sub: '"${a1.issueTitle}" — ${a1.severityLevel}/5 severity',
                            isDone: true,
                          ),
                          const SizedBox(height: 16),
                          _TriageStep(
                            label: 'Agent 2: Department Routing',
                            sub: a2.assignedDepartment.isNotEmpty
                                ? 'Ticket created for ${a2.assignedDepartment}'
                                : 'Pending routing...',
                            isDone: a2.assignedDepartment.isNotEmpty,
                            isActive: a2.assignedDepartment.isEmpty,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    // Location
                    Row(
                      children: [
                        const Text('📍', style: TextStyle(fontSize: 12)),
                        const SizedBox(width: 8),
                        Text(
                          '${widget.ticket.latitude.toStringAsFixed(4)}, ${widget.ticket.longitude.toStringAsFixed(4)}',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppTheme.textTertiary,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
              // ── Sticky Verify Footer ─────────────────────────────────────
              Container(
                padding: EdgeInsets.fromLTRB(20, 16, 20, MediaQuery.of(context).padding.bottom + 16),
                decoration: const BoxDecoration(
                  color: AppTheme.surface,
                  border: Border(top: BorderSide(color: AppTheme.border)),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (_verifyError != null)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Text(
                          _verifyError!,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppTheme.error),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    GestureDetector(
                      onTap: _handleVerify,
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        decoration: BoxDecoration(
                          color: _hasVerified ? const Color(0xFFF0FDF4) : AppTheme.surface,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: _hasVerified ? const Color(0xFF86EFAC) : AppTheme.border,
                          ),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            if (_isVerifying) ...[
                              const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.textSecondary),
                              ),
                              const SizedBox(width: 8),
                              Text('Verifying...', style: Theme.of(context).textTheme.labelLarge?.copyWith(color: AppTheme.textSecondary)),
                            ] else if (_hasVerified) ...[
                              const Icon(Icons.check_circle_outline, size: 16, color: Color(0xFF16A34A)),
                              const SizedBox(width: 8),
                              Text('Verified — Thank you!', style: Theme.of(context).textTheme.labelLarge?.copyWith(color: const Color(0xFF16A34A), fontWeight: FontWeight.w600)),
                            ] else ...[
                              Text('Verify this issue', style: Theme.of(context).textTheme.labelLarge?.copyWith(color: AppTheme.textPrimary, fontWeight: FontWeight.w600)),
                              const SizedBox(width: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(
                                  color: AppTheme.background,
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text('$upvotes', style: Theme.of(context).textTheme.labelSmall?.copyWith(fontWeight: FontWeight.w700)),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _TriageStep extends StatelessWidget {
  final String label;
  final String sub;
  final bool isDone;
  final bool isActive;

  const _TriageStep({
    required this.label,
    required this.sub,
    required this.isDone,
    this.isActive = false,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 16,
          height: 16,
          margin: const EdgeInsets.only(top: 2),
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: isDone
                ? const Color(0xFF22C55E)
                : isActive
                    ? const Color(0xFF6366F1)
                    : const Color(0xFFE2E8F0),
          ),
          child: isDone
              ? const Icon(Icons.check_circle_outline, size: 10, color: Colors.white)
              : isActive
                  ? Center(
                      child: Container(
                        width: 6,
                        height: 6,
                        decoration: const BoxDecoration(shape: BoxShape.circle, color: Colors.white),
                      ),
                    )
                  : null,
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600)),
              Text(sub, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppTheme.textSecondary, height: 1.4)),
            ],
          ),
        ),
      ],
    );
  }
}
