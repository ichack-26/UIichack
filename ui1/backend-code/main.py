from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import (
    RouteRequest, RouteResponse, Route, RouteStep,
    SensorySummary, Coordinate
)
from services.tfl import TfLClient
from services.scoring import JourneyScorer
import logging
from typing import List, Dict, Optional
import os
from datetime import datetime, date, time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CalmRoute TfL API",
    description="Neurodivergent-friendly journey planning for London transport",
    version="1.0.0"
)

# CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tfl_client = TfLClient()
scorer = JourneyScorer()


# ---------------------------------------------------------------------
# LINE CLASSIFICATIONS FOR PREFERENCES
# ---------------------------------------------------------------------
NOISY_LINES = {"central", "northern", "victoria", "piccadilly", "bakerloo"}
HOT_LINES = {"central", "northern", "bakerloo", "piccadilly", "victoria", "jubilee", "waterloo & city"}
COOL_LINES = {"circle", "district", "metropolitan", "hammersmith & city", "elizabeth"}
MAJOR_HUBS = {
    "oxford circus", "victoria", "bank", "liverpool street",
    "king's cross st. pancras", "kings cross", "waterloo",
    "london bridge", "paddington", "leicester square", "green park"
}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CalmRoute TfL API",
        "tfl_auth": "configured" if os.getenv("TFL_APP_KEY") else "no auth (rate limited)"
    }


# ---------------------------------------------------------------------
# COORDINATE EXTRACTION HELPERS
# ---------------------------------------------------------------------
def parse_line_string(line_string: str) -> List[Coordinate]:
    """
    Parse TfL lineString format into list of Coordinates.
    TfL format: "[[lng,lat],[lng,lat],...]" (note: longitude first!)
    """
    if not line_string:
        return []
   
    try:
        import json
        points = json.loads(line_string)
       
        coordinates = []
        for point in points:
            if len(point) >= 2:
                lng, lat = point[0], point[1]
                coordinates.append(Coordinate(lat=lat, lng=lng))
       
        return coordinates
    except Exception as e:
        logger.warning(f"Failed to parse lineString: {e}")
        return []


def extract_leg_path(leg: Dict) -> List[Coordinate]:
    """Extract path coordinates from a journey leg."""
    path_data = leg.get("path", {})
   
    line_string = path_data.get("lineString")
    if line_string:
        return parse_line_string(line_string)
   
    stop_points = path_data.get("stopPoints", [])
    if stop_points:
        coords = []
        for stop in stop_points:
            lat = stop.get("lat")
            lon = stop.get("lon")
            if lat and lon:
                coords.append(Coordinate(lat=lat, lng=lon))
        return coords
   
    coords = []
    dep = leg.get("departurePoint", {})
    arr = leg.get("arrivalPoint", {})
   
    if dep.get("lat") and dep.get("lon"):
        coords.append(Coordinate(lat=dep["lat"], lng=dep["lon"]))
    if arr.get("lat") and arr.get("lon"):
        coords.append(Coordinate(lat=arr["lat"], lng=arr["lon"]))
   
    return coords


def get_point_coords(point: Dict) -> Optional[Coordinate]:
    """Extract coordinates from a departure/arrival point."""
    lat = point.get("lat")
    lon = point.get("lon")
    if lat is not None and lon is not None:
        return Coordinate(lat=lat, lng=lon)
    return None


# ---------------------------------------------------------------------
# TIME-AWARE JOURNEY PARSER WITH COORDINATES
# ---------------------------------------------------------------------
def parse_tfl_journey(
    journey_data: Dict,
    journey_id: str,
    preferences: dict,
    disruptions: Dict[str, str],
    travel_date: Optional[date],
    travel_time: Optional[time]
) -> Route:
    """
    Parse TfL journey response into Route model with sensory scoring.
    Now includes path coordinates for map display.
    """

    start_time_raw = journey_data.get("startDateTime")
    arrival_time_raw = journey_data.get("arrivalDateTime")

    def format_time(dt: Optional[str]) -> Optional[str]:
        if not dt:
            return None
        try:
            return datetime.fromisoformat(dt.replace('Z', '+00:00')).strftime("%H:%M")
        except:
            return None

    legs = journey_data.get("legs", [])
    duration = journey_data.get("duration", 0)

    requested_datetime: Optional[datetime] = None
    if travel_date and travel_time:
        requested_datetime = datetime.combine(travel_date, travel_time)
    elif travel_time:
        requested_datetime = datetime.combine(datetime.now().date(), travel_time)

    steps: List[RouteStep] = []
    full_path: List[Coordinate] = []
    num_transport_legs = 0
   
    start_coords: Optional[Coordinate] = None
    end_coords: Optional[Coordinate] = None

    for i, leg in enumerate(legs):
        mode_name = leg.get("mode", {}).get("name", "walking").lower()

        if mode_name == "walking" and leg.get("duration", 0) < 2:
            continue

        from_point = leg.get("departurePoint", {})
        to_point = leg.get("arrivalPoint", {})

        from_name = from_point.get("commonName", "Unknown")
        to_name = to_point.get("commonName", "Unknown")
       
        leg_path = extract_leg_path(leg)
        departure_coords = get_point_coords(from_point)
        arrival_coords = get_point_coords(to_point)
       
        if i == 0 and departure_coords:
            start_coords = departure_coords
        if arrival_coords:
            end_coords = arrival_coords
       
        for coord in leg_path:
            if not full_path or (coord.lat != full_path[-1].lat or coord.lng != full_path[-1].lng):
                full_path.append(coord)
       
        if not leg_path:
            if departure_coords and (not full_path or
                (departure_coords.lat != full_path[-1].lat or departure_coords.lng != full_path[-1].lng)):
                full_path.append(departure_coords)
            if arrival_coords and (not full_path or
                (arrival_coords.lat != full_path[-1].lat or arrival_coords.lng != full_path[-1].lng)):
                full_path.append(arrival_coords)

        line_name = None
        if leg.get("routeOptions"):
            line_name = leg["routeOptions"][0].get("name")

        if mode_name != "walking":
            num_transport_legs += 1

        if mode_name == "walking":
            instructions = f"Walk to {to_name}"
        elif "bus" in mode_name:
            instructions = f"Take {line_name or 'bus'} from {from_name} to {to_name}"
        else:
            instructions = f"Take {line_name or 'tube'} from {from_name} to {to_name}"

        steps.append(RouteStep(
            mode=mode_name,
            line=line_name,
            from_station=from_name,
            to_station=to_name,
            duration_minutes=leg.get("duration", 0),
            instructions=instructions,
            path=leg_path,
            departure_coords=departure_coords,
            arrival_coords=arrival_coords,
        ))

    number_of_changes = max(0, num_transport_legs - 1)

    # SCORING
    crowding_score, crowd_level, crowd_desc = scorer.score_crowding(
        journey_data, preferences, disruptions, at=requested_datetime
    )
    noise_score, noise_level, noise_desc = scorer.score_noise(
        journey_data, preferences
    )
    heat_score, heat_level, heat_desc = scorer.score_heat(
        journey_data, preferences, at=requested_datetime
    )
    reliability_score, rel_level, rel_desc = scorer.score_reliability(
        journey_data, preferences, disruptions
    )

    overall_score = scorer.calculate_overall_score(
        crowding_score, noise_score, heat_score, reliability_score, preferences
    )

    warnings = scorer.generate_warnings(
        journey_data, disruptions, crowding_score, heat_score, at=requested_datetime
    )

    sensory_summary = SensorySummary(
        crowding={"score": crowding_score, "level": crowd_level, "description": crowd_desc},
        noise={"score": noise_score, "level": noise_level, "description": noise_desc},
        heat={"score": heat_score, "level": heat_level, "description": heat_desc},
        reliability={"score": reliability_score, "level": rel_level, "description": rel_desc}
    )

    return Route(
        journey_id=journey_id,
        duration_minutes=duration,
        number_of_changes=number_of_changes,
        steps=steps,
        sensory_summary=sensory_summary,
        warnings=warnings,
        overall_score=overall_score,
        recommended=False,
        suggested_departure_time=format_time(start_time_raw),
        expected_arrival_time=format_time(arrival_time_raw),
        full_path=full_path,
        start_coords=start_coords,
        end_coords=end_coords,
    )


# ---------------------------------------------------------------------
# APPLY PREFERENCE PENALTIES AND BONUSES
# ---------------------------------------------------------------------
def apply_preference_adjustments(routes: List[Route], preferences: Dict) -> List[Route]:
    """
    Apply heavy penalties and bonuses based on user preferences.
    This makes preferences have a REAL impact on route selection.
    """
   
    for r in routes:
        route_lines = {s.line.lower() for s in r.steps if s.line}
        route_stations = set()
        for s in r.steps:
            route_stations.add(s.from_station.lower())
            route_stations.add(s.to_station.lower())
       
        # ----- AVOID NOISE -----
        if preferences.get("avoid_noise"):
            noisy_lines_used = route_lines & NOISY_LINES
            if noisy_lines_used:
                penalty = len(noisy_lines_used) * 20  # -20 per noisy line
                r.overall_score -= penalty
                logger.info(f"{r.journey_id}: -{penalty} for noisy lines {noisy_lines_used}")
            else:
                r.overall_score += 15  # Bonus for avoiding all noisy lines
                logger.info(f"{r.journey_id}: +15 bonus for no noisy lines")
       
        # ----- AVOID HEAT -----
        if preferences.get("avoid_heat"):
            hot_lines_used = route_lines & HOT_LINES
            cool_lines_used = route_lines & COOL_LINES
            has_bus = any("bus" in s.mode for s in r.steps)
           
            if hot_lines_used:
                penalty = len(hot_lines_used) * 18  # -18 per hot line
                r.overall_score -= penalty
                logger.info(f"{r.journey_id}: -{penalty} for hot lines {hot_lines_used}")
           
            if cool_lines_used:
                bonus = len(cool_lines_used) * 15  # +15 per cool line
                r.overall_score += bonus
                logger.info(f"{r.journey_id}: +{bonus} bonus for cool lines {cool_lines_used}")
           
            if has_bus:
                r.overall_score += 12  # Buses are cooler
                logger.info(f"{r.journey_id}: +12 bonus for bus (cooler)")
       
        # ----- AVOID CROWDS -----
        if preferences.get("avoid_crowds"):
            hubs_in_route = route_stations & MAJOR_HUBS
            if len(hubs_in_route) > 0:
                penalty = len(hubs_in_route) * 12  # -12 per major hub
                r.overall_score -= penalty
                logger.info(f"{r.journey_id}: -{penalty} for major hubs {hubs_in_route}")
            else:
                r.overall_score += 20  # Big bonus for avoiding all major hubs
                logger.info(f"{r.journey_id}: +20 bonus for avoiding major hubs")
       
        # ----- PREFER BUSES -----
        if preferences.get("prefer_buses"):
            has_bus = any("bus" in s.mode for s in r.steps)
            if has_bus:
                r.overall_score += 30  # Strong preference for buses
                logger.info(f"{r.journey_id}: +30 bonus for bus route")
            else:
                r.overall_score -= 10  # Slight penalty for no bus
                logger.info(f"{r.journey_id}: -10 penalty for no bus")
       
        # ----- MINIMISE CHANGES -----
        if preferences.get("minimise_changes"):
            if r.number_of_changes == 0:
                r.overall_score += 35  # Big bonus for direct
                logger.info(f"{r.journey_id}: +35 bonus for direct route")
            elif r.number_of_changes == 1:
                r.overall_score += 15
                logger.info(f"{r.journey_id}: +15 bonus for 1 change")
            elif r.number_of_changes >= 3:
                r.overall_score -= 20  # Penalty for many changes
                logger.info(f"{r.journey_id}: -20 penalty for {r.number_of_changes} changes")
   
    return routes


# ---------------------------------------------------------------------
# ROUTE ENDPOINT
# ---------------------------------------------------------------------
@app.post("/route", response_model=RouteResponse)
async def plan_route(request: RouteRequest):
    try:
        logger.info(f"Route request: {request.origin} → {request.destination}")
        logger.info(f"Date: {request.travel_date}, Time: {request.start_time}, Arrive by: {request.arrive_by}")
        logger.info(f"=== PREFERENCES ===")
        logger.info(f"  avoid_crowds: {request.preferences.avoid_crowds}")
        logger.info(f"  avoid_noise: {request.preferences.avoid_noise}")
        logger.info(f"  avoid_heat: {request.preferences.avoid_heat}")
        logger.info(f"  prefer_buses: {request.preferences.prefer_buses}")
        logger.info(f"  minimise_changes: {request.preferences.minimise_changes}")

        journey_data = tfl_client.get_journey_results(
            from_location=request.origin,
            to_location=request.destination,
            travel_date=request.travel_date,
            travel_time=request.start_time,
            arrive_by=request.arrive_by
        )

        if not journey_data:
            return RouteResponse(success=False, error="TfL API unavailable. Please try again.")
       
        if "error" in journey_data:
            return RouteResponse(success=False, error=journey_data["error"])
       
        if "journeys" not in journey_data or not journey_data["journeys"]:
            return RouteResponse(success=False, error="No routes found between these locations.")

        disruptions = tfl_client.get_line_disruptions()
        preferences_dict = request.preferences.model_dump()

        routes: List[Route] = []

        for idx, journey in enumerate(journey_data["journeys"][:5]):
            try:
                route = parse_tfl_journey(
                    journey,
                    f"route_{idx}",
                    preferences_dict,
                    disruptions,
                    request.travel_date,
                    request.start_time
                )
                routes.append(route)
            except Exception as e:
                logger.warning(f"Failed to parse journey {idx}: {e}")

        if not routes:
            return RouteResponse(success=False, error="No valid routes parsed")

        # Log initial scores
        logger.info("=== SCORES BEFORE PREFERENCE ADJUSTMENTS ===")
        for r in routes:
            lines = [s.line for s in r.steps if s.line]
            logger.info(f"{r.journey_id}: score={r.overall_score:.1f}, lines={lines}")

        # Apply preference penalties and bonuses
        routes = apply_preference_adjustments(routes, preferences_dict)

        # Log adjusted scores
        logger.info("=== SCORES AFTER PREFERENCE ADJUSTMENTS ===")
        for r in routes:
            logger.info(f"{r.journey_id}: score={r.overall_score:.1f}")

        # Sort by score and mark recommended
        routes.sort(key=lambda r: r.overall_score, reverse=True)
        routes[0].recommended = True

        logger.info(f"=== RECOMMENDED: {routes[0].journey_id} (score: {routes[0].overall_score:.1f}) ===")

        primary = routes[0]
        alternative = None

        # Find a meaningfully different alternative
        for r in routes[1:]:
            primary_lines = {s.line for s in primary.steps if s.line}
            r_lines = {s.line for s in r.steps if s.line}
            overlap = len(primary_lines & r_lines) / max(len(primary_lines), 1) if primary_lines else 0
           
            if overlap < 0.5:
                alternative = r
                break

        if not alternative and len(routes) > 1:
            alternative = routes[1]

        return RouteResponse(
            success=True,
            primary_route=primary,
            alternative_route=alternative
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return RouteResponse(success=False, error=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)