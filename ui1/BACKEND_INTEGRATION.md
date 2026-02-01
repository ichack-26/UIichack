# Backend Integration Guide

## Overview
The Flutter app integrates with the CalmRoute TfL backend server for neurodivergent-friendly journey planning in London. The app sends location and preference requests to the backend and displays recommended routes on the map.

## Backend Server Setup

### Starting the Backend Server
The backend server is located in `ui1/backend/` and should run on `localhost:8000`:

```bash
cd ui1/backend
pip install -r requirements.txt
python main.py
```

The server will start on `http://localhost:8000` and provide both `/health` and `/route` endpoints.

## API Integration

### Health Check Endpoint
**Endpoint:** `GET http://localhost:8000/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "CalmRoute TfL API",
  "tfl_auth": "configured" or "no auth (rate limited)"
}
```

### Route Planning Endpoint
**Endpoint:** `POST http://localhost:8000/route`

**Request Body:**
```json
{
  "origin": "King's Cross Station",
  "destination": "British Museum",
  "preferences": {
    "avoid_crowds": false,
    "avoid_noise": false,
    "avoid_heat": false,
    "prefer_buses": false,
    "minimise_changes": false
  },
  "travel_date": "2025-02-15",
  "start_time": "14:30",
  "arrive_by": false
}
```

**Expected Response:**
```json
{
  "success": true,
  "primary_route": {
    "journey_id": "route_0",
    "duration_minutes": 25,
    "number_of_changes": 1,
    "steps": [
      {
        "mode": "walking",
        "line": null,
        "from_station": "King's Cross Station",
        "to_station": "Platform 5",
        "duration_minutes": 3,
        "instructions": "Walk to Platform 5"
      },
      {
        "mode": "tube",
        "line": "Northern",
        "from_station": "King's Cross St Pancras",
        "to_station": "Tottenham Court Road",
        "duration_minutes": 2,
        "instructions": "Take Northern from King's Cross St Pancras to Tottenham Court Road"
      }
    ],
    "sensory_summary": {
      "crowding": {
        "score": 65,
        "level": "Medium",
        "description": "Expected moderate crowding at peak time"
      },
      "noise": {
        "score": 70,
        "level": "High",
        "description": "Typical London underground noise levels"
      },
      "heat": {
        "score": 40,
        "level": "Low",
        "description": "Underground platforms are cool"
      },
      "reliability": {
        "score": 85,
        "level": "High",
        "description": "Northern line is reliable on weekdays"
      }
    },
    "warnings": [],
    "overall_score": 72.5,
    "recommended": true,
    "suggested_departure_time": "14:30",
    "expected_arrival_time": "14:55"
  },
  "alternative_route": {
    "journey_id": "route_1",
    "duration_minutes": 32,
    "number_of_changes": 2,
    "steps": [...],
    "sensory_summary": {...},
    "warnings": [],
    "overall_score": 68.0,
    "recommended": false,
    "suggested_departure_time": "14:30",
    "expected_arrival_time": "15:02"
  }
}
```

### Request Fields
- `origin` (string, required): Starting location name (e.g., "King's Cross Station")
- `destination` (string, required): Ending location name (e.g., "British Museum")
- `preferences` (object): User accessibility and comfort preferences
  - `avoid_crowds` (boolean): Prefer less crowded routes
  - `avoid_noise` (boolean): Prefer quieter routes
  - `avoid_heat` (boolean): Prefer cooler routes
  - `prefer_buses` (boolean): Prefer bus routes over underground
  - `minimise_changes` (boolean): Minimize number of transport changes
- `travel_date` (string, ISO 8601): Date of travel (YYYY-MM-DD)
- `start_time` (string, HH:MM): Desired departure time
- `arrive_by` (boolean): If true, `start_time` is treated as arrival deadline

### Response Format
- `success` (boolean): Whether the request succeeded
- `primary_route` (Route): Recommended route with highest overall_score
- `alternative_route` (Route, optional): Alternative route with different characteristics
- `error` (string, optional): Error message if success is false

Each Route contains:
- `journey_id`, `duration_minutes`, `number_of_changes`
- `steps`: Array of transport legs with mode, line, stations, duration, instructions
- `sensory_summary`: Crowding, noise, heat, and reliability scores (0-100 scale)
- `warnings`: Array of disruption/advisory messages
- `overall_score`: Composite score based on preferences (higher = better)
- `recommended`: Boolean flag for primary route
- `suggested_departure_time`, `expected_arrival_time`: ISO 8601 times

## Flutter Implementation

### How the App Uses the Backend

1. **Location Input**: User enters start and destination as text (e.g., "King's Cross Station")
2. **Preference Mapping**: 
   - `avoid_claustrophobic` → `avoid_crowds: true`
   - Other preferences map directly to backend format
3. **Request**: Sends POST to `/route` with location strings and preferences
4. **Route Display**: 
   - Primary route shown in blue
   - Alternative route shown in green
   - Each shows duration, changes, and sensory information
5. **Save Journey**: Selected route is saved with location names and duration

### Key Functions

#### `_planRoute()` (Async)
- Triggered when user clicks "Plan Route" button
- Shows loading dialog
- Calls `_fetchRoutesFromBackend()`
- Navigates to fullscreen map or shows error

#### `_fetchRoutesFromBackend()`
- Constructs POST request using:
  - User's entered location names (`_fromAddress`, `_toAddress`)
  - Selected travel date
  - Accessibility preferences (mapped to backend format)
- 30-second timeout
- Logs request/response for debugging
- Falls back to mock routes on error

#### `_parseBackendRoute(RouteData, isRecommended)`
- Converts TfL journey steps to display format
- Creates simple start→end polyline
- Extracts sensory summary for display
- Assigns color (blue for recommended, green for alternative)

### Console Logging
```
Sending route request to backend: {...}
Backend response status: 200
Backend response body: {...}
Successfully fetched 2 routes from backend
```

## Testing

### With Backend Running
```bash
# Terminal 1: Start backend
cd ui1/backend
python main.py

# Terminal 2: Run app
cd ui1
flutter run
```

Then:
1. Select locations in the route planner
2. Click "Plan Route"
3. See recommended + alternative routes

### Without Backend (Mock Fallback)
If backend is unavailable:
1. Connection error is caught
2. App falls back to `_generateMockRoutes()`
3. Console shows: "Falling back to mock routes"
4. Mock routes display normally

## Troubleshooting

### Backend Not Responding
```
Error: Backend returned 503
```
**Solution:** Check that backend is running and TfL API is accessible

### "No routes found"
```
Error: No valid routes parsed
```
**Solution:** 
1. Verify location names are recognized by TfL (use full station names)
2. Check console for parse errors
3. Try different location names

### Timeout Errors
```
Error: Timeout while trying to connect
```
**Solution:** 
1. Backend may be slow (runs TfL API queries)
2. Increase timeout in `_fetchRoutesFromBackend()` if needed
3. Check backend logs for TfL API errors

### Empty Response
```
success: false, error: "No routes found"
```
**Solution:**
1. Ensure locations are valid London transport stations/stops
2. Check if TfL has service on that date/time
3. Try well-known stations: "King's Cross Station", "Tottenham Court Road"

## Platform-Specific Notes

### Android Emulator
Replace `localhost` with `10.0.2.2`:
```dart
final url = Uri.parse('http://10.0.2.2:8000/route');
```

### iOS Simulator
Use either `localhost` or `127.0.0.1`

### Device Testing
For real devices, use the machine's IP address:
```dart
final url = Uri.parse('http://192.168.x.x:8000/route');
```

## Environment Variables

The backend uses:
- `TFL_APP_KEY`: TfL API key (optional, for higher rate limits)
- If not set, backend uses public TfL API with rate limiting

See `backend/.env` for configuration.
