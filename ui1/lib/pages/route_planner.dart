import 'package:flutter/material.dart';

class RoutePlannerRoute extends StatefulWidget {
  const RoutePlannerRoute({super.key});

  @override
  State<RoutePlannerRoute> createState() => _RoutePlannerRouteState();
}

class _RoutePlannerRouteState extends State<RoutePlannerRoute> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Route Planner'),
      ),


      body: const Center(
        child: Text('This is the Route Planner page'),
      ),
    );
  }
}