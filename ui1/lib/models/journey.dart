class RouteStep {
  final String mode;
  final String? line;
  final String fromStation;
  final String toStation;
  final int durationMinutes;
  final String instructions;

  RouteStep({
    required this.mode,
    this.line,
    required this.fromStation,
    required this.toStation,
    required this.durationMinutes,
    required this.instructions,
  });

  Map<String, dynamic> toJson() {
    return {
      'mode': mode,
      'line': line,
      'from_station': fromStation,
      'to_station': toStation,
      'duration_minutes': durationMinutes,
      'instructions': instructions,
    };
  }

  factory RouteStep.fromJson(Map<String, dynamic> json) {
    // Handle empty string for line (convert to null)
    final lineValue = json['line'];
    final line = (lineValue == null || lineValue == '') ? null : lineValue as String;
    
    return RouteStep(
      mode: json['mode'] as String? ?? 'walking',
      line: line,
      fromStation: json['from_station'] as String? ?? '',
      toStation: json['to_station'] as String? ?? '',
      durationMinutes: json['duration_minutes'] as int? ?? 0,
      instructions: json['instructions'] as String? ?? '',
    );
  }
}

class Journey {
  final String id;
  final DateTime date;
  final String from;
  final String to;
  final double fromLat;
  final double fromLng;
  final double toLat;
  final double toLng;
  final List<Map<String, double>> polylinePoints; // Stores route waypoints
  final String? imageUrl; // URL to a route-relevant image
  final int? durationMinutes; // Estimated journey duration in minutes
  final List<RouteStep>? steps; // Route steps from API

  Journey({
    required this.id,
    required this.date,
    required this.from,
    required this.to,
    required this.fromLat,
    required this.fromLng,
    required this.toLat,
    required this.toLng,
    required this.polylinePoints,
    this.imageUrl,
    this.durationMinutes,
    this.steps,
  });

  bool get isUpcoming => date.isAfter(DateTime.now());
  
  bool get isOngoing {
    final now = DateTime.now();
    if (durationMinutes == null) return false;
    final endTime = date.add(Duration(minutes: durationMinutes!));
    return now.isAfter(date) && now.isBefore(endTime);
  }
  
  bool get isFinished {
    final now = DateTime.now();
    if (durationMinutes == null) return date.isBefore(now);
    final endTime = date.add(Duration(minutes: durationMinutes!));
    return now.isAfter(endTime);
  }

  // Convert Journey to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'date': date.toIso8601String(),
      'from': from,
      'to': to,
      'fromLat': fromLat,
      'fromLng': fromLng,
      'toLat': toLat,
      'toLng': toLng,
      'polylinePoints': polylinePoints,
      'imageUrl': imageUrl,
      'durationMinutes': durationMinutes,
      'steps': steps?.map((s) => s.toJson()).toList(),
    };
  }

  // Create Journey from JSON
  factory Journey.fromJson(Map<String, dynamic> json) {
    final pointsList = (json['polylinePoints'] as List<dynamic>?)
        ?.map((p) => Map<String, double>.from(p as Map))
        .toList() ?? [];
    
    final stepsList = (json['steps'] as List<dynamic>?)
        ?.map((s) => RouteStep.fromJson(s as Map<String, dynamic>))
        .toList();
    
    return Journey(
      id: json['id'] as String,
      date: DateTime.parse(json['date'] as String),
      from: json['from'] as String,
      to: json['to'] as String,
      fromLat: json['fromLat'] as double,
      fromLng: json['fromLng'] as double,
      toLat: json['toLat'] as double,
      toLng: json['toLng'] as double,
      polylinePoints: pointsList,
      imageUrl: json['imageUrl'] as String?,
      durationMinutes: json['durationMinutes'] as int?,
      steps: stepsList,
    );
  }
}

