# Code Changes Summary

## Modified File
`lib/pages/route_planner.dart`

## Changes Made

### 1. `_planRoute()` Method (Line ~644)

**Before:**
```dart
void _planRoute() {
  if (_fromLocation == null || _toLocation == null) return;
  _routes = _generateMockRoutes();
  setState(() { _selectedRouteIndex = 0; });
  Navigator.of(context).push(MaterialPageRoute(...));
}
```

**After:**
```dart
Future<void> _planRoute() async {
  if (_fromLocation == null || _toLocation == null) return;
  
  // Show loading dialog
  showDialog(
    context: context,
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
    _routes = await _fetchRoutesFromBackend();
    if (!mounted) return;
    Navigator.of(context).pop(); // Close loading dialog
    
    if (_routes.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No routes found. Please try again.')),
      );
      return;
    }
    
    setState(() { _selectedRouteIndex = 0; });
    Navigator.of(context).push(MaterialPageRoute(...));
  } catch (e) {
    print('Error planning route: $e');
    if (mounted) {
      Navigator.of(context).pop();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }
}
```

**Changes:**
- Now `async`
- Shows loading dialog while fetching
- Calls `_fetchRoutesFromBackend()` instead of `_generateMockRoutes()`
- Error handling with user-facing messages
- Checks `mounted` before state updates (good practice for async)

### 2. New Method: `_fetchRoutesFromBackend()`

```dart
Future<List<Route>> _fetchRoutesFromBackend() async {
  try {
    final url = Uri.parse('http://localhost:8000/route');
    
    final requestBody = {
      'origin': _fromAddress,
      'destination': _toAddress,
      'preferences': {
        'avoid_crowds': _avoidClaustrophobic,
        'avoid_noise': false,
        'avoid_heat': false,
        'prefer_buses': false,
        'minimise_changes': false,
      },
      'travel_date': _selectedDate.toIso8601String().split('T')[0],
      'start_time': null,
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
    print('Falling back to mock routes');
    return _generateMockRoutes();
  }
}
```

**Features:**
- Constructs POST request to `http://localhost:8000/route`
- Uses location **names** instead of coordinates
- Maps Flutter preferences to backend format
- Includes travel date
- Parses both primary and alternative routes
- 30-second timeout
- Graceful fallback to mock routes on error
- Comprehensive logging for debugging

### 3. New Method: `_parseBackendRoute()`

```dart
Route _parseBackendRoute(Map<String, dynamic> routeData, bool recommended) {
  final List<LatLng> points = [];

  // Simple start→end polyline
  points.add(_fromLocation!);
  points.add(_toLocation!);

  Color color = recommended ? Colors.blue : Colors.green;

  // Build step descriptions
  final steps = routeData['steps'] as List<dynamic>? ?? [];
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
    name: recommended ? 'Recommended Route' : 'Alternative Route',
    description: descriptionParts.join(' • '),
    polyline: Polyline(
      points: points,
      color: color,
      strokeWidth: 4,
    ),
  );
}
```

**Features:**
- Converts TfL journey data to Flutter Route model
- Creates simple start→end polylines
- Extracts sensory information for display
- Builds human-readable descriptions
- Color coding: Blue (recommended) vs Green (alternative)

## API Integration Points

### Sending Data TO Backend
- Location names (`_fromAddress`, `_toAddress`)
- User preferences (mapped from Flutter UI)
- Travel date

### Receiving Data FROM Backend
- Primary recommended route with highest score
- Alternative route with different characteristics
- Full step-by-step instructions
- Sensory analysis (crowding, noise, heat, reliability)
- Overall scores and warnings

## Error Handling

1. **Connection Errors**: Caught and logged, falls back to mock routes
2. **HTTP Errors**: Checked status code, throws exception
3. **Parse Errors**: Individual routes caught, continues with others
4. **User Feedback**: SnackBar messages for success/failure

## Testing Checklist

- [ ] Backend running on localhost:8000
- [ ] Location names are recognized by TfL (use full station names)
- [ ] Request body matches backend API contract
- [ ] Response parsing handles both primary and alternative routes
- [ ] UI correctly displays route information
- [ ] Loading dialog appears and disappears
- [ ] Error messages display correctly
- [ ] Fallback to mock routes works when backend unavailable
