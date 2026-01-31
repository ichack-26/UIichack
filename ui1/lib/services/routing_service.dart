import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:math';
import 'package:latlong2/latlong.dart';
import 'package:ui1/models/journey.dart';

class RoutingService {
  // Use OpenRouteService (free tier available)
  // Sign up at: https://openrouteservice.org
  static const String _openRouteServiceKey = 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjdlYjJlODU0MGE2YzQyODg4ZDljZGRkNzkxNDcyYmEzIiwiaCI6Im11cm11cjY0In0=';
  static const String _openRouteServiceUrl = 'https://api.openrouteservice.org/v2/directions';

  /// Get detailed turn-by-turn directions for a route
  static Future<RouteDetails> getRouteDetails(
    LatLng start,
    LatLng end, {
    List<LatLng>? waypoints,
  }) async {
    try {
      if (_openRouteServiceKey == 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjdlYjJlODU0MGE2YzQyODg4ZDljZGRkNzkxNDcyYmEzIiwiaCI6Im11cm11cjY0In0=') {
        throw Exception(
          'API key not configured. '
          'Sign up at https://openrouteservice.org and add your key to routing_service.dart line 10'
        );
      }
      
      // Build coordinates array
      final coords = [
        [start.longitude, start.latitude],
        if (waypoints != null)
          ...waypoints.map((w) => [w.longitude, w.latitude]),
        [end.longitude, end.latitude],
      ];

      // Use OpenRouteService for detailed routing
      final url = Uri.parse(
        '$_openRouteServiceUrl/driving-car?'
        'api_key=$_openRouteServiceKey'
      );

      print('Requesting route from OpenRouteService...');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'coordinates': coords,
          'extra_info': ['waytype', 'steepness'],
          'format': 'json',
        }),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print('Route fetched successfully');
        return _parseOpenRouteServiceResponse(data, start, end);
      } else {
        print('Route error: ${response.statusCode} - ${response.body}');
        throw Exception('Failed to get route: ${response.statusCode} - ${response.reasonPhrase}');
      }
    } catch (e) {
      print('Routing error: $e');
      throw Exception('Routing error: $e');
    }
  }

  /// Snap user location to the nearest road/route
  static Future<LatLng> snapToRoad(LatLng location) async {
    try {
      final url = Uri.parse(
        '${_openRouteServiceUrl.replaceFirst('/directions', '/snap')}'
        '?api_key=$_openRouteServiceKey'
      );

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'coordinates': [[location.longitude, location.latitude]],
        }),
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['snapped_coordinates'] != null &&
            (data['snapped_coordinates'] as List).isNotEmpty) {
          final coord = data['snapped_coordinates'][0];
          return LatLng(coord[1], coord[0]);
        }
      }
      return location; // Return original if snapping fails
    } catch (e) {
      return location;
    }
  }

  /// Get distance matrix between multiple points
  static Future<DistanceMatrix> getDistanceMatrix(
    List<LatLng> origins,
    List<LatLng> destinations,
  ) async {
    try {
      final coords = [
        ...origins.map((o) => [o.longitude, o.latitude]),
        ...destinations.map((d) => [d.longitude, d.latitude]),
      ];

      final url = Uri.parse(
        'https://api.openrouteservice.org/v2/matrix/driving-car'
        '?api_key=$_openRouteServiceKey'
      );

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'locations': coords,
          'metrics': ['distance', 'duration'],
        }),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return DistanceMatrix.fromJson(data);
      }
      throw Exception('Failed to get distance matrix');
    } catch (e) {
      throw Exception('Distance matrix error: $e');
    }
  }

  static RouteDetails _parseOpenRouteServiceResponse(
    Map<String, dynamic> data,
    LatLng start,
    LatLng end,
  ) {
    final routes = data['routes'] as List;
    if (routes.isEmpty) {
      throw Exception('No routes found');
    }

    final route = routes[0] as Map<String, dynamic>;
    final segments = (route['segments'] as List?) ?? [];
    final steps = <NavigationStep>[];

    int stepIndex = 0;
    double cumulativeDistance = 0;

    for (final segment in segments) {
      final segmentSteps = (segment['steps'] as List?) ?? [];

      for (final step in segmentSteps) {
        final instruction = step['instruction'] as String?;
        final distance = (step['distance'] as num?)?.toDouble() ?? 0;
        final duration = (step['duration'] as num?)?.toDouble() ?? 0;
        final wayName = step['name'] as String?;

        if (instruction != null && distance > 0) {
          cumulativeDistance += distance;
          steps.add(
            NavigationStep(
              index: stepIndex++,
              instruction: instruction,
              distance: distance,
              duration: duration,
              cumulativeDistance: cumulativeDistance,
              wayName: wayName,
            ),
          );
        }
      }
    }

    // Extract polyline
    final polylinePoints = <LatLng>[];
    if (route['geometry'] is String) {
      // Decode polyline if encoded
      polylinePoints.addAll(_decodePolyline(route['geometry'] as String));
    } else if (route['geometry'] is List) {
      polylinePoints.addAll(
        (route['geometry'] as List).map(
          (coord) => LatLng(coord[1] as double, coord[0] as double),
        ),
      );
    }

    return RouteDetails(
      startPoint: start,
      endPoint: end,
      totalDistance: (route['distance'] as num?)?.toDouble() ?? 0,
      totalDuration: (route['duration'] as num?)?.toDouble() ?? 0,
      polylinePoints: polylinePoints,
      steps: steps,
      bounds: _getBounds(polylinePoints),
    );
  }

  static List<LatLng> _decodePolyline(String encoded) {
    final points = <LatLng>[];
    int index = 0, lat = 0, lng = 0;

    while (index < encoded.length) {
      int result = 0, shift = 0;
      int byte;
      do {
        byte = encoded.codeUnitAt(index++) - 63;
        result |= (byte & 0x1f) << shift;
        shift += 5;
      } while (byte >= 0x20);
      int dlat = ((result & 1) != 0) ? ~(result >> 1) : (result >> 1);
      lat += dlat;

      result = 0;
      shift = 0;
      do {
        byte = encoded.codeUnitAt(index++) - 63;
        result |= (byte & 0x1f) << shift;
        shift += 5;
      } while (byte >= 0x20);
      int dlng = ((result & 1) != 0) ? ~(result >> 1) : (result >> 1);
      lng += dlng;

      points.add(LatLng(lat / 1e5, lng / 1e5));
    }
    return points;
  }

  static RouteBounds _getBounds(List<LatLng> points) {
    if (points.isEmpty) return RouteBounds.zero();

    double minLat = points.first.latitude;
    double maxLat = points.first.latitude;
    double minLng = points.first.longitude;
    double maxLng = points.first.longitude;

    for (final point in points) {
      minLat = minLat > point.latitude ? point.latitude : minLat;
      maxLat = maxLat < point.latitude ? point.latitude : maxLat;
      minLng = minLng > point.longitude ? point.longitude : minLng;
      maxLng = maxLng < point.longitude ? point.longitude : maxLng;
    }

    return RouteBounds(
      southwest: LatLng(minLat, minLng),
      northeast: LatLng(maxLat, maxLng),
    );
  }
}

class RouteDetails {
  final LatLng startPoint;
  final LatLng endPoint;
  final double totalDistance; // in meters
  final double totalDuration; // in seconds
  final List<LatLng> polylinePoints;
  final List<NavigationStep> steps;
  final RouteBounds bounds;

  RouteDetails({
    required this.startPoint,
    required this.endPoint,
    required this.totalDistance,
    required this.totalDuration,
    required this.polylinePoints,
    required this.steps,
    required this.bounds,
  });

  String get totalDistanceStr {
    if (totalDistance < 1000) {
      return '${totalDistance.toStringAsFixed(0)}m';
    }
    return '${(totalDistance / 1000).toStringAsFixed(1)}km';
  }

  String get totalDurationStr {
    final hours = (totalDuration / 3600).floor();
    final minutes = ((totalDuration % 3600) / 60).floor();
    if (hours > 0) {
      return '$hours h $minutes min';
    }
    return '$minutes min';
  }
}

class NavigationStep {
  final int index;
  final String instruction;
  final double distance; // in meters
  final double duration; // in seconds
  final double cumulativeDistance;
  final String? wayName;

  NavigationStep({
    required this.index,
    required this.instruction,
    required this.distance,
    required this.duration,
    required this.cumulativeDistance,
    this.wayName,
  });

  String get distanceStr {
    if (distance < 100) {
      return '${distance.toStringAsFixed(0)}m';
    } else if (distance < 1000) {
      return '${(distance / 100).round() * 100}m';
    }
    return '${(distance / 1000).toStringAsFixed(1)}km';
  }

  String get durationStr {
    final minutes = (duration / 60).round();
    if (minutes < 1) return '< 1 min';
    return '$minutes min';
  }
}

class DistanceMatrix {
  final List<List<double>> distances; // in meters
  final List<List<double>> durations; // in seconds

  DistanceMatrix({
    required this.distances,
    required this.durations,
  });

  factory DistanceMatrix.fromJson(Map<String, dynamic> json) {
    final distances = (json['distances'] as List?)
            ?.map((row) => (row as List).cast<double>().toList())
            .toList() ??
        [];
    final durations = (json['durations'] as List?)
            ?.map((row) => (row as List).cast<double>().toList())
            .toList() ??
        [];

    return DistanceMatrix(
      distances: distances,
      durations: durations,
    );
  }
}

class RouteBounds {
  final LatLng southwest;
  final LatLng northeast;

  RouteBounds({
    required this.southwest,
    required this.northeast,
  });

  factory RouteBounds.zero() {
    return RouteBounds(
      southwest: const LatLng(0, 0),
      northeast: const LatLng(0, 0),
    );
  }

  LatLng get center => LatLng(
    (southwest.latitude + northeast.latitude) / 2,
    (southwest.longitude + northeast.longitude) / 2,
  );
}
