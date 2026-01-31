import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';
import 'dart:convert';
import 'dart:async';

class RoutePlannerRoute extends StatefulWidget {
  const RoutePlannerRoute({super.key});

  @override
  State<RoutePlannerRoute> createState() => _RoutePlannerRouteState();
}

class _RoutePlannerRouteState extends State<RoutePlannerRoute> {
  final MapController _mapController = MapController();
  final TextEditingController _searchController = TextEditingController();
  DateTime? _selectedDate;
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

  // UI state for collapsible preferences
  bool _prefsExpanded = false;

  @override
  void initState() {
    super.initState();
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
                      initialDate: _selectedDate ?? DateTime.now(),
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
                            _selectedDate == null
                                ? 'Select Departure Time'
                                : '${_selectedDate!.day}/${_selectedDate!.month}/${_selectedDate!.year} ${_selectedDate!.hour}:${_selectedDate!.minute.toString().padLeft(2, '0')}',
                            style: TextStyle(
                              fontSize: 16,
                              color: _selectedDate == null ? Colors.grey : Colors.black,
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
                  onPressed: (_fromLocation != null && _toLocation != null && _selectedDate != null)
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
    _markers = [];
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
  }

  void _planRoute() {
    if (_fromLocation == null || _toLocation == null || _selectedDate == null) return;

    final suggestions = _generateMockRoutes();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => Padding(
        padding: const EdgeInsets.only(top: 16.0, left: 16, right: 16, bottom: 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Suggested routes', style: Theme.of(context).textTheme.titleMedium),
                IconButton(
                  onPressed: () => Navigator.of(context).pop(),
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...suggestions.map((route) => Card(
                  child: ListTile(
                    leading: const Icon(Icons.directions),
                    title: Text(route),
                    subtitle: Text(_toAddress.isEmpty ? 'Destination set' : 'To: $_toAddress'),
                    trailing: ElevatedButton(
                      onPressed: () {
                        Navigator.of(context).pop();
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Selected route: $route')),
                        );
                      },
                      child: const Text('Select'),
                    ),
                  ),
                )),
            const SizedBox(height: 12),
            Text('Preferences used:', style: Theme.of(context).textTheme.bodyMedium),
            const SizedBox(height: 6),
            Wrap(
              spacing: 8,
              children: [
                if (_avoidClaustrophobic) Chip(label: const Text('Avoid claustrophobic')),
                if (_requireLift) Chip(label: const Text('Require lift')),
                if (_avoidStairs) Chip(label: const Text('Avoid stairs')),
                if (_wheelchairAccessible) Chip(label: const Text('Wheelchair only')),
                if (!_avoidClaustrophobic && !_requireLift && !_avoidStairs && !_wheelchairAccessible)
                  const Text('None'),
              ],
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  List<String> _generateMockRoutes() {
    final List<String> routes = [];

    if (_wheelchairAccessible || _requireLift) {
      routes.add('Step-free via Main Concourse (uses lifts, ramps) — approx. 12 min');
    } else {
      routes.add('Fastest route via Central Stairs — approx. 9 min');
    }

    if (_avoidClaustrophobic) {
      routes.add('Scenic route avoiding tunnels and narrow passageways — approx. 15 min');
    } else {
      routes.add('Shortest route (may include tight passages) — approx. 8 min');
    }

    if (_avoidStairs) {
      routes.add('Stairs-free route following elevators and ramps — approx. 14 min');
    }

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