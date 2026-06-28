class AnalyticsResponse {
  final bool success;
  final String cacheStatus;
  final String? generatedAt;
  final int ticketCountAnalyzed;
  final AnalyticsCache? analytics;

  const AnalyticsResponse({
    required this.success,
    required this.cacheStatus,
    this.generatedAt,
    required this.ticketCountAnalyzed,
    this.analytics,
  });

  factory AnalyticsResponse.fromJson(Map<String, dynamic> json) {
    return AnalyticsResponse(
      success: json['success'] as bool,
      cacheStatus: json['cache_status'] as String,
      generatedAt: json['generated_at'] as String?,
      ticketCountAnalyzed: json['ticket_count_analyzed'] as int? ?? 0,
      analytics: json['analytics'] != null ? AnalyticsCache.fromJson(json['analytics'] as Map<String, dynamic>) : null,
    );
  }
}

class AnalyticsCache {
  final String generatedAt;
  final int generatedForVersion;
  final String executiveSummary;
  final List<RiskCluster> riskClusters;
  final List<PreventativeRecommendation> recommendations;
  final List<HeatmapPoint>? heatmapData;
  final Map<String, dynamic>? departmentStatistics;
  final Map<String, dynamic>? categoryStatistics;

  const AnalyticsCache({
    required this.generatedAt,
    required this.generatedForVersion,
    required this.executiveSummary,
    required this.riskClusters,
    required this.recommendations,
    this.heatmapData,
    this.departmentStatistics,
    this.categoryStatistics,
  });

  factory AnalyticsCache.fromJson(Map<String, dynamic> json) {
    return AnalyticsCache(
      generatedAt: json['generatedAt'] ?? json['generated_at'] ?? '',
      generatedForVersion: json['generatedForVersion'] ?? 0,
      executiveSummary: json['executiveSummary'] ?? json['summary'] ?? '',
      riskClusters: (json['riskClusters'] ?? json['high_risk_clusters'] as List<dynamic>? ?? [])
          .map((e) => RiskCluster.fromJson(e as Map<String, dynamic>))
          .toList(),
      recommendations: (json['recommendations'] ?? json['preventative_recommendations'] as List<dynamic>? ?? [])
          .map((e) => PreventativeRecommendation.fromJson(e as Map<String, dynamic>))
          .toList(),
      heatmapData: (json['heatmapData'] as List<dynamic>?)
          ?.map((e) => HeatmapPoint.fromJson(e as Map<String, dynamic>))
          .toList(),
      departmentStatistics: json['departmentStatistics'] as Map<String, dynamic>?,
      categoryStatistics: json['categoryStatistics'] as Map<String, dynamic>?,
    );
  }
}

class RiskCluster {
  final String sector;
  final String issueType;
  final int reportCount;
  final String riskLevel;
  final String insight;

  const RiskCluster({
    required this.sector,
    required this.issueType,
    required this.reportCount,
    required this.riskLevel,
    required this.insight,
  });

  factory RiskCluster.fromJson(Map<String, dynamic> json) {
    return RiskCluster(
      sector: json['sector'] ?? json['cluster_name'] ?? '',
      issueType: json['issue_type'] ?? '',
      reportCount: json['report_count'] ?? 0,
      riskLevel: json['risk_level'] ?? '',
      insight: json['insight'] ?? json['description'] ?? '',
    );
  }
}

class PreventativeRecommendation {
  final String department;
  final String action;
  final String urgency;

  const PreventativeRecommendation({
    required this.department,
    required this.action,
    required this.urgency,
  });

  factory PreventativeRecommendation.fromJson(Map<String, dynamic> json) {
    return PreventativeRecommendation(
      department: json['department'] as String? ?? '',
      action: json['action'] as String? ?? '',
      urgency: json['urgency'] as String? ?? '',
    );
  }
}

class HeatmapPoint {
  final double lat;
  final double lng;
  final double weight;

  const HeatmapPoint({
    required this.lat,
    required this.lng,
    required this.weight,
  });

  factory HeatmapPoint.fromJson(Map<String, dynamic> json) {
    return HeatmapPoint(
      lat: (json['lat'] as num).toDouble(),
      lng: (json['lng'] as num).toDouble(),
      weight: (json['weight'] as num).toDouble(),
    );
  }
}
