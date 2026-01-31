import 'package:flutter/material.dart';

class RoutePlannerRoute extends StatelessWidget {
  const RoutePlannerRoute({super.key});

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