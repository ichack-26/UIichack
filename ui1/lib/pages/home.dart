import 'package:flutter/material.dart';
import 'package:ui1/widgets/travel_route_summary.dart';
import 'package:ui1/models/journey.dart';
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
      
      setState(() {
        _allJourneys = journeysJson
            .map((json) => Journey.fromJson(jsonDecode(json)))
            .toList();
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
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.
    return Scaffold(
      appBar: AppBar(
        // TRY THIS: Try changing the color here to a specific color (to
        // Colors.amber, perhaps?) and trigger a hot reload to see the AppBar
        // change color while the other colors stay the same.
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        // Here we take the value from the MyHomePage object that was created by
        // the App.build method, and use it to set our appbar title.
        title: Text(widget.title),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : Builder(builder: (context) {
                // Journeys from storage
                final List<Journey> all = _allJourneys;
                final upcoming = all.where((j) => j.isUpcoming).toList()
                  ..sort((a, b) => a.date.compareTo(b.date));
                final history = all.where((j) => !j.isUpcoming).toList()
                  ..sort((a, b) => b.date.compareTo(a.date));

                return ListView(
                  children: [
                    Text('Upcoming journeys', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: 8),
                    if (upcoming.isEmpty)
                      const Text('No upcoming journeys', style: TextStyle(color: Colors.grey)),
                    ...upcoming.map((j) => Padding(
                    padding: const EdgeInsets.only(bottom: 12.0),
                    child: TravelRouteSummaryWidget(
                      travelDate: j.date,
                      fromLocation: j.from,
                      toLocation: j.to,
                      isUpcoming: true,
                    ),
                  )),

              const SizedBox(height: 16),
              Text('History', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              if (history.isEmpty)
                const Text('No past journeys', style: TextStyle(color: Colors.grey)),
              ...history.map((j) => Padding(
                    padding: const EdgeInsets.only(bottom: 12.0),
                    child: TravelRouteSummaryWidget(
                      travelDate: j.date,
                      fromLocation: j.from,
                      toLocation: j.to,
                      isUpcoming: false,
                    ),
                  )),
            ],
          );
            }),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _loadJourneys(),
        tooltip: 'Refresh',
        child: const Icon(Icons.refresh),
      ),
    );
  }
}
