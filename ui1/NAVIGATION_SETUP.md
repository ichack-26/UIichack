# Advanced Live Navigation Setup Guide

## Overview
Your app now has complete turn-by-turn navigation with live instructions based on device location. Here's how to set it up:

## 1. Get a Free API Key (OpenRouteService)

1. **Sign up** at https://openrouteservice.org/sign-up/
2. **Create an API key** in your dashboard
3. **Copy your API key**

## 2. Add Your API Key

Edit [lib/services/routing_service.dart](lib/services/routing_service.dart#L9):

```dart
static const String _openRouteServiceKey = 'YOUR_API_KEY_HERE';
```

Replace `YOUR_API_KEY_HERE` with your actual API key.

## 3. Update pubspec.yaml (Optional Dependencies)

These are already in your pubspec.yaml but ensure you have them:

```yaml
dependencies:
  geolocator: ^10.1.0
  http: ^1.2.0
  flutter_map: ^6.1.0
  latlong2: ^0.9.0
```

## 4. Platform Permissions

### Android (android/app/src/main/AndroidManifest.xml)
Add these permissions:

```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

### iOS (ios/Runner/Info.plist)
Add these keys:

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>We need your location for turn-by-turn navigation</string>
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>We need your location for turn-by-turn navigation</string>
```

## 5. How It Works

### RoutingService
Handles route planning:
- Gets detailed turn-by-turn directions from OpenRouteService API
- Snaps user location to the nearest road
- Calculates distance matrices between points
- Decodes polylines and provides route bounds

**Key Methods:**
- `getRouteDetails()` - Get full route with turn instructions
- `snapToRoad()` - Align user location to actual road
- `getDistanceMatrix()` - Get distances between multiple locations

### AdvancedNavigationService
Handles real-time navigation:
- Tracks device location every 3+ meters
- Automatically progresses through turn instructions
- Triggers state changes (loading → navigating → arrived)
- Calculates progress percentage

**Key Methods:**
- `startNavigation()` - Begin turn-by-turn navigation
- `getCurrentStep()` - Get current instruction
- `getNextStep()` - Get next instruction preview
- `getProgressPercentage()` - Route completion %

### JourneyDetailsPage UI
Displays live navigation:
- Real-time instruction card at top
- User location marker during navigation
- Progress bar showing route completion
- Route changes from blue to green while navigating

## 6. Usage Example

In your journey details page, users can:

1. **View route summary** - Distance and estimated time
2. **Start navigation** - Tap "Start Live Navigation" button
3. **Follow instructions** - See turn-by-turn directions in real-time
4. **Track progress** - Watch progress bar update
5. **Stop navigation** - Tap "Stop Navigation" button

## 7. Key Features

✅ **Turn-by-Turn Navigation** - Detailed instructions with distance/duration  
✅ **Real-Time Updates** - Location updated every 3+ meters  
✅ **Progress Tracking** - Know how far through the route you are  
✅ **Road Snapping** - User location aligned to actual roads  
✅ **Multiple Waypoints** - Support for intermediate stops  
✅ **Distance Matrix** - Calculate distances between multiple locations  
✅ **Error Handling** - Graceful fallbacks and error messages  

## 8. Customization Options

### Adjust location update frequency
In [lib/services/advanced_navigation_service.dart](lib/services/advanced_navigation_service.dart#L33):

```dart
const double _waypointThreshold = 30; // Distance in meters to trigger next step
```

### Change map style
In [lib/pages/journey_details.dart](lib/pages/journey_details.dart#L72):

```dart
// Use different tile layer
// MapBox: https://api.mapbox.com/styles/v1/...
// Stamen: https://stamen-tiles.a.ssl.fastly.net/...
```

## 9. Troubleshooting

**Navigation not starting?**
- Check location permission is granted
- Ensure API key is valid
- Check internet connection

**Instructions not updating?**
- Verify device is getting GPS signal (outdoors)
- Check location permission is "Always" not "While Using"

**Route doesn't show?**
- Check API key is active
- Verify coordinates are valid
- Check OpenRouteService status

## 10. Alternative APIs

If you want to switch services:

- **Google Maps**: Requires API key, more expensive
- **Mapbox**: Good free tier with routing
- **Here Maps**: Enterprise-grade navigation
- **TomTom**: Real-time traffic included

Update `_openRouteServiceUrl` in `routing_service.dart` to switch providers.
