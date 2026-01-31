# Flutter Backend Integration - Quick Start

## What Changed

The Flutter app now calls the CalmRoute TfL backend server (in `ui1/backend/`) instead of using mock routes.

### Key Updates

1. **Route Planning Endpoint**: Changed from mock routes to `POST http://localhost:8000/route`

2. **API Contract**:
   - **Request**: Sends location names (strings) + preferences
   - **Response**: Returns 1-2 recommended routes with sensory analysis (crowding, noise, heat, reliability scores)

3. **Implementation**:
   - `_planRoute()` - Now async with loading dialog
   - `_fetchRoutesFromBackend()` - Calls backend, handles errors gracefully
   - `_parseBackendRoute()` - Converts TfL journey data to Flutter Route objects

4. **Graceful Fallback**: If backend is unavailable, automatically falls back to mock routes

## Quick Start

### 1. Start the Backend
```bash
cd ui1/backend
pip install -r requirements.txt
python main.py
# Backend runs on http://localhost:8000
```

### 2. Run the Flutter App
```bash
cd ui1
flutter run
```

### 3. Plan a Route
1. Enter location names (e.g., "King's Cross Station" → "British Museum")
2. Click "Plan Route"
3. Backend queries TfL API and returns 2 routes
4. Select route on fullscreen map

## API Endpoints

### POST /route
Accepts location names and preferences, returns recommended + alternative routes with sensory analysis.

### GET /health
Returns service status and TfL API auth status.

## Preference Mapping

| Flutter | Backend | Meaning |
|---------|---------|---------|
| avoid_claustrophobic | avoid_crowds | Prefer less crowded routes |
| (new) | avoid_noise | Prefer quieter routes |
| (new) | avoid_heat | Prefer cooler routes |
| require_lift | (not implemented) | Requires elevator access |
| avoid_stairs | (not implemented) | No stairs |
| wheelchair_accessible | (not implemented) | Full wheelchair access |

**Note**: Currently only `avoid_crowds` (from `avoid_claustrophobic`) is connected. Other preferences can be mapped when UI is expanded.

## Route Display

- **Blue route** = Primary recommended route (best overall score)
- **Green route** = Alternative route (different characteristics)
- Each shows: Duration, # of changes, crowding level, step-by-step instructions

## Testing Without Backend

If backend is not running, the app gracefully falls back to mock routes. Check console for:
```
Falling back to mock routes
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No routes found" | Use valid London station names, check backend logs |
| Connection timeout | Ensure backend is running on localhost:8000 |
| Empty response | Backend may be slow (TfL API queries), wait or increase timeout |
| Routes don't display | Check console for parse errors in route data |

## Architecture Notes

- Location input is now **string-based** (station/stop names) instead of coordinates
- Routes use simple start→end polylines (full turn-by-turn not needed for display)
- Route recommendations based on sensory scoring algorithm in backend
- All timing and disruption analysis done by backend, not Flutter app

## Next Steps

1. Test location input format (use full station names)
2. Expand UI preferences to include noise, heat preferences
3. Display full step-by-step instructions in route details
4. Add arrival/departure time selection UI
5. Cache route results to reduce API calls
