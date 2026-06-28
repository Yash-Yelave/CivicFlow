import '../../models/ticket_model.dart';
import '../services/ticket_service.dart';

class TicketRepository {
  final TicketService _ticketService;

  TicketRepository(this._ticketService);

  Future<List<Ticket>> getTickets() async {
    return await _ticketService.fetchTickets();
  }

  Future<int> verifyTicket(String ticketId) async {
    return await _ticketService.verifyTicket(ticketId);
  }
}
