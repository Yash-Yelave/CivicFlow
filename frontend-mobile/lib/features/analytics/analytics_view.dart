import 'package:flutter/material.dart';

class AnalyticsView extends StatelessWidget {
  const AnalyticsView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Predictive Insights'),
      ),
      body: const Center(
        child: Text('Analytics Dashboard Placeholder'),
      ),
    );
  }
}
