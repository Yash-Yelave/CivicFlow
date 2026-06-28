import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../routes/app_router.dart';

class CivicFlowApp extends StatelessWidget {
  const CivicFlowApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'CivicFlow',
      theme: AppTheme.light,
      routerConfig: appRouter,
      debugShowCheckedModeBanner: false,
    );
  }
}
