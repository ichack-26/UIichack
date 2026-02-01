import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'dart:async';
import 'dart:math';
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
  LatLng _userLocation = const LatLng(51.5074, -0.1278); // Default to London

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

  String _generateRouteImageUrl(String destination) {
    // Extract keywords from destination for relevant images
    List<String> keywords = destination.toLowerCase().split(',')[0].split(' ').take(2).toList();
    
    // Common location keywords with themed images
    final keywordImageMap = {
      'london': 'https://images.unsplash.com/photo-1486299267070-83823f5448dd?w=600&h=400&fit=crop',
      'paris': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&h=400&fit=crop',
      'new': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=600&h=400&fit=crop',
      'york': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=600&h=400&fit=crop',
      'tokyo': 'https://images.unsplash.com/photo-1540959375944-7049f642e9a0?w=600&h=400&fit=crop',
      'sydney': 'https://images.unsplash.com/photo-1506973404872-a4a8b6ce2f0d?w=600&h=400&fit=crop',
      'dubai': 'https://images.unsplash.com/photo-1512453475900-7e03e547a1b1?w=600&h=400&fit=crop',
      'mountain': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=400&fit=crop',
      'beach': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&h=400&fit=crop',
      'forest': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=600&h=400&fit=crop',
      'airport': 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&h=400&fit=crop',
    };
    
    // Check if any keyword matches
    for (String keyword in keywords) {
      if (keywordImageMap.containsKey(keyword)) {
        return keywordImageMap[keyword]!;
      }
    }
    
    // Default to generic travel image
    return 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&h=400&fit=crop';
  }

  Future<String> _getPhotoFromRoute() async {
    try {
      if (_routes.isEmpty || _selectedRouteIndex == null) {
        return _generateRouteImageUrl(_toAddress);
      }

      // Get a random point from the selected route
      final route = _routes[_selectedRouteIndex!];
      if (route.polyline.points.isEmpty) {
        return _generateRouteImageUrl(_toAddress);
      }

      // Pick a point along the route
      final pointCount = route.polyline.points.length;
      if (pointCount <= 2) {
        return _generateRouteImageUrl(_toAddress);
      }

      final midIndex = pointCount ~/ 2;
      final midPoint = route.polyline.points[midIndex];

      print('Searching for photo near: ${midPoint.latitude}, ${midPoint.longitude}');

      // Use Wikimedia Commons geosearch API (no key required)
      final wikiUrl = 'https://commons.wikimedia.org/w/api.php?'
          'action=query'
          '&format=json'
          '&list=geosearch'
          '&gscoord=${midPoint.latitude}|${midPoint.longitude}'
          '&gsradius=1000'
          '&gslimit=10'
          '&gsprop=type'
          '&gsnamespace=6';

      final response = await http.get(Uri.parse(wikiUrl)).timeout(
        const Duration(seconds: 4),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['query'] != null && data['query']['geosearch'] != null) {
          final results = data['query']['geosearch'] as List;
          
          if (results.isNotEmpty) {
            // Get a random result from the geotagged images
            final randomIndex = DateTime.now().millisecondsSinceEpoch % results.length;
            final pageId = results[randomIndex]['pageid'];
            
            // Get the image URL
            final imageInfoUrl = 'https://commons.wikimedia.org/w/api.php?'
                'action=query'
                '&format=json'
                '&prop=imageinfo'
                '&iiprop=url'
                '&iiurlwidth=600'
                '&pageids=$pageId';
            
            final imageResponse = await http.get(Uri.parse(imageInfoUrl)).timeout(
              const Duration(seconds: 3),
            );
            
            if (imageResponse.statusCode == 200) {
              final imageData = jsonDecode(imageResponse.body);
              if (imageData['query'] != null && imageData['query']['pages'] != null) {
                final pages = imageData['query']['pages'];
                final page = pages[pageId.toString()];
                
                if (page != null && page['imageinfo'] != null && (page['imageinfo'] as List).isNotEmpty) {
                  final thumbUrl = page['imageinfo'][0]['thumburl'];
                  if (thumbUrl != null) {
                    print('Found Wikimedia photo: $thumbUrl');
                    return thumbUrl;
                  }
                }
              }
            }
          }
        }
      }

      print('No geotagged photo found, using fallback');
      return _generateRouteImageUrl(_toAddress);
    } catch (e) {
      print('Error fetching route photo: $e');
      return _generateRouteImageUrl(_toAddress);
    }
  }

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
      
      // Calculate estimated journey duration based on walking speed (5 km/h average)
      double totalDistance = 0;
      for (int i = 0; i < selectedRoute.polyline.points.length - 1; i++) {
        final p1 = selectedRoute.polyline.points[i];
        final p2 = selectedRoute.polyline.points[i + 1];
        final lat1 = p1.latitude * 0.017453292519943295; // to radians
        final lat2 = p2.latitude * 0.017453292519943295;
        final lon1 = p1.longitude * 0.017453292519943295;
        final lon2 = p2.longitude * 0.017453292519943295;
        
        // Haversine formula
        final dLat = lat2 - lat1;
        final dLon = lon2 - lon1;
        final a = sin(dLat / 2) * sin(dLat / 2) +
            cos(lat1) * cos(lat2) *
            sin(dLon / 2) * sin(dLon / 2);
        final c = 2 * asin(sqrt(a));
        totalDistance += 6371 * c; // Earth radius in km
      }
      
      // Calculate duration: distance (km) / speed (5 km/h) * 60 = minutes
      final durationMinutes = (totalDistance / 5 * 60).round();
      
      // Generate unique ID for the journey
      final journeyId = DateTime.now().millisecondsSinceEpoch.toString();
      
      // Get a photo from the actual route location
      final imageUrl = await _getPhotoFromRoute();
      
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
        imageUrl: imageUrl,
        durationMinutes: durationMinutes,
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
    
    // Initialize with London as default locations
    _fromLocation = _userLocation;
    _fromAddress = 'Select Start Location';
    
    // Set a default destination (e.g., South Kensington, London)
    _toLocation = const LatLng(51.4945, -0.1757);
    _toAddress = 'Select Destination';
    
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
      
      final gpsLocation = LatLng(position.latitude, position.longitude);

      // Always use GPS location as default start location
      setState(() {
        _userLocation = gpsLocation;
        _fromLocation = gpsLocation;
        _fromAddress = 'Your Location (${gpsLocation.latitude.toStringAsFixed(4)}, ${gpsLocation.longitude.toStringAsFixed(4)})';
        _updateMarkers();
      });
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          _mapController.move(_userLocation, 14);
        }
      });
      print('User location obtained: $_userLocation');
    } catch (e) {
      print('Error getting user location: $e');
      // Will use default London location
    }
  }

  bool _isUkLatLng(LatLng point) {
    // Rough UK bounding box (lat: 49.8..60.9, lon: -8.6..2.1)
    return point.latitude >= 49.8 &&
        point.latitude <= 60.9 &&
        point.longitude >= -8.6 &&
        point.longitude <= 2.1;
  }

  bool _ensureUkSelection(LatLng point, bool isStart) {
    if (_isUkLatLng(point)) {
      return true;
    }

    final label = isStart ? 'start' : 'destination';
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Please select a UK $label location.'),
      ),
    );
    return false;
  }

  String get _preferencesSummary {
    final count = [_avoidClaustrophobic, _requireLift, _avoidStairs, _wheelchairAccessible].where((v) => v).length;
    return count == 0 ? 'None selected' : '$count selected';
  }
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
                        if (!_ensureUkSelection(point, true)) {
                          return;
                        }
                        setState(() {
                          _fromLocation = point;
                          _fromAddress = 'Lat: ${point.latitude.toStringAsFixed(4)}, Lng: ${point.longitude.toStringAsFixed(4)}';
                          _updateMarkers();
                          _selectingStart = false;
                        });
                      } else if (_selectingDestination) {
                        if (!_ensureUkSelection(point, false)) {
                          return;
                        }
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

  /// Convert UK latitude/longitude to postcode using postcodes.io API
  /// Returns null if location is outside UK or API fails
  Future<String?> _convertLatLngToUKPostcode(double latitude, double longitude) async {
    try {
      print('Converting lat=$latitude, lng=$longitude to UK postcode...');
      
      final url = Uri.parse(
        'https://api.postcodes.io/postcodes?lat=$latitude&lon=$longitude&limit=1',
      );
      
      final response = await http.get(url).timeout(const Duration(seconds: 8));
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        // postcodes.io returns status: 200 with result: null for non-UK locations
        if (data['status'] == 200) {
          if (data['result'] != null && data['result'].isNotEmpty) {
            final result = data['result'][0];
            final postcode = result['postcode'];
            final country = result['country'];
            
            print('✓ UK Postcode: $postcode (in $country)');
            return postcode;
          } else {
            // No result found - location is outside UK
            print('✗ No postcode found - location may be outside UK');
            return null;
          }
        } else {
          // Unexpected status
          print('✗ Unexpected API status: ${data['status']}');
          return null;
        }
      } else {
        print('✗ HTTP error: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('✗ Error converting to postcode: $e');
      return null;
    }
  }


  Future<void> _planRoute() async {
    if (_fromLocation == null || _toLocation == null) return;

    if (!_isUkLatLng(_fromLocation!) || !_isUkLatLng(_toLocation!)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select UK locations for both start and destination.')),
      );
      return;
    }

    print('DEBUG: From location = ${_fromLocation!.latitude}, ${_fromLocation!.longitude}');
    print('DEBUG: To location = ${_toLocation!.latitude}, ${_toLocation!.longitude}');

    // Show loading dialog
    var dialogOpen = true;
    final rootNavigator = Navigator.of(context, rootNavigator: true);
    showDialog(
      context: context,
      useRootNavigator: true,
      barrierDismissible: false,
      builder: (context) => const AlertDialog(
        content: Row(
          children: [
            CircularProgressIndicator(),
            SizedBox(width: 16),
            Text('Finding routes...'),
          ],
        ),
      ),
    );

    try {
      // Convert coordinates to postcodes
      print('Converting coordinates to postcodes...');
      final fromPostcode = await _convertLatLngToUKPostcode(
        _fromLocation!.latitude,
        _fromLocation!.longitude,
      );
      final toPostcode = await _convertLatLngToUKPostcode(
        _toLocation!.latitude,
        _toLocation!.longitude,
      );
      
      if (fromPostcode == null) {
        throw Exception('Could not convert start location to UK postcode. Please use the search function.');
      }
      if (toPostcode == null) {
        throw Exception('Could not convert destination to UK postcode. Please use the search function.');
      }
      
      print('Route: $fromPostcode → $toPostcode');
      
      // Fetch routes from backend using postcodes
      _routes = await _fetchRoutesFromBackend(fromPostcode, toPostcode);
      
      if (!mounted) return;
      rootNavigator.pop(); // Close loading dialog
      dialogOpen = false;
      
      if (_routes.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No routes found. Please try again.')),
        );
        return;
      }
      
      setState(() {
        _selectedRouteIndex = 0;
      });

      // Navigate to fullscreen map with route selection
      if (mounted) {
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
    } catch (e) {
      print('Error planning route: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (dialogOpen && mounted && rootNavigator.canPop()) {
        rootNavigator.pop();
      }
    }
  }

  Future<List<Route>> _fetchRoutesFromBackend(String fromPostcode, String toPostcode) async {
    try {
      final url = Uri.parse('http://172.30.185.25:8000/route');

      print("Going from $fromPostcode to $toPostcode");
      
      final requestBody = {
        'origin': fromPostcode,
        'destination': toPostcode,
        'preferences': {
          'avoid_crowds': _avoidClaustrophobic,
          'avoid_noise': false, // Not exposed in UI yet
          'avoid_heat': false, // Not exposed in UI yet
          'prefer_buses': false, // Not exposed in UI yet
          'minimise_changes': false, // Not exposed in UI yet
        },
        'travel_date': _selectedDate.toIso8601String().split('T')[0],
        'start_time': null, // User can set this if needed
        'arrive_by': false,
      };

      print('Sending route request to backend: $requestBody');

      final response = await http
          .post(
            url,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(requestBody),
          )
          .timeout(const Duration(seconds: 30));

      print('Backend response status: ${response.statusCode}');
      print('Backend response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final routes = <Route>[];

        // Parse primary route
        if (data['success'] == true && data['primary_route'] != null) {
          try {
            final route = _parseBackendRoute(data['primary_route'], true);
            routes.add(route);
          } catch (e) {
            print('Error parsing primary route: $e');
          }
        }

        // Parse alternative route
        if (data['alternative_route'] != null) {
          try {
            final route = _parseBackendRoute(data['alternative_route'], false);
            routes.add(route);
          } catch (e) {
            print('Error parsing alternative route: $e');
          }
        }

        if (routes.isEmpty) {
          throw Exception(data['error'] ?? 'No valid routes parsed');
        }

        print('Successfully fetched ${routes.length} routes from backend');
        return routes;
      } else {
        throw Exception(
          'Backend returned ${response.statusCode}: ${response.body}',
        );
      }
    } catch (e) {
      print('Error fetching routes from backend: $e');
      // Fallback to mock routes if backend fails
      print('Falling back to mock routes');
      return _generateMockRoutes();
    }
  }

  Route _parseBackendRoute(Map<String, dynamic> routeData, bool recommended) {
    final List<LatLng> points = [];

    // Prefer detailed step paths if provided by backend
    final steps = routeData['steps'] as List<dynamic>? ?? [];
    for (final step in steps) {
      final path = (step as Map<String, dynamic>)['path'] as List<dynamic>? ?? [];
      for (final p in path) {
        if (p is Map<String, dynamic>) {
          final lat = p['lat'];
          final lng = p['lng'];
          if (lat is num && lng is num) {
            final latVal = lat.toDouble();
            final lngVal = lng.toDouble();
            // Backend may send lat/lng swapped; detect UK lat/lng and fix
            if (latVal.abs() <= 3 && lngVal.abs() >= 49) {
              points.add(LatLng(lngVal, latVal));
            } else {
              points.add(LatLng(latVal, lngVal));
            }
          }
        }
      }
    }

    // Use backend-provided polyline coordinates when available
    if (points.isEmpty) {
      final polylineCoords = routeData['polyline_coords'] as List<dynamic>? ?? [];
      for (final coord in polylineCoords) {
        if (coord is List && coord.length >= 2) {
          final lat = coord[0];
          final lon = coord[1];
          if (lat is num && lon is num) {
            points.add(LatLng(lat.toDouble(), lon.toDouble()));
          }
        }
      }
    }

    // Fallback: straight line if no geometry provided
    if (points.isEmpty) {
      points.add(_fromLocation!);
      points.add(_toLocation!);
    }

    // Determine color based on recommendation
    Color color = recommended ? Colors.blue : Colors.green;

    // Build step descriptions
    final stepsDescription = steps
        .map((s) => '${s['instructions']}')
        .join(' → ')
        .replaceAll('  ', ' ');

    final durationMinutes = routeData['duration_minutes'] as int? ?? 0;
    final numChanges = routeData['number_of_changes'] as int? ?? 0;

    // Get sensory summary for description
    final sensorySummary = routeData['sensory_summary'] as Map<String, dynamic>? ?? {};
    final crowding = sensorySummary['crowding'] as Map<String, dynamic>? ?? {};

    final descriptionParts = [
      'Duration: ~$durationMinutes min',
      'Changes: $numChanges',
      'Crowding: ${crowding['level'] ?? 'Unknown'}',
    ];

    if (stepsDescription.isNotEmpty) {
      descriptionParts.add('Route: $stepsDescription');
    }

    return Route(
      name: recommended
          ? 'Recommended Route'
          : 'Alternative Route',
      description: descriptionParts.join(' • '),
      polyline: Polyline(
        points: points,
        color: color,
        strokeWidth: 4,
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
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Center(
                        child: Container(
                          width: 40,
                          height: 4,
                          decoration: BoxDecoration(
                            color: Colors.grey[400],
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          CircleAvatar(
                            radius: 16,
                            backgroundColor: isStart ? Colors.blue : Colors.red,
                            child: Icon(
                              isStart ? Icons.trip_origin : Icons.location_on,
                              color: Colors.white,
                              size: 18,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  isStart ? 'Select Start Location' : 'Select Destination',
                                  style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  'UK locations only',
                                  style: TextStyle(
                                    color: Colors.grey[600],
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _searchController,
                        decoration: InputDecoration(
                          hintText: 'Search for a place or postcode',
                          filled: true,
                          fillColor: Colors.white,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide(color: Colors.grey.shade300),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide(color: Colors.grey.shade300),
                          ),
                          prefixIcon: const Icon(Icons.search),
                          suffixIcon: _searchController.text.isNotEmpty
                              ? IconButton(
                                  icon: const Icon(Icons.clear),
                                  onPressed: () {
                                    _searchController.clear();
                                    setModalState(() {
                                      _searchResults = [];
                                      _isSearching = false;
                                    });
                                  },
                                )
                              : null,
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
                        return Card(
                          margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: ListTile(
                            leading: CircleAvatar(
                              backgroundColor: (isStart ? Colors.blue : Colors.red).withAlpha(30),
                              child: Icon(
                                Icons.location_on,
                                color: isStart ? Colors.blue : Colors.red,
                              ),
                            ),
                            title: Text(
                              result.displayName,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            subtitle: Text(
                              '${result.lat.toStringAsFixed(4)}, ${result.lon.toStringAsFixed(4)}',
                              style: TextStyle(color: Colors.grey[600]),
                            ),
                            trailing: const Icon(Icons.chevron_right),
                            onTap: () {
                              final location = LatLng(result.lat, result.lon);
                              if (!_ensureUkSelection(location, isStart)) {
                                return;
                              }
                              setState(() {
                                if (isStart) {
                                  _fromLocation = location;
                                  _fromAddress = result.displayName;
                                } else {
                                  _toLocation = location;
                                  _toAddress = result.displayName;
                                }
                                _updateMarkers();
                              });
                              _mapController.move(location, 14);
                              Navigator.of(context).pop();
                            },
                          ),
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
                          'Search for a place or pick directly on the map',
                          style: TextStyle(color: Colors.grey),
                          textAlign: TextAlign.center,
                        ),
                      ),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
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
                            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            backgroundColor: Colors.blue.withAlpha(230),
                            foregroundColor: Colors.white,
                            elevation: 0,
                        ),
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
          // Route selection bottom sheet
          Positioned.fill(
            child: Align(
              alignment: Alignment.bottomCenter,
              child: DraggableScrollableSheet(
                initialChildSize: 0.35,
                minChildSize: 0.2,
                maxChildSize: 0.75,
                builder: (context, scrollController) {
                  return Material(
                    elevation: 12,
                    color: Theme.of(context).scaffoldBackgroundColor,
                    borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                    child: Padding(
                      padding: const EdgeInsets.only(top: 8.0, left: 16, right: 16, bottom: 16),
                      child: ListView(
                        controller: scrollController,
                        children: [
                          Center(
                            child: Container(
                              width: 40,
                              height: 4,
                              decoration: BoxDecoration(
                                color: Colors.grey[400],
                                borderRadius: BorderRadius.circular(2),
                              ),
                            ),
                          ),
                          const SizedBox(height: 12),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('Suggested routes', style: Theme.of(context).textTheme.titleMedium),
                              Text('${widget.routes.length} options', style: Theme.of(context).textTheme.bodySmall),
                            ],
                          ),
                          const SizedBox(height: 12),
                          ...widget.routes.asMap().entries.map((entry) {
                            final index = entry.key;
                            final route = entry.value;
                            final isSelected = _selectedRouteIndex == index;
                            final routeColor = route.polyline.color;

                            return InkWell(
                              onTap: () {
                                setState(() {
                                  _selectedRouteIndex = index;
                                });
                                if (widget.onRouteSelected != null) {
                                  widget.onRouteSelected!(index);
                                }
                              },
                              borderRadius: BorderRadius.circular(16),
                              child: Container(
                                margin: const EdgeInsets.only(bottom: 10),
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: isSelected ? routeColor.withAlpha(26) : Colors.white,
                                  borderRadius: BorderRadius.circular(16),
                                  border: Border.all(
                                    color: isSelected ? routeColor : Colors.grey.shade200,
                                    width: isSelected ? 2 : 1,
                                  ),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.black.withOpacity(0.04),
                                      blurRadius: 8,
                                      offset: const Offset(0, 2),
                                    ),
                                  ],
                                ),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Container(
                                      width: 8,
                                      height: 56,
                                      decoration: BoxDecoration(
                                        color: routeColor,
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                    ),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Row(
                                            children: [
                                              Expanded(
                                                child: Text(
                                                  route.name,
                                                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                                        fontWeight: FontWeight.w600,
                                                      ),
                                                ),
                                              ),
                                              if (isSelected)
                                                Icon(Icons.check_circle, color: routeColor, size: 20),
                                            ],
                                          ),
                                          const SizedBox(height: 4),
                                          Text(
                                            route.description,
                                            style: Theme.of(context).textTheme.bodySmall,
                                            maxLines: 3,
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          }).toList(),
                          const SizedBox(height: 8),
                          Text('Preferences used:', style: Theme.of(context).textTheme.bodyMedium),
                          const SizedBox(height: 6),
                          Wrap(
                            spacing: 8,
                            runSpacing: 6,
                            children: [
                              if (widget.preferences?.avoidClaustrophobic ?? false) Chip(label: const Text('Avoid claustrophobic')),
                              if (widget.preferences?.requireLift ?? false) Chip(label: const Text('Require lift')),
                              if (widget.preferences?.avoidStairs ?? false) Chip(label: const Text('Avoid stairs')),
                              if (widget.preferences?.wheelchairAccessible ?? false) Chip(label: const Text('Wheelchair only')),
                              if ((widget.preferences?.avoidClaustrophobic ?? false) == false &&
                                  (widget.preferences?.requireLift ?? false) == false &&
                                  (widget.preferences?.avoidStairs ?? false) == false &&
                                  (widget.preferences?.wheelchairAccessible ?? false) == false)
                                const Chip(label: Text('None')),
                            ],
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton.icon(
                            onPressed: () async {
                              if (widget.onContinue != null) {
                                await widget.onContinue!();
                              }
                              Navigator.of(context).pop();
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.blue,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            icon: const Icon(Icons.check_circle_outline),
                            label: const Text('Use selected route'),
                          ),
                        ],
                      ),
                    ),
                  );
                },
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