import 'package:dio/dio.dart';
import '../../models/ticket_model.dart';
import '../core/network/api_client.dart';
import '../core/constants/app_constants.dart';

class TicketService {
  final ApiClient _apiClient;

  TicketService(this._apiClient);

  Future<List<Ticket>> fetchTickets() async {
    final Response response = await _apiClient.get(AppConstants.endpointTickets);
    final data = response.data;
    
    if (data['success'] == true && data['tickets'] != null) {
      final List<dynamic> ticketsJson = data['tickets'];
      return ticketsJson.map((json) => Ticket.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load tickets');
    }
  }

  Future<int> verifyTicket(String ticketId) async {
    final Response response = await _apiClient.patch('${AppConstants.endpointTickets}/$ticketId/verify');
    final data = response.data;
    
    if (data['success'] == true && data['new_upvote_count'] != null) {
      return data['new_upvote_count'] as int;
    } else {
      throw Exception('Failed to verify ticket');
    }
  }
}
