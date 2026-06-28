import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/network/api_client.dart';
import '../services/analytics_service.dart';
import '../services/report_service.dart';
import '../services/ticket_service.dart';
import '../repositories/analytics_repository.dart';
import '../repositories/report_repository.dart';
import '../repositories/ticket_repository.dart';

// --- Core ---
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

// --- Services ---
final ticketServiceProvider = Provider<TicketService>((ref) {
  return TicketService(ref.read(apiClientProvider));
});

final analyticsServiceProvider = Provider<AnalyticsService>((ref) {
  return AnalyticsService(ref.read(apiClientProvider));
});

final reportServiceProvider = Provider<ReportService>((ref) {
  return ReportService(ref.read(apiClientProvider));
});

// --- Repositories ---
final ticketRepositoryProvider = Provider<TicketRepository>((ref) {
  return TicketRepository(ref.read(ticketServiceProvider));
});

final analyticsRepositoryProvider = Provider<AnalyticsRepository>((ref) {
  return AnalyticsRepository(ref.read(analyticsServiceProvider));
});

final reportRepositoryProvider = Provider<ReportRepository>((ref) {
  return ReportRepository(ref.read(reportServiceProvider));
});
