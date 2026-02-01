# UIichack - Journey Route Planning & Navigation App

A Flutter-based mobile application for planning, tracking, and navigating journeys with intelligent route optimization and real-time location tracking.

## 📁 Project Structure

```
UIichack/
├── ui1/                          # Main Flutter application
│   ├── lib/                      # Dart source code
│   │   ├── main.dart            # App entry point
│   │   ├── nav.dart             # Navigation configuration
│   │   ├── models/              # Data models
│   │   │   └── journey.dart     # Journey data structure
│   │   ├── pages/               # Screen pages
│   │   │   ├── home.dart        # Home page with journey history
│   │   │   ├── route_planner.dart # Route planning and selection
│   │   │   └── journey_details.dart # Journey detail view with map
│   │   ├── services/            # Business logic services
│   │   │   ├── routing_service.dart # Route calculation and snapping
│   │   │   └── advanced_navigation_service.dart # Turn-by-turn navigation
│   │   └── widgets/             # Reusable UI components
│   │       └── travel_route_summary.dart # Route summary display
│   ├── android/                 # Android platform code
│   ├── ios/                     # iOS platform code
│   ├── linux/                   # Linux platform code
│   ├── macos/                   # macOS platform code
│   ├── windows/                 # Windows platform code
│   ├── web/                     # Web platform code
│   ├── test/                    # Unit and widget tests
│   ├── pubspec.yaml            # Flutter dependencies and config
│   ├── analysis_options.yaml   # Dart linter configuration
│   └── README.md               # Original Flutter template README
├── backend/                      # Python backend (if applicable)
└── README.md                    # This file
```

## 🚀 Getting Started

### Prerequisites
- Flutter SDK (^3.10.8)
- Dart SDK (included with Flutter)
- An IDE (VS Code, Android Studio, or IntelliJ)

### Installation & Running

1. **Navigate to the app directory:**
   ```bash
   cd UIichack/ui1
   ```

2. **Get dependencies:**
   ```bash
   flutter pub get
   ```

3. **Run on connected device/emulator:**
   ```bash
   flutter run
   ```

4. **Build for production:**
   ```bash
   flutter build apk      # Android APK
   flutter build ipa      # iOS IPA
   flutter build web      # Web build
   ```

## 📱 Key Features

### Journey Management
- **Home Page** - View all journeys organized by Today/Upcoming/History
- **Route Planning** - Plan new routes with multiple transportation modes
- **Journey Details** - View detailed journey information with interactive map

### Route Optimization
- **Smart Routing** - Calculates optimal routes using backend routing service
- **Multiple Transport Modes** - Support for walking, bus, train, cycling, etc.
- **Route Scoring** - Evaluates routes based on distance, time, and accessibility

### Navigation
- **Live Tracking** - Real-time location updates during journey
- **Turn-by-Turn Guidance** - Step-by-step navigation instructions
- **Map Integration** - Interactive map display with polyline routes

### Location Services
- **Location Permission Handling** - Request and manage location permissions
- **Current Location Detection** - Get user's current GPS position
- **Map-based Point Selection** - Select start and destination via map interface

## 🔧 Technology Stack

### Frontend (Flutter/Dart)
- **flutter_map** - Interactive map widget
- **latlong2** - Geographic coordinates handling
- **geolocator** - GPS and location services
- **http** - API communication
- **shared_preferences** - Local data persistence
- **intl** - Internationalization and date formatting
- **fl_chart** - Data visualization (future use)

### Platform Support
- Android (native)
- iOS (native)
- Linux (desktop)
- macOS (desktop)
- Windows (desktop)
- Web (browser)

## 📂 Core Components

### `lib/models/journey.dart`
Defines the Journey data model with:
- Route coordinates (from/to lat/lng)
- Journey metadata (date, time, duration)
- Steps and polyline for visualization
- Senses-related scoring data

### `lib/pages/home.dart`
Home screen featuring:
- Scrollable journey list organized by date sections
- Section jump buttons (Today/Upcoming/History)
- Journey cards with quick access to details

### `lib/pages/route_planner.dart`
Route planning interface with:
- Start/destination point selection
- Multiple route display and comparison
- Route selection and saving
- Map-based location picker

### `lib/pages/journey_details.dart`
Journey details view with:
- Interactive map showing route
- Start and end location markers
- Live tracking capability
- Scrollable journey steps/instructions

### `lib/services/routing_service.dart`
Backend communication service:
- Calculates routes via external routing service
- Snaps user position to nearest road
- Retrieves turn-by-turn instructions
- Formats route data for display

### `lib/widgets/travel_route_summary.dart`
Reusable route display component:
- Shows journey date and time
- Displays start/end locations
- Shows transportation modes
- Indicates journey duration

## 🔌 API Integration

The app communicates with a backend service at `172.30.111.204:8000` for:
- Route calculation and optimization
- Turn-by-turn navigation directions
- Location snapping and validation

## 💾 Data Storage

- **SharedPreferences** - Stores journey history locally on device
- **In-memory State** - Navigation and UI state managed via Flutter StatefulWidgets

## 🧪 Testing

Run unit and widget tests:
```bash
flutter test
```

## 📝 Development Notes

- The app uses Material Design for consistent UI
- Location permissions are requested at runtime
- Routes are cached in local storage for offline access
- Navigation state is managed through service classes

## 🐛 Known Issues & Improvements

- Navigation service integration ready for advanced turn-by-turn features
- Error handling UI in place for failed route loading
- Map view fitting implemented for better route visualization

## 📄 License

Private project - All rights reserved

## 👤 Author

Developed as part of UIichack project

---

For detailed documentation on specific components, see the inline comments in respective Dart files.
