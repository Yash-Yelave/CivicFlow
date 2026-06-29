import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../../providers/location_provider.dart';
import '../../providers/ticket_provider.dart';
import '../../providers/data_providers.dart';
import '../../repositories/report_repository.dart';
import '../../core/theme/app_theme.dart';
import 'package:go_router/go_router.dart';

class ReportView extends ConsumerStatefulWidget {
  const ReportView({super.key});

  @override
  ConsumerState<ReportView> createState() => _ReportViewState();
}

class _ReportViewState extends ConsumerState<ReportView> {
  File? _imageFile;
  String _description = '';
  bool _isSubmitting = false;
  int _currentStep = 0;
  String? _error;
  final ImagePicker _picker = ImagePicker();

  final List<Map<String, dynamic>> _triageSteps = [
    {'label': 'Uploading image to secure storage...', 'delay': 0},
    {'label': 'Agent 1: Analyzing infrastructure issue via Gemini Vision...', 'delay': 1500},
    {'label': 'Agent 2: Routing to correct municipal department...', 'delay': 4000},
    {'label': 'Saving ticket to database...', 'delay': 6000},
  ];

  Future<void> _pickImage(ImageSource source) async {
    try {
      final pickedFile = await _picker.pickImage(source: source, imageQuality: 80);
      if (pickedFile != null) {
        setState(() {
          _imageFile = File(pickedFile.path);
          _error = null;
        });
      }
    } catch (e) {
      setState(() => _error = 'Failed to pick image.');
    }
  }

  Future<void> _handleSubmit() async {
    if (_imageFile == null) {
      setState(() => _error = 'Please attach an image of the issue before submitting.');
      return;
    }

    final locationAsync = ref.read(locationProvider);
    if (!locationAsync.hasValue) {
      setState(() => _error = 'Waiting for location...');
      return;
    }

    setState(() {
      _error = null;
      _isSubmitting = true;
      _currentStep = 0;
    });

    // Simulate triage steps timing
    for (int i = 0; i < _triageSteps.length; i++) {
      Future.delayed(Duration(milliseconds: _triageSteps[i]['delay']), () {
        if (mounted && _isSubmitting) {
          setState(() => _currentStep = i);
        }
      });
    }

    try {
      final repository = ref.read(reportRepositoryProvider);
      final center = locationAsync.value!;
      final newTicket = await repository.submitReport(
        filePath: _imageFile!.path,
        latitude: center.latitude,
        longitude: center.longitude,
        description: _description,
      );

      ref.read(ticketsProvider.notifier).addTicket(newTicket);
      
      if (mounted) {
        // Reset form and go back to home tab
        setState(() {
          _imageFile = null;
          _description = '';
          _isSubmitting = false;
          _currentStep = 0;
        });
        context.go('/home');
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Submission failed. Please try again.';
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final locationAsync = ref.watch(locationProvider);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Report Issue',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
            ),
            const Text(
              'Powered by Gemini AI Multi-Agent System',
              style: TextStyle(fontSize: 12, color: AppTheme.textSecondary, fontWeight: FontWeight.w400),
            ),
          ],
        ),
      ),
      body: _isSubmitting ? _buildLoadingState() : _buildForm(locationAsync),
    );
  }

  Widget _buildLoadingState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SizedBox(
              width: 64,
              height: 64,
              child: CircularProgressIndicator(strokeWidth: 4, color: Color(0xFF6366F1)),
            ),
            const SizedBox(height: 40),
            ...List.generate(_triageSteps.length, (index) {
              final step = _triageSteps[index];
              final isPast = index < _currentStep;
              final isCurrent = index == _currentStep;

              return AnimatedOpacity(
                duration: const Duration(milliseconds: 300),
                opacity: isPast || isCurrent ? 1.0 : 0.3,
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Row(
                    children: [
                      Container(
                        width: 20,
                        height: 20,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: isPast
                              ? const Color(0xFF10B981) // emerald-500
                              : isCurrent
                                  ? const Color(0xFF6366F1) // indigo-500
                                  : const Color(0xFFE2E8F0), // slate-200
                        ),
                        child: isPast
                            ? const Icon(Icons.check, size: 12, color: Colors.white)
                            : isCurrent
                                ? Center(
                                    child: Container(
                                      width: 8,
                                      height: 8,
                                      decoration: const BoxDecoration(shape: BoxShape.circle, color: Colors.white),
                                    ),
                                  )
                                : null,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          step['label'],
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: isCurrent
                                    ? const Color(0xFF1E293B)
                                    : isPast
                                        ? const Color(0xFF059669)
                                        : AppTheme.textTertiary,
                                fontWeight: isCurrent ? FontWeight.w600 : FontWeight.normal,
                              ),
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildForm(AsyncValue locationAsync) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_error != null)
            Container(
              margin: const EdgeInsets.only(bottom: 20),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: const Color(0xFFFEF2F2),
                border: Border.all(color: const Color(0xFFFEE2E2)),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline, size: 16, color: Color(0xFFDC2626)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _error!,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(color: const Color(0xFFB91C1C)),
                    ),
                  ),
                ],
              ),
            ),

          // Image Dropzone Area
          GestureDetector(
            onTap: () {
              showModalBottomSheet(
                context: context,
                builder: (_) => SafeArea(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      ListTile(
                        leading: const Icon(Icons.camera_alt_outlined),
                        title: const Text('Take a photo'),
                        onTap: () {
                          Navigator.pop(context);
                          _pickImage(ImageSource.camera);
                        },
                      ),
                      ListTile(
                        leading: const Icon(Icons.photo_library_outlined),
                        title: const Text('Choose from gallery'),
                        onTap: () {
                          Navigator.pop(context);
                          _pickImage(ImageSource.gallery);
                        },
                      ),
                    ],
                  ),
                ),
              );
            },
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: _imageFile != null ? const Color(0xFFECFDF5).withOpacity(0.5) : AppTheme.surface,
                border: Border.all(
                  color: _imageFile != null ? const Color(0xFF6EE7B7) : AppTheme.border,
                  width: 2,
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: _imageFile != null
                  ? Column(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: Image.file(_imageFile!, height: 160, width: double.infinity, fit: BoxFit.cover),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.check_circle, size: 16, color: Color(0xFF10B981)),
                            const SizedBox(width: 6),
                            Text(
                              'Image attached',
                              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: const Color(0xFF059669),
                                    fontWeight: FontWeight.w600,
                                  ),
                            ),
                          ],
                        ),
                      ],
                    )
                  : Column(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: const BoxDecoration(
                            color: Color(0xFFEEF2FF),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.cloud_upload_outlined, size: 24, color: Color(0xFF6366F1)),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Tap to attach issue image',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'PNG, JPG, HEIC up to 10MB',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppTheme.textTertiary),
                        ),
                      ],
                    ),
            ),
          ),
          const SizedBox(height: 20),

          // Auto Geolocation
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.background,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.border),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppTheme.surface,
                    borderRadius: BorderRadius.circular(8),
                    boxShadow: const [BoxShadow(color: Color(0x0A000000), blurRadius: 4, offset: Offset(0, 2))],
                  ),
                  child: const Icon(Icons.place_outlined, size: 18, color: Color(0xFF10B981)),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'AUTO-DETECTED LOCATION',
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                              color: AppTheme.textTertiary,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 1.2,
                              fontSize: 10,
                            ),
                      ),
                      const SizedBox(height: 2),
                      locationAsync.when(
                        data: (center) => Text(
                          '${center.latitude.toStringAsFixed(4)}°, ${center.longitude.toStringAsFixed(4)}°',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                fontFamily: 'monospace',
                                fontWeight: FontWeight.w600,
                              ),
                        ),
                        loading: () => const Text('Detecting...'),
                        error: (_, __) => const Text('Location unavailable'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Description
          Text(
            'Description',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimary,
                ),
          ),
          const SizedBox(height: 8),
          TextField(
            maxLines: 4,
            onChanged: (val) => _description = val,
            decoration: InputDecoration(
              hintText: 'e.g., Large pothole causing traffic near the junction...',
              hintStyle: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppTheme.textTertiary),
              filled: true,
              fillColor: AppTheme.background,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppTheme.border),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppTheme.border),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFF818CF8)),
              ),
            ),
          ),
          const SizedBox(height: 32),

          // Submit Button
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: _imageFile == null ? null : _handleSubmit,
              style: FilledButton.styleFrom(
                backgroundColor: const Color(0xFF0F172A),
                disabledBackgroundColor: const Color(0xFF0F172A).withOpacity(0.5),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: const Text('Submit to AI Triage System'),
            ),
          ),
        ],
      ),
    );
  }
}
