import 'package:flutter/material.dart';

class TravelRouteSummaryWidget extends StatelessWidget {
  const TravelRouteSummaryWidget({
    super.key,
    required this.travelDate,
    required this.fromLocation,
    required this.toLocation,
    this.isUpcoming = false,
    this.onTap,
  });

  final DateTime travelDate;
  final String fromLocation; // todo - define types properly
  final String toLocation;
  final bool isUpcoming;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final dateLabel = travelDate.toLocal().toString().split(' ')[0];

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16.0),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8.0),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withAlpha(77),
              spreadRadius: 2,
              blurRadius: 5,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Travel Date: $dateLabel',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Chip(
                  label: Text(isUpcoming ? 'Upcoming' : 'Past'),
                  backgroundColor: isUpcoming ? Colors.green.shade100 : Colors.grey.shade200,
                ),
              ],
            ),
          const SizedBox(height: 8.0),
          Text(
            'From: $fromLocation',
            style: const TextStyle(fontSize: 14),
          ),
          const SizedBox(height: 4.0),
          Text(
            'To: $toLocation',
            style: const TextStyle(fontSize: 14),
          ),
        ],
      ),
      ),
    );
  }
}