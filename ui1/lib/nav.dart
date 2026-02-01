import 'package:flutter/material.dart';
import 'package:ui1/pages/home.dart';
import 'package:ui1/pages/route_planner.dart';
import 'package:ui1/pages/live_location.dart';
import 'package:ui1/pages/my_stats.dart';

/// Flutter code sample for [NavigationBar].

void main() => runApp(const NavigationBarApp());

class NavigationBarApp extends StatelessWidget {
  const NavigationBarApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(home: NavigationExample());
  }
}

class NavigationExample extends StatefulWidget {
  const NavigationExample({super.key});

  @override
  State<NavigationExample> createState() => _NavigationExampleState();
}

class _NavigationExampleState extends State<NavigationExample> {
  int currentPageIndex = 0;

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    return Scaffold(
      bottomNavigationBar: NavigationBar(
        onDestinationSelected: (int index) {
          setState(() {
            currentPageIndex = index;
          });
        },
        indicatorColor: Colors.amber,
        selectedIndex: currentPageIndex,
        destinations: const <Widget>[
          NavigationDestination(
            selectedIcon: Icon(Icons.home),
            icon: Icon(Icons.home_outlined),
            label: 'Home',
          ),
          NavigationDestination(
            selectedIcon: Icon(Icons.route),
            icon: Icon(Icons.route_outlined),
            label: 'Route Planner',
          ),
          NavigationDestination(
            selectedIcon: Icon(Icons.my_location),
            icon: Icon(Icons.my_location_outlined),
            label: 'Live',
          ),
          NavigationDestination(
            selectedIcon: Icon(Icons.person),
            icon: Icon(Icons.person_outline),
            label: 'My',
          ),
        ],
      ),
      body: <Widget>[
        HomePageRoute(title: 'Home Page'),

        RoutePlannerRoute(),

        const LiveLocationPage(),

        const MyStatsPage(),
      ][currentPageIndex],
    );
  }
}