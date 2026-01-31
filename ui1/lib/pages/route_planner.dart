import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'dart:async';
import 'package:ui1/models/journey.dart';

class RoutePlannerRoute extends StatefulWidget {
  const RoutePlannerRoute({super.key});

  @override
  State<RoutePlannerRoute> createState() => _RoutePlannerRouteState();
}

class _RoutePlannerRouteState extends State<RoutePlannerRoute> {
  final MapController _mapController = MapController();
  final TextEditingController _searchController = TextEditingController();
  late DateTime _selectedDate;
  LatLng? _fromLocation;
  LatLng? _toLocation;
  String _fromAddress = '';
  String _toAddress = '';
  List<Marker> _markers = [];
  bool _selectingStart = false;
  bool _selectingDestination = false;
  List<SearchResult> _searchResults = [];
  bool _isSearching = false;
  Timer? _debounce;
  LatLng _userLocation = const LatLng(37.7749, -122.4194); // Default to San Francisco

  // User preferences
  bool _avoidClaustrophobic = false;
  bool _requireLift = false;
  bool _avoidStairs = false;
  bool _wheelchairAccessible = false;

  // Routes state
  List<Route> _routes = [];
  int? _selectedRouteIndex;
  List<Polyline> _polylines = [];

  // UI state for collapsible preferences
  bool _prefsExpanded = false;

  Future<void> _saveJourneyToStorage() async {
    if (_fromLocation == null || _toLocation == null || _selectedRouteIndex == null) {
      print('Cannot save: missing fromLocation, toLocation, or selectedRouteIndex');
      return;
    }
    
    if (_selectedRouteIndex! >= _routes.length) {
      print('Cannot save: selected route index out of range');
      return;
    }
    
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // Get the selected route's polyline points
      final selectedRoute = _routes[_selectedRouteIndex!];
      final polylinePoints = selectedRoute.polyline.points
          .map((point) => {'lat': point.latitude, 'lng': point.longitude})
          .toList();
      
      // Generate unique ID for the journey
      final journeyId = DateTime.now().millisecondsSinceEpoch.toString();
      
      // Create journey object with coordinates and route polyline
      final journey = Journey(
        id: journeyId,
        date: _selectedDate,
        from: _fromAddress,
        to: _toAddress,
        fromLat: _fromLocation!.latitude,
        fromLng: _fromLocation!.longitude,
        toLat: _toLocation!.latitude,
        toLng: _toLocation!.longitude,
        polylinePoints: polylinePoints,
      );
      
      // Get existing journeys
      final journeysJson = prefs.getStringList('journeys') ?? [];
      
      // Add new journey
      final jsonStr = jsonEncode(journey.toJson());
      print('Saving journey JSON: $jsonStr');
      print('Saving route with ${polylinePoints.length} waypoints');
      journeysJson.add(jsonStr);
      
      // Save back to storage
      await prefs.setStringList('journeys', journeysJson);
      
      print('Journey saved successfully: ${journey.id}');
      print('Total journeys in storage: ${journeysJson.length}');
    } catch (e) {
      print('Error saving journey: $e');
      print('Stack trace: $e');
    }
  }

  @override
  void initState() {
    super.initState();
    _selectedDate = DateTime.now();
    _getUserLocation();
  }

  Future<void> _getUserLocation() async {
    try {
      // Check permission status
      LocationPermission permission = await Geolocator.checkPermission();
      
      if (permission == LocationPermission.denied) {
        // Request permission
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          print('Location permissions are denied');
          return;
        }
      }
      
      if (permission == LocationPermission.deniedForever) {
        print('Location permissions are permanently denied');
        return;
      }

      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.best,
        timeLimit: const Duration(seconds: 10),
      );
      
      setState(() {
        _userLocation = LatLng(position.latitude, position.longitude);
        
        // Set start location to user's current location
        _fromLocation = _userLocation;
        _fromAddress = 'Your Location (${_userLocation.latitude.toStringAsFixed(4)}, ${_userLocation.longitude.toStringAsFixed(4)})';
        
        _updateMarkers();
        _mapController.move(_userLocation, 14);
      });
      print('User location obtained: $_userLocation');
    } catch (e) {
      print('Error getting user location: $e');
      // Will use default San Francisco location
    }
  }

  String get _preferencesSummary {
    final count = [_avoidClaustrophobic, _requireLift, _avoidStairs, _wheelchairAccessible].where((v) => v).length;
    return count == 0 ? 'None selected' : '$count selected';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Route Planner'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Column(
        children: [
          // Search and input section
          Container(
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.2),
                  spreadRadius: 1,
                  blurRadius: 5,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Start Place
                InkWell(
                  onTap: () => _showLocationPicker(true),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.blue),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.trip_origin, color: Colors.blue),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            _fromAddress.isEmpty ? 'Select Start Place' : _fromAddress,
                            style: TextStyle(
                              fontSize: 16,
                              color: _fromAddress.isEmpty ? Colors.grey : Colors.black,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const Icon(Icons.search, color: Colors.grey),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                // Destination Place
                InkWell(
                  onTap: () => _showLocationPicker(false),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.red),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.location_on, color: Colors.red),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            _toAddress.isEmpty ? 'Select Destination Place' : _toAddress,
                            style: TextStyle(
                              fontSize: 16,
                              color: _toAddress.isEmpty ? Colors.grey : Colors.black,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const Icon(Icons.search, color: Colors.grey),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                // Departure Time
                InkWell(
                  onTap: () async {
                    final date = await showDatePicker(
                      context: context,
                      initialDate: _selectedDate,
                      firstDate: DateTime.now(),
                      lastDate: DateTime(2101),
                    );
                    if (date != null) {
                      final time = await showTimePicker(
                        context: context,
                        initialTime: TimeOfDay.now(),
                      );
                      if (time != null) {
                        setState(() {
                          _selectedDate = DateTime(
                            date.year,
                            date.month,
                            date.day,
                            time.hour,
                            time.minute,
                          );
                        });
                      }
                    }
                  },
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.access_time, color: Colors.grey),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            '${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year} ${_selectedDate.hour}:${_selectedDate.minute.toString().padLeft(2, '0')}',
                            style: const TextStyle(
                              fontSize: 16,
                              color: Colors.black,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Collapsible Preferences
                Theme(
                  data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                  child: ExpansionTile(
                    key: const Key('preferences_tile'),
                    initiallyExpanded: _prefsExpanded,
                    onExpansionChanged: (v) => setState(() => _prefsExpanded = v),
                    leading: const Icon(Icons.filter_list),
                    title: const Text('Preferences'),
                    subtitle: Text(_preferencesSummary),
                    children: [
                      CheckboxListTile(
                        value: _avoidClaustrophobic,
                        onChanged: (v) => setState(() => _avoidClaustrophobic = v ?? false),
                        title: const Text('Avoid claustrophobic areas'),
                        subtitle: const Text('Avoid narrow tunnels or enclosed corridors'),
                        secondary: const Icon(Icons.airline_stops_outlined),
                        controlAffinity: ListTileControlAffinity.leading,
                      ),

                      CheckboxListTile(
                        value: _requireLift,
                        onChanged: (v) => setState(() => _requireLift = v ?? false),
                        title: const Text('Require lift/elevator access'),
                        subtitle: const Text('Prefer routes with elevator access'),
                        secondary: const Icon(Icons.elevator),
                        controlAffinity: ListTileControlAffinity.leading,
                      ),

                      CheckboxListTile(
                        value: _avoidStairs,
                        onChanged: (v) => setState(() => _avoidStairs = v ?? false),
                        title: const Text('Avoid stairs'),
                        subtitle: const Text('Prefer ramps and level paths'),
                        secondary: const Icon(Icons.stairs),
                        controlAffinity: ListTileControlAffinity.leading,
                      ),

                      CheckboxListTile(
                        value: _wheelchairAccessible,
                        onChanged: (v) => setState(() => _wheelchairAccessible = v ?? false),
                        title: const Text('Wheelchair-accessible routes only'),
                        subtitle: const Text('Filter to fully accessible options'),
                        secondary: const Icon(Icons.accessible),
                        controlAffinity: ListTileControlAffinity.leading,
                      ),

                      const SizedBox(height: 4),
                    ],
                  ),
                ),

                const SizedBox(height: 8),
                // Go Button
                ElevatedButton(
                  onPressed: (_fromLocation != null && _toLocation != null)
                      ? _planRoute
                      : null,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: Colors.blue,
                    foregroundColor: Colors.white,
                    disabledBackgroundColor: Colors.grey[300],
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text(
                    'Plan Route',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),
          // Map section
          Expanded(
            child: Stack(
              children: [
                FlutterMap(
                  mapController: _mapController,
                  options: MapOptions(
                    initialCenter: _userLocation,
                    initialZoom: 14,
                    onTap: (tapPosition, point) {
                      if (_selectingStart) {
                        setState(() {
                          _fromLocation = point;
                          _fromAddress = 'Lat: ${point.latitude.toStringAsFixed(4)}, Lng: ${point.longitude.toStringAsFixed(4)}';
                          _updateMarkers();
                          _selectingStart = false;
                        });
                      } else if (_selectingDestination) {
                        setState(() {
                          _toLocation = point;
                          _toAddress = 'Lat: ${point.latitude.toStringAsFixed(4)}, Lng: ${point.longitude.toStringAsFixed(4)}';
                          _updateMarkers();
                          _selectingDestination = false;
                        });
                      }
                    },
                  ),
                  children: [
                    TileLayer(
                      urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'com.example.ui1',
                      maxNativeZoom: 19,
                      maxZoom: 19,
                    ),
                    PolylineLayer(
                      polylines: _polylines,
                    ),
                    MarkerLayer(
                      markers: _markers,
                    ),
                  ],
                ),
                if (_selectingStart || _selectingDestination)
                  Positioned(
                    top: 16,
                    left: 16,
                    right: 16,
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(8),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.2),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Text(
                        _selectingStart 
                          ? 'Tap on the map to select start location'
                          : 'Tap on the map to select destination',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _updateMarkers() {
    setState(() {
      _markers = [];
      
      // Add user's current location marker
      _markers.add(
        Marker(
          point: _userLocation,
          width: 40,
          height: 40,
          child: const Icon(
            Icons.my_location,
            color: Colors.cyan,
            size: 40,
          ),
        ),
      );
      
      if (_fromLocation != null) {
        _markers.add(
          Marker(
            point: _fromLocation!,
            width: 40,
            height: 40,
            child: const Icon(
              Icons.location_pin,
              color: Colors.blue,
              size: 40,
            ),
          ),
        );
      }
      if (_toLocation != null) {
        _markers.add(
          Marker(
            point: _toLocation!,
            width: 40,
            height: 40,
            child: const Icon(
              Icons.location_pin,
              color: Colors.red,
              size: 40,
            ),
          ),
        );
      }
    });
  }

  void _planRoute() {
    if (_fromLocation == null || _toLocation == null) return;

    // Generate mock routes
    _routes = _generateMockRoutes();
    
    setState(() {
      _selectedRouteIndex = 0;
    });

    // Navigate to fullscreen map with route selection
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => FullscreenMapPage(
          markers: _markers,
          userLocation: _userLocation,
          routes: _routes,
          onRouteSelected: (routeIndex) {
            setState(() {
              _selectedRouteIndex = routeIndex;
              _updateRoutePolylines();
            });
          },
          onContinue: _saveJourneyToStorage,
          preferences: (
            avoidClaustrophobic: _avoidClaustrophobic,
            requireLift: _requireLift,
            avoidStairs: _avoidStairs,
            wheelchairAccessible: _wheelchairAccessible,
          ),
        ),
      ),
    );
  }

  void _updateRoutePolylines() {
    _polylines = [];
    if (_selectedRouteIndex != null && _selectedRouteIndex! < _routes.length) {
      final selectedRoute = _routes[_selectedRouteIndex!];
      _polylines = [selectedRoute.polyline];
    }
  }

  List<Route> _generateMockRoutes() {
    final List<Route> routes = [];
    
    // Route 1: Direct/Fastest route (blue)
    routes.add(Route(
      name: _wheelchairAccessible || _requireLift 
        ? 'Step-free via Main Concourse'
        : 'Fastest route via Central Stairs',
      description: _wheelchairAccessible || _requireLift
        ? 'Uses lifts, ramps — approx. 12 min'
        : 'Approx. 9 min',
      polyline: Polyline(
        points: [
          _fromLocation!,
          LatLng(
            (_fromLocation!.latitude + _toLocation!.latitude) / 2,
            (_fromLocation!.longitude + _toLocation!.longitude) / 2,
          ),
          _toLocation!,
        ],
        color: Colors.blue,
        strokeWidth: 4,
      ),
    ));
    
    // Route 2: Scenic route (green)
    routes.add(Route(
      name: 'Scenic route',
      description: _avoidClaustrophobic
        ? 'Through open spaces, avoiding tunnels — approx. 15 min'
        : 'Through parks and landmarks — approx. 18 min',
      polyline: Polyline(
        points: [
          _fromLocation!,
          LatLng(
            _fromLocation!.latitude + 0.002,
            (_fromLocation!.longitude + _toLocation!.longitude) / 2,
          ),
          LatLng(
            _toLocation!.latitude - 0.001,
            _toLocation!.longitude,
          ),
          _toLocation!,
        ],
        color: Colors.green,
        strokeWidth: 4,
      ),
    ));
    
    // Route 3: Accessible route (orange)
    routes.add(Route(
      name: 'Accessible route',
      description: _avoidStairs
        ? 'Stairs-free, elevators and ramps only — approx. 15 min'
        : 'Wheelchair friendly, no major obstacles — approx. 14 min',
      polyline: Polyline(
        points: [
          _fromLocation!,
          LatLng(
            _fromLocation!.latitude - 0.002,
            (_fromLocation!.longitude + _toLocation!.longitude) / 2,
          ),
          LatLng(
            _toLocation!.latitude + 0.001,
            _toLocation!.longitude,
          ),
          _toLocation!,
        ],
        color: Colors.orange,
        strokeWidth: 4,
      ),
    ));

    return routes;
  }

  Future<void> _searchPlaces(String query) async {
    if (query.isEmpty) {
      setState(() {
        _searchResults = [];
        _isSearching = false;
      });
      return;
    }

    // Cancel previous timer
    _debounce?.cancel();

    setState(() {
      _isSearching = true;
    });

    // Debounce the search request
    _debounce = Timer(const Duration(milliseconds: 500), () async {
      try {
        final url = Uri.parse(
          'https://nominatim.openstreetmap.org/search?q=${Uri.encodeComponent(query)}&format=json&limit=5',
        );
        final response = await http.get(
          url,
          headers: {'User-Agent': 'FlutterApp'},
        );

        if (response.statusCode == 200) {
          final List<dynamic> data = json.decode(response.body);
          if (mounted) {
            setState(() {
              _searchResults = data.map((item) => SearchResult.fromJson(item)).toList();
              _isSearching = false;
            });
          }
        }
      } catch (e) {
        print('Error searching: $e');
        if (mounted) {
          setState(() {
            _isSearching = false;
          });
        }
      }
    });
  }

  void _showLocationPicker(bool isStart) {
    _searchController.clear();
    _searchResults = [];
    
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) => DraggableScrollableSheet(
          initialChildSize: 0.7,
          minChildSize: 0.5,
          maxChildSize: 0.95,
          builder: (_, controller) => Container(
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                  ),
                  child: Column(
                    children: [
                      Container(
                        width: 40,
                        height: 4,
                        decoration: BoxDecoration(
                          color: Colors.grey[400],
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        isStart ? 'Select Start Location' : 'Select Destination',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _searchController,
                        decoration: InputDecoration(
                          hintText: 'Search for a place',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                          prefixIcon: const Icon(Icons.search),
                        ),
                        onChanged: (value) {
                          _searchPlaces(value).then((_) {
                            setModalState(() {});
                          });
                        },
                      ),
                    ],
                  ),
                ),
                if (_isSearching)
                  const Padding(
                    padding: EdgeInsets.all(16.0),
                    child: CircularProgressIndicator(),
                  )
                else if (_searchResults.isNotEmpty)
                  Expanded(
                    child: ListView.builder(
                      controller: controller,
                      itemCount: _searchResults.length,
                      itemBuilder: (context, index) {
                        final result = _searchResults[index];
                        return ListTile(
                          leading: Icon(
                            Icons.location_on,
                            color: isStart ? Colors.blue : Colors.red,
                          ),
                          title: Text(result.displayName),
                          onTap: () {
                            setState(() {
                              final location = LatLng(result.lat, result.lon);
                              if (isStart) {
                                _fromLocation = location;
                                _fromAddress = result.displayName;
                              } else {
                                _toLocation = location;
                                _toAddress = result.displayName;
                              }
                              _updateMarkers();
                            });
                            _mapController.move(LatLng(result.lat, result.lon), 14);
                            Navigator.of(context).pop();
                          },
                        );
                      },
                    ),
                  )
                else
                  Column(
                    children: [
                      const Padding(
                        padding: EdgeInsets.all(16.0),
                        child: Text(
                          'Search for a place or tap the button below to select from map',
                          style: TextStyle(color: Colors.grey),
                          textAlign: TextAlign.center,
                        ),
                      ),
                      ElevatedButton.icon(
                        onPressed: () {
                          Navigator.of(context).pop();
                          // Use Future.delayed to ensure modal is fully closed
                          Future.delayed(const Duration(milliseconds: 100), () {
                            if (mounted) {
                              setState(() {
                                if (isStart) {
                                  _selectingStart = true;
                                } else {
                                  _selectingDestination = true;
                                }
                              });
                            }
                          });
                        },
                        icon: const Icon(Icons.map),
                        label: const Text('Select from Map'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _searchController.dispose();
    super.dispose();
  }
}

/// Full-screen map page
class FullscreenMapPage extends StatefulWidget {
  final List<Marker> markers;
  final LatLng userLocation;
  final List<Route> routes;
  final Function(int)? onRouteSelected;
  final Future<void> Function()? onContinue;
  final ({bool avoidClaustrophobic, bool requireLift, bool avoidStairs, bool wheelchairAccessible})? preferences;

  const FullscreenMapPage({
    required this.markers,
    required this.userLocation,
    required this.routes,
    this.onRouteSelected,
    this.onContinue,
    this.preferences,
  });

  @override
  State<FullscreenMapPage> createState() => _FullscreenMapPageState();
}

class _FullscreenMapPageState extends State<FullscreenMapPage> {
  late MapController _fullscreenMapController;
  int? _selectedRouteIndex = 0;

  @override
  void initState() {
    super.initState();
    _fullscreenMapController = MapController();
    // Center the map at the user's location
    Future.delayed(const Duration(milliseconds: 500), () {
      _fullscreenMapController.move(widget.userLocation, 14);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Map'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Stack(
        children: [
          FlutterMap(
            mapController: _fullscreenMapController,
            options: MapOptions(
              initialCenter: widget.userLocation,
              initialZoom: 14,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.example.ui1',
                maxNativeZoom: 19,
                maxZoom: 19,
              ),
              PolylineLayer(
                polylines: widget.routes.map((route) => route.polyline).toList(),
              ),
              MarkerLayer(
                markers: widget.markers,
              ),
            ],
          ),
          // Route selection overlay at bottom
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              color: Theme.of(context).scaffoldBackgroundColor,
              child: SingleChildScrollView(
                child: Padding(
                  padding: const EdgeInsets.only(top: 16.0, left: 16, right: 16, bottom: 24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text('Suggested routes', style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 12),
                      ...widget.routes.asMap().entries.map((entry) {
                        final index = entry.key;
                        final route = entry.value;
                        final isSelected = _selectedRouteIndex == index;
                        final routeColor = route.polyline.color;
                        return Card(
                          color: isSelected ? routeColor.withAlpha(51) : null,
                          child: ListTile(
                            leading: Icon(Icons.directions, color: routeColor),
                            title: Text(route.name),
                            subtitle: Text(route.description),
                            onTap: () {
                              setState(() {
                                _selectedRouteIndex = index;
                              });
                              if (widget.onRouteSelected != null) {
                                widget.onRouteSelected!(index);
                              }
                            },
                          ),
                        );
                      }).toList(),
                      const SizedBox(height: 12),
                      Text('Preferences used:', style: Theme.of(context).textTheme.bodyMedium),
                      const SizedBox(height: 6),
                      Wrap(
                        spacing: 8,
                        children: [
                          if (widget.preferences?.avoidClaustrophobic ?? false) Chip(label: const Text('Avoid claustrophobic')),
                          if (widget.preferences?.requireLift ?? false) Chip(label: const Text('Require lift')),
                          if (widget.preferences?.avoidStairs ?? false) Chip(label: const Text('Avoid stairs')),
                          if (widget.preferences?.wheelchairAccessible ?? false) Chip(label: const Text('Wheelchair only')),
                          if ((widget.preferences?.avoidClaustrophobic ?? false) == false && 
                              (widget.preferences?.requireLift ?? false) == false && 
                              (widget.preferences?.avoidStairs ?? false) == false && 
                              (widget.preferences?.wheelchairAccessible ?? false) == false)
                            const Text('None'),
                        ],
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () async {
                          // Save the journey to persistent storage
                          if (widget.onContinue != null) {
                            await widget.onContinue!();
                          }
                          Navigator.of(context).pop(); // Close fullscreen map
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue,
                        ),
                        child: const Text('Continue'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class SearchResult {
  final String displayName;
  final double lat;
  final double lon;

  SearchResult({
    required this.displayName,
    required this.lat,
    required this.lon,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) {
    return SearchResult(
      displayName: json['display_name'] as String,
      lat: double.parse(json['lat'] as String),
      lon: double.parse(json['lon'] as String),
    );
  }
}

class Route {
  final String name;
  final String description;
  final Polyline polyline;

  Route({
    required this.name,
    required this.description,
    required this.polyline,
  });
}