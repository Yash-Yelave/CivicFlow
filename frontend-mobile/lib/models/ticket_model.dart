class Ticket {
  final String ticketId;
  final String imageUrl;
  final double latitude;
  final double longitude;
  final String? description;
  final String status;
  final int upvotes;
  final Agent1Assessment agent1Assessment;
  final Agent2Routing agent2Routing;
  final String createdAt;

  const Ticket({
    required this.ticketId,
    required this.imageUrl,
    required this.latitude,
    required this.longitude,
    this.description,
    required this.status,
    required this.upvotes,
    required this.agent1Assessment,
    required this.agent2Routing,
    required this.createdAt,
  });

  factory Ticket.fromJson(Map<String, dynamic> json) {
    return Ticket(
      ticketId: json['ticket_id'] as String,
      imageUrl: json['image_url'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      description: json['description'] as String?,
      status: json['status'] as String? ?? 'Pending',
      upvotes: json['upvotes'] as int? ?? 1,
      agent1Assessment: Agent1Assessment.fromJson(json['agent1_assessment'] as Map<String, dynamic>),
      agent2Routing: Agent2Routing.fromJson(json['agent2_routing'] as Map<String, dynamic>),
      createdAt: json['created_at'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'ticket_id': ticketId,
      'image_url': imageUrl,
      'latitude': latitude,
      'longitude': longitude,
      'description': description,
      'status': status,
      'upvotes': upvotes,
      'agent1_assessment': agent1Assessment.toJson(),
      'agent2_routing': agent2Routing.toJson(),
      'created_at': createdAt,
    };
  }
}

class Agent1Assessment {
  final String issueTitle;
  final String category;
  final int severityLevel;
  final String visualSummary;

  const Agent1Assessment({
    required this.issueTitle,
    required this.category,
    required this.severityLevel,
    required this.visualSummary,
  });

  factory Agent1Assessment.fromJson(Map<String, dynamic> json) {
    return Agent1Assessment(
      issueTitle: json['issue_title'] as String,
      category: json['category'] as String,
      severityLevel: json['severity_level'] as int,
      visualSummary: json['visual_summary'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'issue_title': issueTitle,
      'category': category,
      'severity_level': severityLevel,
      'visual_summary': visualSummary,
    };
  }
}

class Agent2Routing {
  final String assignedDepartment;
  final String ticketPriority;
  final String recommendedAction;
  final String estimatedResolutionTime;

  const Agent2Routing({
    required this.assignedDepartment,
    required this.ticketPriority,
    required this.recommendedAction,
    required this.estimatedResolutionTime,
  });

  factory Agent2Routing.fromJson(Map<String, dynamic> json) {
    return Agent2Routing(
      assignedDepartment: json['assigned_department'] as String,
      ticketPriority: json['ticket_priority'] as String,
      recommendedAction: json['recommended_action'] as String,
      estimatedResolutionTime: json['estimated_resolution_time'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'assigned_department': assignedDepartment,
      'ticket_priority': ticketPriority,
      'recommended_action': recommendedAction,
      'estimated_resolution_time': estimatedResolutionTime,
    };
  }
}
