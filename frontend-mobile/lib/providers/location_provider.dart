import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';

final locationProvider = FutureProvider<LatLng>((ref) async {
  bool serviceEnabled;
  LocationPermission permission;

  serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) {
    // Default to New Delhi if service is disabled
    return const LatLng(28.6139, 77.2090);
  }

  permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied) {
      return const LatLng(28.6139, 77.2090);
    }
  }

  if (permission == LocationPermission.deniedForever) {
    return const LatLng(28.6139, 77.2090);
  }

  try {
    Position position = await Geolocator.getCurrentPosition();
    return LatLng(position.latitude, position.longitude);
  } catch (e) {
    return const LatLng(28.6139, 77.2090);
  }
});
