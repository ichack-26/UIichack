import 'package:flutter/material.dart';
import 'package:ui1/widgets/travel_route_summary.dart';
import 'package:ui1/models/journey.dart';
import 'package:ui1/pages/journey_details.dart';
import 'package:shared_preferences/shared_preferences.dart';
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

  @override
  void initState() {
    super.initState();
    _loadJourneys();
  }

  Future<void> _loadJourneys() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final journeysJson = prefs.getStringList('journeys') ?? [];
      
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
      
      print('Loaded ${_allJourneys.length} journeys from storage');
    } catch (e) {
      print('Error loading journeys: $e');
      setState(() {
        _isLoading = false;
      });
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
                      child: TravelRouteSummaryWidget(
                        travelDate: j.date,
                        fromLocation: j.from,
                        toLocation: j.to,
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
                    child: TravelRouteSummaryWidget(
                      travelDate: j.date,
                      fromLocation: j.from,
                      toLocation: j.to,
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
                    child: TravelRouteSummaryWidget(
                      travelDate: j.date,
                      fromLocation: j.from,
                      toLocation: j.to,
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
                  )),
                  const SizedBox(height: 80),
                ],
              );
            }),
    );
  }
}
