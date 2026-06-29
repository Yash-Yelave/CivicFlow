import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/analytics_model.dart';
import 'data_providers.dart';

final analyticsProvider = AsyncNotifierProvider<AnalyticsNotifier, AnalyticsResponse?>(() {
  return AnalyticsNotifier();
});

class AnalyticsNotifier extends AsyncNotifier<AnalyticsResponse?> {
  @override
  Future<AnalyticsResponse?> build() async {
    return _fetchAnalytics();
  }

  Future<AnalyticsResponse?> _fetchAnalytics() async {
    try {
      final repository = ref.read(analyticsRepositoryProvider);
      return await repository.getAnalytics();
    } catch (e) {
      // Throw to let the UI handle the error state
      throw Exception('Failed to load analytics: $e');
    }
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchAnalytics());
  }
}
