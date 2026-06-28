import 'package:dio/dio.dart';
import '../../models/ticket_model.dart';
import '../core/network/api_client.dart';
import '../core/constants/app_constants.dart';

class ReportService {
  final ApiClient _apiClient;

  ReportService(this._apiClient);

  Future<Ticket> submitReport({
    required String filePath,
    required double latitude,
    required double longitude,
    String? description,
  }) async {
    // Note: Actual multipart file uploading implementation is deferred.
    // This is the architectural foundation.
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath, filename: 'report_image.jpg'),
      'latitude': latitude,
      'longitude': longitude,
      if (description != null) 'description': description,
    });

    final Response response = await _apiClient.post(
      AppConstants.endpointReport,
      data: formData,
    );

    final data = response.data;
    if (data['success'] == true && data['ticket'] != null) {
      return Ticket.fromJson(data['ticket']);
    } else {
      throw Exception(data['message'] ?? 'Failed to submit report');
    }
  }
}
