class AppConstants {
  AppConstants._();

  // API Base URL - Placeholder for now, typically loaded from env variables
  static const String apiBaseUrl = 'http://10.0.2.2:8000/api/';

  // API Endpoints
  static const String endpointReport = 'report';
  static const String endpointTickets = 'tickets';
  static const String endpointAnalytics = 'analytics';
  static const String endpointAnalyticsRegenerate = 'analytics/regenerate';

  // Request Timeouts
  static const int connectTimeoutMs = 15000; // 15 seconds
  static const int receiveTimeoutMs = 15000; // 15 seconds
}
