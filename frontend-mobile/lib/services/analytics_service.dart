import 'package:dio/dio.dart';
import '../../models/analytics_model.dart';
import '../core/network/api_client.dart';
import '../core/constants/app_constants.dart';

class AnalyticsService {
  final ApiClient _apiClient;

  AnalyticsService(this._apiClient);

  Future<AnalyticsResponse> fetchAnalytics() async {
    final Response response = await _apiClient.get(AppConstants.endpointAnalytics);
    return AnalyticsResponse.fromJson(response.data);
  }

  Future<void> regenerateAnalytics() async {
    final Response response = await _apiClient.post(AppConstants.endpointAnalyticsRegenerate);
    final data = response.data;
    if (data['success'] != true) {
      throw Exception('Failed to trigger analytics regeneration');
    }
  }
}
