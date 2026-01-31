class Journey {
  final String id;
  final DateTime date;
  final String from;
  final String to;
  final double fromLat;
  final double fromLng;
  final double toLat;
  final double toLng;

  Journey({
    required this.id,
    required this.date,
    required this.from,
    required this.to,
    required this.fromLat,
    required this.fromLng,
    required this.toLat,
    required this.toLng,
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
    };
  }

  // Create Journey from JSON
  factory Journey.fromJson(Map<String, dynamic> json) {
    return Journey(
      id: json['id'] as String,
      date: DateTime.parse(json['date'] as String),
      from: json['from'] as String,
      to: json['to'] as String,
      fromLat: json['fromLat'] as double,
      fromLng: json['fromLng'] as double,
      toLat: json['toLat'] as double,
      toLng: json['toLng'] as double,
    );
  }
}

