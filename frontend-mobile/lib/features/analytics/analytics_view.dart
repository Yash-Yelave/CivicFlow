import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/analytics_provider.dart';
import '../../providers/ticket_provider.dart';
import '../../core/theme/app_theme.dart';
import 'predictive_card.dart';

class AnalyticsView extends ConsumerStatefulWidget {
  const AnalyticsView({super.key});

  @override
  ConsumerState<AnalyticsView> createState() => _AnalyticsViewState();
}

class _AnalyticsViewState extends ConsumerState<AnalyticsView> {
  @override
  Widget build(BuildContext context) {
    final analyticsAsync = ref.watch(analyticsProvider);
    final ticketsAsync = ref.watch(ticketsProvider);

    final isLoading = analyticsAsync.isLoading || ticketsAsync.isLoading;
    final ticketCount = ticketsAsync.valueOrNull?.length ?? 0;

    return Scaffold(
      backgroundColor: AppTheme.background,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            backgroundColor: AppTheme.background,
            scrolledUnderElevation: 1,
            surfaceTintColor: Colors.transparent,
            pinned: true,
            expandedHeight: 120,
            flexibleSpace: FlexibleSpaceBar(
              titlePadding: const EdgeInsets.only(left: 20, bottom: 16, right: 20),
              title: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Municipal Analytics',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF0F172A),
                      letterSpacing: -0.5,
                    ),
                  ),
                  if (!isLoading)
                    GestureDetector(
                      onTap: () {
                        ref.read(analyticsProvider.notifier).refresh();
                        ref.read(ticketsProvider.notifier).refresh();
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: AppTheme.border),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.refresh, size: 14, color: AppTheme.textSecondary),
                            const SizedBox(width: 4),
                            Text(
                              'Refresh',
                              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                    color: AppTheme.textSecondary,
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
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
              child: Text(
                'Real-time performance metrics & Agent 3 predictive intelligence.',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppTheme.textSecondary,
                    ),
              ),
            ),
          ),
          
          // ── Metric Highlights ──
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                _MetricCard(
                  label: 'Active Reports',
                  value: isLoading ? '...' : '$ticketCount',
                  icon: Icons.show_chart,
                  iconColor: const Color(0xFF3B82F6),
                  trend: 'Live from Firestore',
                ),
                const SizedBox(height: 12),
                const _MetricCard(
                  label: 'Autonomous Triage Success Rate',
                  value: '98.4%',
                  icon: Icons.check_circle_outline,
                  iconColor: const Color(0xFF10B981),
                  trend: 'Gemini Flash',
                ),
                const SizedBox(height: 12),
                const _MetricCard(
                  label: 'Average Routing Time',
                  value: '< 2s',
                  icon: Icons.bolt,
                  iconColor: const Color(0xFFF59E0B),
                  trend: 'Agent 1 + Agent 2',
                ),
                const SizedBox(height: 32),
                
                // ── Predictive Intelligence Header ──
                Row(
                  children: [
                    const Text(
                      'Predictive Intelligence',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF0F172A),
                        letterSpacing: -0.5,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFEEF2FF),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        'AGENT 3 ACTIVE',
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                              color: const Color(0xFF4F46E5),
                              fontWeight: FontWeight.w700,
                              letterSpacing: 1.2,
                              fontSize: 9,
                            ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),

                // ── States ──
                if (isLoading)
                  Container(
                    padding: const EdgeInsets.symmetric(vertical: 40),
                    alignment: Alignment.center,
                    child: Column(
                      children: [
                        const SizedBox(
                          width: 32,
                          height: 32,
                          child: CircularProgressIndicator(color: Color(0xFF818CF8)),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Agent 3 is analyzing infrastructure patterns...',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: AppTheme.textSecondary,
                                fontWeight: FontWeight.w500,
                              ),
                        ),
                      ],
                    ),
                  )
                else if (analyticsAsync.hasError)
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFEF2F2),
                      border: Border.all(color: const Color(0xFFFEE2E2)),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Column(
                      children: [
                        Text(
                          'Failed to load analytics data.',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: const Color(0xFFDC2626),
                                fontWeight: FontWeight.w500,
                              ),
                        ),
                        const SizedBox(height: 8),
                        GestureDetector(
                          onTap: () => ref.read(analyticsProvider.notifier).refresh(),
                          child: Text(
                            'Retry',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: const Color(0xFFEF4444),
                                  decoration: TextDecoration.underline,
                                ),
                          ),
                        ),
                      ],
                    ),
                  )
                else if (analyticsAsync.hasValue && analyticsAsync.value != null) ...[
                  // Executive Summary
                  if (analyticsAsync.value!.analytics!.executiveSummary.isNotEmpty)
                    Container(
                      padding: const EdgeInsets.all(20),
                      margin: const EdgeInsets.only(bottom: 24),
                      decoration: BoxDecoration(
                        color: AppTheme.surface,
                        border: Border.all(color: AppTheme.border),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'EXECUTIVE SUMMARY',
                            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                  color: AppTheme.textTertiary,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 1.2,
                                  fontSize: 10,
                                ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            analyticsAsync.value!.analytics!.executiveSummary,
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: AppTheme.textPrimary,
                                  height: 1.5,
                                ),
                          ),
                        ],
                      ),
                    ),
                  
                  // High Risk Clusters
                  if (analyticsAsync.value!.analytics!.riskClusters.isNotEmpty)
                    ...analyticsAsync.value!.analytics!.riskClusters.map((cluster) {
                      return PredictiveCard(
                        cluster: {
                          'title': '${cluster.issueType} — ${cluster.sector}',
                          'description': cluster.insight,
                          'impact': '${cluster.riskLevel} Risk · ${cluster.reportCount} reports',
                        },
                      );
                    }),
                  
                  // Preventative Recommendations
                  if (analyticsAsync.value!.analytics!.recommendations.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    const Text(
                      'Preventative Recommendations',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF0F172A),
                      ),
                    ),
                    const SizedBox(height: 16),
                    ...analyticsAsync.value!.analytics!.recommendations.map((rec) {
                      final isHigh = rec.urgency == 'HIGH' || rec.urgency == 'CRITICAL';
                      final isMedium = rec.urgency == 'MEDIUM';
                      
                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AppTheme.surface,
                          border: Border.all(color: AppTheme.border),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: isHigh ? const Color(0xFFFEF2F2) : isMedium ? const Color(0xFFFFFBEB) : const Color(0xFFF1F5F9),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Text(
                                rec.urgency,
                                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                      color: isHigh ? const Color(0xFFDC2626) : isMedium ? const Color(0xFFD97706) : AppTheme.textSecondary,
                                      fontWeight: FontWeight.w700,
                                      fontSize: 10,
                                    ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    rec.department.toUpperCase(),
                                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                          color: AppTheme.textTertiary,
                                          fontWeight: FontWeight.w700,
                                          letterSpacing: 1.2,
                                          fontSize: 10,
                                        ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    rec.action,
                                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                          color: AppTheme.textPrimary,
                                        ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    }),
                  ],
                  const SizedBox(height: 40),
                ] else
                  Container(
                    padding: const EdgeInsets.symmetric(vertical: 40),
                    alignment: Alignment.center,
                    child: Text(
                      'No risk clusters detected yet. Submit more reports to enable Agent 3 pattern analysis.',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppTheme.textTertiary,
                          ),
                      textAlign: TextAlign.center,
                    ),
                  ),
              ]),
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color iconColor;
  final String trend;

  const _MetricCard({
    required this.label,
    required this.value,
    required this.icon,
    required this.iconColor,
    required this.trend,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
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
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.background,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, size: 20, color: iconColor),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: AppTheme.background,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  trend,
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: AppTheme.textTertiary,
                        fontWeight: FontWeight.w500,
                      ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppTheme.textSecondary,
                  fontWeight: FontWeight.w500,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1E293B), // slate-800
              letterSpacing: -0.5,
            ),
          ),
        ],
      ),
    );
  }
}
