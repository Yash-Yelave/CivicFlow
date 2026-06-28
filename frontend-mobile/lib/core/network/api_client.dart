import 'package:dio/dio.dart';
import '../constants/app_constants.dart';

class ApiClient {
  late final Dio _dio;

  ApiClient() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.apiBaseUrl,
        connectTimeout: const Duration(milliseconds: AppConstants.connectTimeoutMs),
        receiveTimeout: const Duration(milliseconds: AppConstants.receiveTimeoutMs),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Logging Interceptor for Debugging
    _dio.interceptors.add(
      LogInterceptor(
        request: true,
        requestHeader: true,
        requestBody: true,
        responseHeader: false,
        responseBody: true,
        error: true,
      ),
    );

    // Custom Error Interceptor
    _dio.interceptors.add(
      InterceptorsWrapper(
        onError: (DioException e, ErrorInterceptorHandler handler) {
          // Custom error mapping could go here.
          return handler.next(e);
        },
      ),
    );
  }

  /// Perform a GET request
  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) async {
    try {
      return await _dio.get(path, queryParameters: queryParameters);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Perform a POST request
  Future<Response> post(String path, {dynamic data}) async {
    try {
      return await _dio.post(path, data: data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Perform a PATCH request
  Future<Response> patch(String path, {dynamic data}) async {
    try {
      return await _dio.patch(path, data: data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(DioException error) {
    String message = "An unknown error occurred.";
    if (error.type == DioExceptionType.connectionTimeout || 
        error.type == DioExceptionType.receiveTimeout) {
      message = "Connection timed out. Please check your internet connection.";
    } else if (error.type == DioExceptionType.badResponse) {
      message = "Server returned an error: ${error.response?.statusCode}.";
      if (error.response?.data != null && error.response?.data is Map) {
         final data = error.response?.data as Map;
         if (data.containsKey('message')) {
           message = data['message'];
         }
      }
    } else if (error.type == DioExceptionType.connectionError) {
      message = "No internet connection. Please verify your network.";
    }
    return Exception(message);
  }
}
