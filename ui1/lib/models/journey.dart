class Journey {
  final String id;
  final DateTime date;
  final String from;
  final String to;

  Journey({required this.id, required this.date, required this.from, required this.to});

  bool get isUpcoming => date.isAfter(DateTime.now());

  // Convert Journey to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'date': date.toIso8601String(),
      'from': from,
      'to': to,
    };
  }

  // Create Journey from JSON
  factory Journey.fromJson(Map<String, dynamic> json) {
    return Journey(
      id: json['id'] as String,
      date: DateTime.parse(json['date'] as String),
      from: json['from'] as String,
      to: json['to'] as String,
    );
  }
}

