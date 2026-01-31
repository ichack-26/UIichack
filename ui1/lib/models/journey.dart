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
  });

  bool get isUpcoming => date.isAfter(DateTime.now());

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
    };
  }

  // Create Journey from JSON
  factory Journey.fromJson(Map<String, dynamic> json) {
    final pointsList = (json['polylinePoints'] as List<dynamic>?)
        ?.map((p) => Map<String, double>.from(p as Map))
        .toList() ?? [];
    
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
    );
  }
}

