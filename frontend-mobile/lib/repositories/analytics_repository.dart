import '../../models/analytics_model.dart';
import '../services/analytics_service.dart';

class AnalyticsRepository {
  final AnalyticsService _analyticsService;

  AnalyticsRepository(this._analyticsService);

  Future<AnalyticsResponse> getAnalytics() async {
    return await _analyticsService.fetchAnalytics();
  }

  Future<void> regenerateAnalytics() async {
    await _analyticsService.regenerateAnalytics();
  }
}
