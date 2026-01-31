import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';
import 'package:flutter/material.dart';
import 'dart:async';
import 'dart:math';
import 'package:ui1/models/journey.dart';
import 'package:ui1/services/routing_service.dart';

class AdvancedNavigationService {
  final Journey journey;
  final Function(NavigationState) onStateChange;
  final Function(NavigationStep)? onInstructionChange;
  
  late StreamSubscription<Position> _positionStream;
  RouteDetails? _routeDetails;
  int _currentStepIndex = 0;
  NavigationState _currentState = NavigationState.idle;
  
  // Thresholds
  static const double _waypointThreshold = 30; // meters
  static const double _speedThreshold = 1; // m/s
  
  AdvancedNavigationService({
    required this.journey,
    required this.onStateChange,
    this.onInstructionChange,
  });

  Future<bool> startNavigation() async {
    try {
      _changeState(NavigationState.loading);
      
      print('Starting navigation...');
      
      // Request location permission
      LocationPermission permission = await Geolocator.checkPermission();
      print('Current permission: $permission');
      
      if (permission == LocationPermission.denied) {
        print('Permission denied, requesting...');
        permission = await Geolocator.requestPermission();
        print('Permission after request: $permission');
      }
      
      if (permission == LocationPermission.deniedForever) {
        final errorMsg = 'Location permission denied forever. Enable in app settings.';
        print(errorMsg);
        _changeState(NavigationState.error);
        return false;
      }

      // Get route details from routing service
      print('Fetching route details...');
      final start = LatLng(journey.fromLat, journey.fromLng);
      final end = LatLng(journey.toLat, journey.toLng);
      
      try {
        _routeDetails = await RoutingService.getRouteDetails(start, end);
        print('Route details received: ${_routeDetails?.steps.length} steps');
      } catch (routeError) {
        print('Route error: $routeError');
        _changeState(NavigationState.error);
        return false;
      }
      
      // Start listening to position updates
      print('Starting position stream...');
      _positionStream = Geolocator.getPositionStream(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.best,
          distanceFilter: 3, // Update every 3 meters
          timeLimit: Duration(seconds: 5),
        ),
      ).listen(
        _handlePositionUpdate,
        onError: (error) {
          print('Position stream error: $error');
          _changeState(NavigationState.error);
        },
      );
      
      _changeState(NavigationState.navigating);
      _currentStepIndex = 0;
      print('Navigation started successfully');
      return true;
    } catch (e) {
      print('Navigation startup error: $e');
      _changeState(NavigationState.error);
      return false;
    }
  }

  void _handlePositionUpdate(Position position) async {
    if (_routeDetails == null) return;
    
    final userLocation = LatLng(position.latitude, position.longitude);
    
    // Snap user location to road
    final snappedLocation = await RoutingService.snapToRoad(userLocation);
    
    // Find closest step in route
    _findAndUpdateCurrentStep(snappedLocation, position.speed);
  }

  void _findAndUpdateCurrentStep(LatLng userLocation, double speed) {
    if (_routeDetails == null || _routeDetails!.steps.isEmpty) return;
    
    // If already completed
    if (_currentStepIndex >= _routeDetails!.steps.length) {
      _changeState(NavigationState.arrived);
      return;
    }
    
    final currentStep = _routeDetails!.steps[_currentStepIndex];
    
    // Find distance to next step endpoint
    final distanceToWaypoint = _calculateDistance(
      userLocation,
      _routeDetails!.polylinePoints[
        (_currentStepIndex + 1).clamp(0, _routeDetails!.polylinePoints.length - 1)
      ],
    );
    
    // Move to next step if close enough or moving slowly
    if (distanceToWaypoint < _waypointThreshold || 
        (speed < _speedThreshold && distanceToWaypoint < _waypointThreshold * 2)) {
      _currentStepIndex++;
      
      if (_currentStepIndex < _routeDetails!.steps.length) {
        final nextStep = _routeDetails!.steps[_currentStepIndex];
        onInstructionChange?.call(nextStep);
      } else {
        _changeState(NavigationState.arrived);
      }
    } else {
      // Update progress on current step
      onInstructionChange?.call(currentStep);
    }
  }

  double _calculateDistance(LatLng point1, LatLng point2) {
    const double earthRadius = 6371000; // meters
    final lat1Rad = point1.latitude * pi / 180;
    final lat2Rad = point2.latitude * pi / 180;
    final dLatRad = (point2.latitude - point1.latitude) * pi / 180;
    final dLngRad = (point2.longitude - point1.longitude) * pi / 180;
    
    final a = sin(dLatRad / 2) * sin(dLatRad / 2) +
        cos(lat1Rad) * cos(lat2Rad) * 
        sin(dLngRad / 2) * sin(dLngRad / 2);
    final c = 2 * asin(sqrt(a));
    
    return earthRadius * c;
  }

  NavigationStep? getCurrentStep() {
    if (_routeDetails == null || 
        _currentStepIndex >= _routeDetails!.steps.length) {
      return null;
    }
    return _routeDetails!.steps[_currentStepIndex];
  }

  NavigationStep? getNextStep() {
    if (_routeDetails == null || 
        _currentStepIndex + 1 >= _routeDetails!.steps.length) {
      return null;
    }
    return _routeDetails!.steps[_currentStepIndex + 1];
  }

  RouteDetails? getRouteDetails() => _routeDetails;

  int getProgressPercentage() {
    if (_routeDetails == null || _routeDetails!.steps.isEmpty) return 0;
    return ((_currentStepIndex / _routeDetails!.steps.length) * 100).toInt();
  }

  void _changeState(NavigationState state, {String? errorMessage}) {
    _currentState = state;
    onStateChange(state);
  }

  void stopNavigation() {
    _positionStream.cancel();
    _changeState(NavigationState.stopped);
  }

  void pauseNavigation() {
    _changeState(NavigationState.paused);
  }

  void resumeNavigation() {
    _changeState(NavigationState.navigating);
  }

  @override
  toString() => 'AdvancedNavigationService(state: $_currentState, step: $_currentStepIndex)';
}

enum NavigationState {
  idle,
  loading,
  navigating,
  paused,
  arrived,
  stopped,
  error,
}

extension NavigationStateExtension on NavigationState {
  String get displayName {
    switch (this) {
      case NavigationState.idle:
        return 'Ready';
      case NavigationState.loading:
        return 'Loading route...';
      case NavigationState.navigating:
        return 'Navigating';
      case NavigationState.paused:
        return 'Paused';
      case NavigationState.arrived:
        return 'Arrived!';
      case NavigationState.stopped:
        return 'Stopped';
      case NavigationState.error:
        return 'Error';
    }
  }

  Color get color {
    switch (this) {
      case NavigationState.navigating:
        return const Color(0xFF2196F3);
      case NavigationState.arrived:
        return const Color(0xFF4CAF50);
      case NavigationState.paused:
        return const Color(0xFFFFC107);
      case NavigationState.error:
        return const Color(0xFFF44336);
      default:
        return const Color(0xFF9E9E9E);
    }
  }
}

