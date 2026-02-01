import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:ui1/models/journey.dart';
import 'package:intl/intl.dart';

class JourneyDetailsPage extends StatefulWidget {
  final Journey journey;

  const JourneyDetailsPage({
    super.key,
    required this.journey,
  });

  @override
  State<JourneyDetailsPage> createState() => _JourneyDetailsPageState();
}

class _JourneyDetailsPageState extends State<JourneyDetailsPage> with SingleTickerProviderStateMixin {
  late MapController _mapController;
  late LatLng _startLocation;
  late LatLng _endLocation;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _tabController = TabController(length: 2, vsync: this);
    
    // Use the coordinates stored in the journey
    _startLocation = LatLng(widget.journey.fromLat, widget.journey.fromLng);
    _endLocation = LatLng(widget.journey.toLat, widget.journey.toLng);
    
    // Center map between start and end points
    Future.delayed(const Duration(milliseconds: 500), () {
      final centerLat = (_startLocation.latitude + _endLocation.latitude) / 2;
      final centerLng = (_startLocation.longitude + _endLocation.longitude) / 2;
      _mapController.move(LatLng(centerLat, centerLng), 12);
    });
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final tomorrow = today.add(const Duration(days: 1));
    final dateOnly = DateTime(date.year, date.month, date.day);

    if (dateOnly == today) {
      return 'Today';
    } else if (dateOnly == tomorrow) {
      return 'Tomorrow';
    } else {
      final day = date.day;
      final suffix = _getDaySuffix(day);
      final monthName = DateFormat('MMMM').format(date);
      return '$day$suffix $monthName';
    }
  }

  String _getDaySuffix(int day) {
    if (day >= 11 && day <= 13) {
      return 'th';
    }
    switch (day % 10) {
      case 1:
        return 'st';
      case 2:
        return 'nd';
      case 3:
        return 'rd';
      default:
        return 'th';
    }
  }

  IconData _getModeIcon(String mode) {
    switch (mode.toLowerCase()) {
      case 'walking':
      case 'walk':
        return Icons.directions_walk;
      case 'bus':
        return Icons.directions_bus;
      case 'train':
      case 'rail':
        return Icons.train;
      case 'underground':
      case 'tube':
      case 'subway':
        return Icons.subway;
      case 'cycling':
      case 'bike':
        return Icons.directions_bike;
      default:
        return Icons.directions;
    }
  }

  Color _getModeColor(String mode) {
    switch (mode.toLowerCase()) {
      case 'walking':
      case 'walk':
        return Colors.green;
      case 'bus':
        return Colors.red;
      case 'train':
      case 'rail':
        return Colors.purple;
      case 'underground':
      case 'tube':
      case 'subway':
        return Colors.blue;
      case 'cycling':
      case 'bike':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final dateLabel = _formatDate(widget.journey.date);
    final timeLabel = '${widget.journey.date.hour}:${widget.journey.date.minute.toString().padLeft(2, '0')}';

    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Journey Details'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.blue,
          unselectedLabelColor: Colors.grey,
          indicatorColor: Colors.blue,
          tabs: const [
            Tab(icon: Icon(Icons.map), text: 'Map'),
            Tab(icon: Icon(Icons.list), text: 'Steps'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // Map View
          _buildMapView(dateLabel, timeLabel),
          // Steps View
          _buildStepsView(dateLabel, timeLabel),
        ],
      ),
    );
  }

  Widget _buildMapView(String dateLabel, String timeLabel) {
    return Stack(
      children: [
        FlutterMap(
          mapController: _mapController,
          options: MapOptions(
            initialCenter: const LatLng(51.5074, -0.1278),
            initialZoom: 12,
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.example.ui1',
              maxNativeZoom: 19,
              maxZoom: 19,
            ),
            PolylineLayer(
              polylines: [
                Polyline(
                  points: widget.journey.polylinePoints.isNotEmpty
                      ? widget.journey.polylinePoints
                          .map((p) => LatLng(p['lat']!, p['lng']!))
                          .toList()
                      : [_startLocation, _endLocation],
                  color: Colors.blue,
                  strokeWidth: 4,
                ),
              ],
            ),
            MarkerLayer(
              markers: [
                // Start marker (green)
                Marker(
                  point: _startLocation,
                  width: 40,
                  height: 40,
                  child: const Icon(
                    Icons.location_pin,
                    color: Colors.green,
                    size: 40,
                  ),
                ),
                // End marker (red)
                Marker(
                  point: _endLocation,
                  width: 40,
                  height: 40,
                  child: const Icon(
                    Icons.location_pin,
                    color: Colors.red,
                    size: 40,
                  ),
                ),
              ],
            ),
          ],
        ),
        // Journey info card at bottom
        Positioned(
          left: 16,
          right: 16,
          bottom: 16,
          child: Card(
            elevation: 8,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            dateLabel,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                          ),
                          Text(
                            timeLabel,
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                      if (widget.journey.durationMinutes != null)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.blue.shade100,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.access_time, size: 16, color: Colors.blue),
                              const SizedBox(width: 4),
                              Text(
                                '${widget.journey.durationMinutes} min',
                                style: const TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.blue,
                                ),
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                  const Divider(height: 24),
                  Row(
                    children: [
                      const Icon(Icons.location_on, color: Colors.green, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          widget.journey.from,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      const Icon(Icons.location_pin, color: Colors.red, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          widget.journey.to,
                          style: const TextStyle(
                            fontSize: 14,
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
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStepsView(String dateLabel, String timeLabel) {
    final hasSteps = widget.journey.steps != null && widget.journey.steps!.isNotEmpty;

    return ListView(
      padding: const EdgeInsets.all(16.0),
      children: [
        // Journey Summary Card
        Card(
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          dateLabel,
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                        ),
                        Text(
                          timeLabel,
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                    if (widget.journey.durationMinutes != null)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        decoration: BoxDecoration(
                          color: Colors.blue.shade100,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.access_time, size: 18, color: Colors.blue),
                            const SizedBox(width: 6),
                            Text(
                              '${widget.journey.durationMinutes} min',
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.blue,
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
                const Divider(height: 24),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.green.shade100,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.location_on, color: Colors.green, size: 20),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'From',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          Text(
                            widget.journey.from,
                            style: const TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.red.shade100,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.location_pin, color: Colors.red, size: 20),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'To',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          Text(
                            widget.journey.to,
                            style: const TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 24),
        // Steps Section
        Row(
          children: [
            const Text(
              'Route Steps',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Colors.black87,
              ),
            ),
            if (hasSteps) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.blue.shade100,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${widget.journey.steps!.length}',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade700,
                  ),
                ),
              ),
            ],
          ],
        ),
        const SizedBox(height: 12),
        if (!hasSteps)
          Card(
            elevation: 1,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                children: [
                  Icon(Icons.info_outline, size: 48, color: Colors.grey[400]),
                  const SizedBox(height: 12),
                  Text(
                    'No detailed steps available for this journey',
                    style: TextStyle(
                      fontSize: 15,
                      color: Colors.grey[600],
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          )
        else
          ...widget.journey.steps!.asMap().entries.map((entry) {
            final index = entry.key;
            final step = entry.value;
            final isLast = index == widget.journey.steps!.length - 1;

            return Padding(
              padding: const EdgeInsets.only(bottom: 12.0),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Step indicator column
                  Column(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: _getModeColor(step.mode),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          _getModeIcon(step.mode),
                          color: Colors.white,
                          size: 20,
                        ),
                      ),
                      if (!isLast)
                        Container(
                          width: 2,
                          height: 60,
                          color: Colors.grey[300],
                        ),
                    ],
                  ),
                  const SizedBox(width: 12),
                  // Step details card
                  Expanded(
                    child: Card(
                      elevation: 2,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: _getModeColor(step.mode).withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    step.mode.toUpperCase(),
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.bold,
                                      color: _getModeColor(step.mode),
                                    ),
                                  ),
                                ),
                                if (step.line != null) ...[
                                  const SizedBox(width: 8),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: Colors.grey[200],
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Text(
                                      step.line!,
                                      style: const TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.black87,
                                      ),
                                    ),
                                  ),
                                ],
                                const Spacer(),
                                Icon(Icons.access_time, size: 14, color: Colors.grey[600]),
                                const SizedBox(width: 4),
                                Text(
                                  '${step.durationMinutes} min',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey[600],
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            if (step.instructions.isNotEmpty) ...[
                              Text(
                                step.instructions,
                                style: const TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w500,
                                  color: Colors.black87,
                                ),
                              ),
                              const SizedBox(height: 8),
                            ],
                            if (step.fromStation.isNotEmpty || step.toStation.isNotEmpty) ...[
                              Row(
                                children: [
                                  Icon(Icons.circle, size: 8, color: Colors.grey[400]),
                                  const SizedBox(width: 6),
                                  Expanded(
                                    child: Text(
                                      step.fromStation,
                                      style: TextStyle(
                                        fontSize: 13,
                                        color: Colors.grey[700],
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  Icon(Icons.arrow_downward, size: 12, color: Colors.grey[400]),
                                  const SizedBox(width: 2),
                                ],
                              ),
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  Icon(Icons.circle, size: 8, color: Colors.grey[400]),
                                  const SizedBox(width: 6),
                                  Expanded(
                                    child: Text(
                                      step.toStation,
                                      style: TextStyle(
                                        fontSize: 13,
                                        color: Colors.grey[700],
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
      ],
    );
  }

  @override
  void dispose() {
    _mapController.dispose();
    _tabController.dispose();
    super.dispose();
  }
}
