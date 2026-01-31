class Journey {
  final String id;
  final DateTime date;
  final String from;
  final String to;

  Journey({required this.id, required this.date, required this.from, required this.to});

  bool get isUpcoming => date.isAfter(DateTime.now());
}
