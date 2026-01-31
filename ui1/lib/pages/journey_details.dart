import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:ui1/models/journey.dart';

class JourneyDetailsPage extends StatefulWidget {
  final Journey journey;

  const JourneyDetailsPage({
    super.key,
    required this.journey,
  });

  @override
  State<JourneyDetailsPage> createState() => _JourneyDetailsPageState();
}

class _JourneyDetailsPageState extends State<JourneyDetailsPage> {
  late MapController _mapController;
  late LatLng _startLocation;
  late LatLng _endLocation;

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    
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

  @override
  Widget build(BuildContext context) {
    final dateLabel = widget.journey.date.toLocal().toString().split(' ')[0];
    final timeLabel = '${widget.journey.date.hour}:${widget.journey.date.minute.toString().padLeft(2, '0')}';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Journey Details'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Stack(
        children: [
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: const LatLng(37.7749, -122.4194),
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
                    points: [_startLocation, _endLocation],
                    color: Colors.blue,
                    strokeWidth: 4,
                  ),
                ],
              ),
              MarkerLayer(
                markers: [
                  // Start marker (blue)
                  Marker(
                    point: _startLocation,
                    width: 40,
                    height: 40,
                    child: const Icon(
                      Icons.location_pin,
                      color: Colors.blue,
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
          // Journey info overlay at bottom
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              color: Theme.of(context).scaffoldBackgroundColor,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'Journey Information',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Date: $dateLabel',
                          style: const TextStyle(fontSize: 14),
                        ),
                        Text(
                          'Time: $timeLabel',
                          style: const TextStyle(fontSize: 14),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'From: ${widget.journey.from}',
                      style: const TextStyle(fontSize: 14),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'To: ${widget.journey.to}',
                      style: const TextStyle(fontSize: 14),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }
}
