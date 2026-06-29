import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/ticket_model.dart';
import 'data_providers.dart';

final ticketsProvider = AsyncNotifierProvider<TicketsNotifier, List<Ticket>>(() {
  return TicketsNotifier();
});

class TicketsNotifier extends AsyncNotifier<List<Ticket>> {
  @override
  Future<List<Ticket>> build() async {
    return _fetchTickets();
  }

  Future<List<Ticket>> _fetchTickets() async {
    try {
      final repository = ref.read(ticketRepositoryProvider);
      return await repository.getTickets();
    } catch (e) {
      // Fallback to demo data matching the React app if the backend is down
      return [
        Ticket(
          ticketId: 'demo-1',
          latitude: 28.6139,
          longitude: 77.2090,
          upvotes: 12,
          status: 'Pending',
          description: 'High pressure water main rupture near Sector 4 intersection.',
          imageUrl: '',
          createdAt: DateTime.now().toIso8601String(),
          agent1Assessment: const Agent1Assessment(
            issueTitle: 'Major Water Main Pipe Burst',
            category: 'Water Leak',
            severityLevel: 5,
            visualSummary: 'Significant water flow detected on road surface indicating pipe failure.',
          ),
          agent2Routing: const Agent2Routing(
            assignedDepartment: 'Water & Sanitation Department',
            ticketPriority: 'CRITICAL',
            recommendedAction: 'Dispatch emergency repair crew immediately.',
            estimatedResolutionTime: '4-6 hours',
          ),
        ),
        Ticket(
          ticketId: 'demo-2',
          latitude: 28.6200,
          longitude: 77.2150,
          upvotes: 8,
          status: 'Pending',
          description: 'Complete loss of power to synchronized traffic signals.',
          imageUrl: '',
          createdAt: DateTime.now().toIso8601String(),
          agent1Assessment: const Agent1Assessment(
            issueTitle: 'Traffic Signal Network Failure',
            category: 'Streetlight',
            severityLevel: 4,
            visualSummary: 'Multiple traffic lights dark across main arterial road.',
          ),
          agent2Routing: const Agent2Routing(
            assignedDepartment: 'Electrical & Streetlight Department',
            ticketPriority: 'HIGH',
            recommendedAction: 'Deploy traffic wardens and inspect grid relay box.',
            estimatedResolutionTime: '24-48 hours',
          ),
        ),
        Ticket(
          ticketId: 'demo-3',
          latitude: 28.6050,
          longitude: 77.2000,
          upvotes: 45,
          status: 'Pending',
          description: 'Deep longitudinal cracking on primary bridge support pillar.',
          imageUrl: '',
          createdAt: DateTime.now().toIso8601String(),
          agent1Assessment: const Agent1Assessment(
            issueTitle: 'Structural Bridge Crack — Critical',
            category: 'Structural Damage',
            severityLevel: 5,
            visualSummary: 'Horizontal cracking visible on load-bearing column, indicating structural fatigue.',
          ),
          agent2Routing: const Agent2Routing(
            assignedDepartment: 'Urban Planning Department',
            ticketPriority: 'CRITICAL',
            recommendedAction: 'Immediately close bridge to traffic and deploy structural engineers.',
            estimatedResolutionTime: 'Emergency response — 1-3 days',
          ),
        )
      ];
    }
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchTickets());
  }

  void addTicket(Ticket ticket) {
    if (state.hasValue) {
      state = AsyncValue.data([ticket, ...state.value!]);
    }
  }

  void updateUpvotes(String ticketId, int newCount) {
    if (state.hasValue) {
      final updatedList = state.value!.map((t) {
        if (t.ticketId == ticketId) {
          return Ticket(
            ticketId: t.ticketId,
            imageUrl: t.imageUrl,
            latitude: t.latitude,
            longitude: t.longitude,
            description: t.description,
            status: t.status,
            upvotes: newCount,
            agent1Assessment: t.agent1Assessment,
            agent2Routing: t.agent2Routing,
            createdAt: t.createdAt,
          );
        }
        return t;
      }).toList();
      state = AsyncValue.data(updatedList);
    }
  }
}
