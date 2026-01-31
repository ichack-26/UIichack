import 'package:flutter/material.dart';

class TravelRouteSummaryWidget extends StatelessWidget {
  const TravelRouteSummaryWidget({
    super.key,
    required this.travelDate,
    required this.fromLocation,
    required this.toLocation,
    this.isUpcoming = false,
    this.isOngoing = false,
    this.imageUrl,
    this.onTap,
  });

  final DateTime travelDate;
  final String fromLocation;
  final String toLocation;
  final bool isUpcoming;
  final bool isOngoing;
  final String? imageUrl;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final dateLabel = travelDate.toLocal().toString().split(' ')[0];
    final timeLabel = '${travelDate.hour}:${travelDate.minute.toString().padLeft(2, '0')}';
    final isPast = !isUpcoming && !isOngoing;
    final statusLabel = isOngoing ? 'Now' : (isUpcoming ? 'Upcoming' : 'Completed');
    final statusColor = isOngoing
      ? Colors.orange.withOpacity(0.85)
      : (isUpcoming ? Colors.green.withOpacity(0.8) : Colors.grey.withOpacity(0.6));

    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 200,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16.0),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              spreadRadius: 2,
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(16.0),
          child: Stack(
            children: [
              // Background image
              Positioned.fill(
                child: Image.network(
                  imageUrl ?? 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&h=400&fit=crop',
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) {
                    return Container(
                      color: Colors.blue.shade100,
                      child: const Icon(Icons.directions, size: 60, color: Colors.blue),
                    );
                  },
                ),
              ),
              // Dark overlay
              Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.black.withOpacity(0.3),
                      Colors.black.withOpacity(0.6),
                    ],
                  ),
                ),
              ),
              // Past overlay to grey out finished journeys
              if (isPast)
                Container(
                  color: Colors.grey.withOpacity(0.35),
                ),
              // Content
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Header with date and status
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              dateLabel,
                              style: const TextStyle(
                                fontSize: 14,
                                color: Colors.white70,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                            Text(
                              timeLabel,
                              style: TextStyle(
                                fontSize: 18,
                                color: isPast ? Colors.white70 : Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: statusColor,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            statusLabel,
                            style: const TextStyle(
                              fontSize: 12,
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    // Route information
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.location_on, color: Colors.white, size: 18),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                fromLocation,
                                style: TextStyle(
                                  fontSize: 14,
                                  color: isPast ? Colors.white70 : Colors.white,
                                  fontWeight: FontWeight.w500,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            const Icon(Icons.location_pin, color: Colors.white, size: 18),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                toLocation,
                                style: TextStyle(
                                  fontSize: 14,
                                  color: isPast ? Colors.white70 : Colors.white,
                                  fontWeight: FontWeight.w500,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              // Tap indicator
              Positioned(
                bottom: 8,
                right: 8,
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.9),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  padding: const EdgeInsets.all(8),
                  child: const Icon(
                    Icons.arrow_forward,
                    color: Colors.blue,
                    size: 20,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}