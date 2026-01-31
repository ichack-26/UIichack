import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:ui1/models/journey.dart';
import 'package:ui1/services/advanced_navigation_service.dart';
import 'package:ui1/services/routing_service.dart';

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
  
  // Advanced navigation
  late AdvancedNavigationService _navigationService;
  NavigationState _navState = NavigationState.idle;
  NavigationStep? _currentStep;
  RouteDetails? _routeDetails;
  LatLng? _userLocation;

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    
    // Use the coordinates stored in the journey
    _startLocation = LatLng(widget.journey.fromLat, widget.journey.fromLng);
    _endLocation = LatLng(widget.journey.toLat, widget.journey.toLng);
    
    // Initialize navigation service
    _navigationService = AdvancedNavigationService(
      journey: widget.journey,
      onStateChange: _handleNavStateChange,
      onInstructionChange: _handleInstructionChange,
    );
    
    // Center map between start and end points
    Future.delayed(const Duration(milliseconds: 500), () {
      final centerLat = (_startLocation.latitude + _endLocation.latitude) / 2;
      final centerLng = (_startLocation.longitude + _endLocation.longitude) / 2;
      _mapController.move(LatLng(centerLat, centerLng), 12);
    });
  }

  void _handleNavStateChange(NavigationState state) {
    setState(() => _navState = state);
    
    // Fetch route details when navigation starts
    if (state == NavigationState.navigating && _routeDetails == null) {
      _fetchRouteDetails();
    }
  }

  void _handleInstructionChange(NavigationStep step) {
    setState(() => _currentStep = step);
  }

  Future<void> _fetchRouteDetails() async {
    try {
      final details = await RoutingService.getRouteDetails(
        _startLocation,
        _endLocation,
      );
      setState(() => _routeDetails = details);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Route error: $e')),
        );
      }
    }
  }

  Future<void> _startNavigation() async {
    final success = await _navigationService.startNavigation();
    if (!success && mounted) {
      // Show detailed error message
      String errorMsg = 'Failed to start navigation';
      
      if (_navState == NavigationState.error) {
        errorMsg = 'Check: 1) API key configured? 2) Location permission? 3) Internet connection?';
      }
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(errorMsg),
          duration: const Duration(seconds: 5),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final dateLabel = widget.journey.date.toLocal().toString().split(' ')[0];
    final timeLabel = '${widget.journey.date.hour}:${widget.journey.date.minute.toString().padLeft(2, '0')}';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Journey Details'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          if (_navState == NavigationState.navigating)
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Center(
                child: Text(
                  _navState.displayName,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ),
        ],
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
              // Show detailed route polyline if available
              PolylineLayer(
                polylines: [
                  if (_routeDetails != null)
                    Polyline(
                      points: _routeDetails!.polylinePoints,
                      color: _navState == NavigationState.navigating ? Colors.green : Colors.blue,
                      strokeWidth: 5,
                    )
                  else
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
                  // User location marker during navigation
                  if (_navState == NavigationState.navigating && _userLocation != null)
                    Marker(
                      point: _userLocation!,
                      width: 40,
                      height: 40,
                      child: Container(
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.blue, width: 3),
                        ),
                        child: const Icon(Icons.my_location, color: Colors.blue),
                      ),
                    ),
                ],
              ),
            ],
          ),
          // Navigation instruction card
          if (_navState == NavigationState.navigating)
            Positioned(
              top: 16,
              left: 16,
              right: 16,
              child: _buildInstructionCard(),
            ),
          // Route summary at bottom
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: _buildBottomPanel(dateLabel, timeLabel),
          ),
        ],
      ),
    );
  }

  Widget _buildInstructionCard() {
    if (_currentStep == null) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Loading directions...',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            if (_routeDetails != null) ...[
              const SizedBox(height: 8),
              Text(
                'Total: ${_routeDetails!.totalDistanceStr} (${_routeDetails!.totalDurationStr})',
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            _currentStep!.instruction,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: Text(
                  'Distance: ${_currentStep!.distanceStr}',
                  style: const TextStyle(fontSize: 14, color: Colors.blue),
                ),
              ),
              Text(
                'Duration: ${_currentStep!.durationStr}',
                style: const TextStyle(fontSize: 14, color: Colors.blue),
              ),
            ],
          ),
          if (_currentStep!.wayName != null) ...[
            const SizedBox(height: 4),
            Text(
              _currentStep!.wayName!,
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
          if (_routeDetails != null) ...[
            const SizedBox(height: 8),
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: _navigationService.getProgressPercentage() / 100,
                minHeight: 4,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Progress: ${_navigationService.getProgressPercentage()}%',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildBottomPanel(String dateLabel, String timeLabel) {
    final isNavigating = _navState == NavigationState.navigating;
    
    return Container(
      color: Theme.of(context).scaffoldBackgroundColor,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (!isNavigating) ...[
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
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _startNavigation,
                icon: const Icon(Icons.navigation),
                label: const Text('Start Live Navigation'),
              ),
            ] else ...[
              ElevatedButton.icon(
                onPressed: () {
                  setState(() {
                    _navigationService.stopNavigation();
                  });
                },
                icon: const Icon(Icons.stop),
                label: const Text('Stop Navigation'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _mapController.dispose();
    _navigationService.stopNavigation();
    super.dispose();
  }
}
