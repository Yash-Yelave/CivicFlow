import '../../models/ticket_model.dart';
import '../services/report_service.dart';

class ReportRepository {
  final ReportService _reportService;

  ReportRepository(this._reportService);

  Future<Ticket> submitReport({
    required String filePath,
    required double latitude,
    required double longitude,
    String? description,
  }) async {
    return await _reportService.submitReport(
      filePath: filePath,
      latitude: latitude,
      longitude: longitude,
      description: description,
    );
  }
}
