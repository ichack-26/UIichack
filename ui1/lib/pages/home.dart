import 'package:flutter/material.dart';
import 'package:ui1/widgets/travel_route_summary.dart';
import 'package:ui1/models/journey.dart';
import 'package:ui1/pages/journey_details.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class HomePageRoute extends StatefulWidget {
  const HomePageRoute({super.key, required this.title});

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  final String title;

  @override
  State<HomePageRoute> createState() => _HomePageRouteState();
}

class _HomePageRouteState extends State<HomePageRoute> {
  // List to hold journeys loaded from storage
  List<Journey> _allJourneys = [];
  bool _isLoading = true;
  final Map<String, String> _locationNameCache = {};
  bool _isResolvingLocations = false;

  @override
  void initState() {
    super.initState();
    _loadJourneys();
  }

  Future<void> _loadJourneys() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final journeysJson = prefs.getStringList('journeys') ?? [];
      await _loadLocationCache(prefs);
      
      List<Journey> loadedJourneys = [];
      
      for (String json in journeysJson) {
        try {
          final journeyData = jsonDecode(json);
          // Load journeys that have the required coordinate fields
          // (polylinePoints is optional for backwards compatibility)
          if (journeyData.containsKey('fromLat') && 
              journeyData.containsKey('fromLng') && 
              journeyData.containsKey('toLat') && 
              journeyData.containsKey('toLng')) {
            loadedJourneys.add(Journey.fromJson(journeyData));
          }
        } catch (e) {
          print('Error loading individual journey: $e');
          // Skip malformed journeys
        }
      }
      
      setState(() {
        _allJourneys = loadedJourneys;
        _isLoading = false;
      });
      
      _resolveMissingLocationNames(loadedJourneys);
      _migrateJourneysWithResolvedNames();

      print('Loaded ${_allJourneys.length} journeys from storage');
    } catch (e) {
      print('Error loading journeys: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _deleteJourney(Journey journey) async {
    final prefs = await SharedPreferences.getInstance();
    final updatedJourneys = _allJourneys.where((j) => j.id != journey.id).toList();
    final updatedJson = updatedJourneys.map((j) => jsonEncode(j.toJson())).toList();
    await prefs.setStringList('journeys', updatedJson);
    if (!mounted) return;
    setState(() {
      _allJourneys = updatedJourneys;
    });
  }

  bool _looksLikeCoordinates(String value) {
    final trimmed = value.trim();
    if (trimmed.isEmpty) return false;
    if (trimmed.toLowerCase().startsWith('lat:')) return true;
    if (trimmed.toLowerCase().contains('lng:')) return true;
    return RegExp(r'^-?\d+(\.\d+)?,\s*-?\d+(\.\d+)?$').hasMatch(trimmed);
  }

  Future<void> _migrateJourneysWithResolvedNames() async {
    if (_allJourneys.isEmpty) return;
    final prefs = await SharedPreferences.getInstance();
    bool updatedAny = false;
    final List<Journey> updatedJourneys = [];

    for (final journey in _allJourneys) {
      String fromName = journey.from;
      String toName = journey.to;

      if (_looksLikeCoordinates(journey.from)) {
        final resolved = await _reverseGeocode(journey.fromLat, journey.fromLng);
        if (resolved != null && resolved.isNotEmpty) {
          fromName = resolved;
          updatedAny = true;
          _locationNameCache['${journey.id}_from'] = resolved;
          _locationNameCache['${journey.fromLat.toStringAsFixed(5)},${journey.fromLng.toStringAsFixed(5)}'] = resolved;
          await Future.delayed(const Duration(milliseconds: 1100));
        }
      }

      if (_looksLikeCoordinates(journey.to)) {
        final resolved = await _reverseGeocode(journey.toLat, journey.toLng);
        if (resolved != null && resolved.isNotEmpty) {
          toName = resolved;
          updatedAny = true;
          _locationNameCache['${journey.id}_to'] = resolved;
          _locationNameCache['${journey.toLat.toStringAsFixed(5)},${journey.toLng.toStringAsFixed(5)}'] = resolved;
          await Future.delayed(const Duration(milliseconds: 1100));
        }
      }

      if (fromName != journey.from || toName != journey.to) {
        updatedJourneys.add(Journey(
          id: journey.id,
          date: journey.date,
          from: fromName,
          to: toName,
          fromLat: journey.fromLat,
          fromLng: journey.fromLng,
          toLat: journey.toLat,
          toLng: journey.toLng,
          polylinePoints: journey.polylinePoints,
          imageUrl: journey.imageUrl,
          durationMinutes: journey.durationMinutes,
        ));
      } else {
        updatedJourneys.add(journey);
      }
    }

    if (updatedAny) {
      final updatedJson = updatedJourneys.map((j) => jsonEncode(j.toJson())).toList();
      await prefs.setStringList('journeys', updatedJson);
      await _saveLocationCache();
      if (mounted) {
        setState(() {
          _allJourneys = updatedJourneys;
        });
      }
    }
  }

  Future<void> _loadLocationCache(SharedPreferences prefs) async {
    final cacheJson = prefs.getString('locationNameCache');
    if (cacheJson == null || cacheJson.isEmpty) return;
    try {
      final decoded = jsonDecode(cacheJson) as Map<String, dynamic>;
      decoded.forEach((key, value) {
        if (value is String && value.isNotEmpty) {
          _locationNameCache[key] = value;
        }
      });
    } catch (_) {
      // ignore cache load errors
    }
  }

  Future<void> _saveLocationCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('locationNameCache', jsonEncode(_locationNameCache));
    } catch (_) {
      // ignore cache save errors
    }
  }

  Future<void> _resolveMissingLocationNames(List<Journey> journeys) async {
    if (_isResolvingLocations) return;
    _isResolvingLocations = true;
    try {
      for (final journey in journeys) {
        await _resolveLocationIfCoordinate(journey.id, journey.from, true, journey.fromLat, journey.fromLng);
        await Future.delayed(const Duration(milliseconds: 800));
        await _resolveLocationIfCoordinate(journey.id, journey.to, false, journey.toLat, journey.toLng);
        await Future.delayed(const Duration(milliseconds: 800));
      }
    } finally {
      _isResolvingLocations = false;
    }
  }

  Future<void> _resolveLocationIfCoordinate(
    String journeyId,
    String locationValue,
    bool isFrom,
    double lat,
    double lng,
  ) async {
    final coordKey = '${lat.toStringAsFixed(5)},${lng.toStringAsFixed(5)}';
    final key = '${journeyId}_${isFrom ? 'from' : 'to'}';

    // If the stored value already looks like a name, keep it
    final hasLetters = RegExp(r'[A-Za-z]').hasMatch(locationValue);
    if (hasLetters) {
      _locationNameCache[key] = locationValue;
      return;
    }

    final existing = _locationNameCache[key];
    if (existing != null && RegExp(r'[A-Za-z]').hasMatch(existing)) return;
    if (_locationNameCache.containsKey(coordKey)) {
      _locationNameCache[key] = _locationNameCache[coordKey]!;
      return;
    }

    final name = await _reverseGeocode(lat, lng);
    if (!mounted) return;
    setState(() {
      if (name != null && name.isNotEmpty) {
        _locationNameCache[coordKey] = name;
        _locationNameCache[key] = name;
        _saveLocationCache();
      } else {
        _locationNameCache[key] = locationValue;
      }
    });
  }

  Future<String?> _reverseGeocode(double lat, double lng) async {
    try {
      final mapsCoUrl = Uri.parse(
        'https://geocode.maps.co/reverse?lat=$lat&lon=$lng',
      );
      final mapsCoResponse = await http.get(mapsCoUrl).timeout(
        const Duration(seconds: 6),
      );
      if (mapsCoResponse.statusCode == 200) {
        final data = jsonDecode(mapsCoResponse.body);
        final address = data['address'] as Map<String, dynamic>?;
        if (address != null) {
          final place = address['neighbourhood'] ??
              address['suburb'] ??
              address['city_district'] ??
              address['city'] ??
              address['town'] ??
              address['village'] ??
              address['county'];
          if (place != null) return place.toString();
        }
        final display = data['display_name'] as String?;
        if (display != null && display.isNotEmpty) return display;
      }

      final url = Uri.parse(
        'https://nominatim.openstreetmap.org/reverse?format=json&lat=$lat&lon=$lng&zoom=14&addressdetails=1',
      );
      final response = await http.get(
        url,
        headers: {
          'User-Agent': 'UIichack/1.0 (https://github.com/ichack-26/UIichack)',
          'Accept-Language': 'en',
        },
      );
      if (response.statusCode != 200) return null;
      final data = jsonDecode(response.body);
      final address = data['address'] as Map<String, dynamic>?;
      if (address == null) return null;
      final place = address['neighbourhood'] ??
          address['suburb'] ??
          address['city_district'] ??
          address['city'] ??
          address['town'] ??
          address['village'] ??
          address['county'];
      if (place != null) return place.toString();
      return data['display_name'] as String?;
    } catch (_) {
      return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Text(
          widget.title,
          style: const TextStyle(
            color: Colors.black87,
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.black87),
            onPressed: () => _loadJourneys(),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Builder(builder: (context) {
              final now = DateTime.now();
              final today = DateTime(now.year, now.month, now.day);
              
              // Categorize journeys
              final List<Journey> all = _allJourneys;
              
              // Ongoing: journeys that started but haven't finished yet
              final ongoing = all.where((j) => j.isOngoing).toList()
                ..sort((a, b) => a.date.compareTo(b.date));
              
              // Upcoming: journeys that haven't started yet
              final upcoming = all.where((j) => j.isUpcoming).toList()
                ..sort((a, b) => a.date.compareTo(b.date));
              
              // History: journeys that have finished
              final history = all.where((j) => j.isFinished).toList()
                ..sort((a, b) => b.date.compareTo(a.date));

              return ListView(
                padding: const EdgeInsets.symmetric(vertical: 24.0),
                children: [
                  // Ongoing journeys section
                  if (ongoing.isNotEmpty) ...[
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 20.0),
                      child: Row(
                        children: [
                          Container(
                            width: 4,
                            height: 24,
                            decoration: BoxDecoration(
                              color: Colors.green,
                              borderRadius: BorderRadius.circular(2),
                            ),
                          ),
                          const SizedBox(width: 12),
                          const Text(
                            'Happening Today',
                            style: TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: Colors.green.shade100,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              '${ongoing.length}',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: Colors.green.shade700,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    ...ongoing.map((j) => Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 6.0),
                      child: Dismissible(
                        key: ValueKey('journey_${j.id}'),
                        direction: DismissDirection.startToEnd,
                        background: Container(
                          decoration: BoxDecoration(
                            color: Colors.red.shade400,
                            borderRadius: BorderRadius.circular(16.0),
                          ),
                          alignment: Alignment.centerLeft,
                          padding: const EdgeInsets.symmetric(horizontal: 20.0),
                          child: const Icon(Icons.delete, color: Colors.white),
                        ),
                        onDismissed: (_) => _deleteJourney(j),
                        child: TravelRouteSummaryWidget(
                          travelDate: j.date,
                          fromLocation: _locationNameCache['${j.id}_from'] ?? j.from,
                          toLocation: _locationNameCache['${j.id}_to'] ?? j.to,
                          isUpcoming: false,
                          isOngoing: true,
                          imageUrl: j.imageUrl,
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (context) => JourneyDetailsPage(journey: j),
                              ),
                            );
                          },
                        ),
                      ),
                    )),
                    const SizedBox(height: 32),
                  ],
                  
                  // Upcoming journeys section
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20.0),
                    child: Row(
                      children: [
                        Container(
                          width: 4,
                          height: 24,
                          decoration: BoxDecoration(
                            color: Colors.blue,
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                        const SizedBox(width: 12),
                        const Text(
                          'Upcoming',
                          style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  if (upcoming.isEmpty)
                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 20.0),
                      child: Text(
                        'No upcoming journeys',
                        style: TextStyle(color: Colors.grey, fontSize: 15),
                      ),
                    ),
                  ...upcoming.map((j) => Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 6.0),
                    child: Dismissible(
                      key: ValueKey('journey_${j.id}'),
                      direction: DismissDirection.startToEnd,
                      background: Container(
                        decoration: BoxDecoration(
                          color: Colors.red.shade400,
                          borderRadius: BorderRadius.circular(16.0),
                        ),
                        alignment: Alignment.centerLeft,
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: const Icon(Icons.delete, color: Colors.white),
                      ),
                      onDismissed: (_) => _deleteJourney(j),
                      child: TravelRouteSummaryWidget(
                        travelDate: j.date,
                        fromLocation: _locationNameCache['${j.id}_from'] ?? j.from,
                        toLocation: _locationNameCache['${j.id}_to'] ?? j.to,
                        isUpcoming: true,
                        imageUrl: j.imageUrl,
                        onTap: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (context) => JourneyDetailsPage(journey: j),
                            ),
                          );
                        },
                      ),
                    ),
                  )),

                  const SizedBox(height: 32),
                  
                  // History section
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20.0),
                    child: Row(
                      children: [
                        Container(
                          width: 4,
                          height: 24,
                          decoration: BoxDecoration(
                            color: Colors.grey,
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                        const SizedBox(width: 12),
                        const Text(
                          'History',
                          style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  if (history.isEmpty)
                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 20.0),
                      child: Text(
                        'No past journeys',
                        style: TextStyle(color: Colors.grey, fontSize: 15),
                      ),
                    ),
                  ...history.map((j) => Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 6.0),
                    child: Dismissible(
                      key: ValueKey('journey_${j.id}'),
                      direction: DismissDirection.startToEnd,
                      background: Container(
                        decoration: BoxDecoration(
                          color: Colors.red.shade400,
                          borderRadius: BorderRadius.circular(16.0),
                        ),
                        alignment: Alignment.centerLeft,
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: const Icon(Icons.delete, color: Colors.white),
                      ),
                      onDismissed: (_) => _deleteJourney(j),
                      child: TravelRouteSummaryWidget(
                        travelDate: j.date,
                        fromLocation: _locationNameCache['${j.id}_from'] ?? j.from,
                        toLocation: _locationNameCache['${j.id}_to'] ?? j.to,
                        isUpcoming: false,
                        imageUrl: j.imageUrl,
                        onTap: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (context) => JourneyDetailsPage(journey: j),
                            ),
                          );
                        },
                      ),
                    ),
                  )),
                  const SizedBox(height: 80),
                ],
              );
            }),
    );
  }
}
