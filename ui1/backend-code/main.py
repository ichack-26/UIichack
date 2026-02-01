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
    if not line_string:
        return []
    try:
        import json
        points = json.loads(line_string)
        return [Coordinate(lat=pt[1], lng=pt[0]) for pt in points if len(pt) >= 2]
    except Exception as e:
        logger.warning(f"Failed to parse lineString: {e}")
        return []


def extract_leg_path(leg: Dict) -> List[Coordinate]:
    path_data = leg.get("path", {})
    if line_string := path_data.get("lineString"):
        return parse_line_string(line_string)
    if stop_points := path_data.get("stopPoints", []):
        return [Coordinate(lat=s.get("lat"), lng=s.get("lon")) for s in stop_points if s.get("lat") and s.get("lon")]
    coords = []
    if dep := leg.get("departurePoint", {}):
        if dep.get("lat") and dep.get("lon"):
            coords.append(Coordinate(lat=dep["lat"], lng=dep["lon"]))
    if arr := leg.get("arrivalPoint", {}):
        if arr.get("lat") and arr.get("lon"):
            coords.append(Coordinate(lat=arr["lat"], lng=arr["lon"]))
    return coords


def get_point_coords(point: Dict) -> Optional[Coordinate]:
    if lat := point.get("lat"):
        if lon := point.get("lon"):
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
    start_time_raw = journey_data.get("startDateTime")
    arrival_time_raw = journey_data.get("arrivalDateTime")

    def format_time(dt: Optional[str]) -> Optional[str]:
        if not dt:
            return None
        try:
            return datetime.fromisoformat(dt.replace("Z", "+00:00")).strftime("%H:%M")
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
            if departure_coords and (not full_path or (departure_coords.lat != full_path[-1].lat or departure_coords.lng != full_path[-1].lng)):
                full_path.append(departure_coords)
            if arrival_coords and (not full_path or (arrival_coords.lat != full_path[-1].lat or arrival_coords.lng != full_path[-1].lng)):
                full_path.append(arrival_coords)

        line_name = leg.get("routeOptions", [{}])[0].get("name") if leg.get("routeOptions") else None

        if mode_name != "walking":
            num_transport_legs += 1

        instructions = f"Walk to {to_name}" if mode_name == "walking" else f"Take {line_name or mode_name} from {from_name} to {to_name}"

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
    crowding_score, crowd_level, crowd_desc = scorer.score_crowding(journey_data, preferences, disruptions, at=requested_datetime)
    noise_score, noise_level, noise_desc = scorer.score_noise(journey_data, preferences)
    heat_score, heat_level, heat_desc = scorer.score_heat(journey_data, preferences, at=requested_datetime)
    reliability_score, rel_level, rel_desc = scorer.score_reliability(journey_data, preferences, disruptions)

    # Pass journey_data to calculate_overall_score for train preference logic
    overall_score = scorer.calculate_overall_score(
        crowding_score, noise_score, heat_score, reliability_score, preferences, journey_data
    )

    warnings = scorer.generate_warnings(journey_data, disruptions, crowding_score, heat_score, at=requested_datetime)

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
    for r in routes:
        route_lines = {s.line.lower() for s in r.steps if s.line}
        route_stations = {s.from_station.lower() for s in r.steps} | {s.to_station.lower() for s in r.steps}

        if preferences.get("avoid_noise"):
            noisy_lines_used = route_lines & NOISY_LINES
            r.overall_score += 15 if not noisy_lines_used else -len(noisy_lines_used) * 20

        if preferences.get("avoid_heat"):
            hot_lines_used = route_lines & HOT_LINES
            cool_lines_used = route_lines & COOL_LINES
            has_bus = any("bus" in s.mode for s in r.steps)
            r.overall_score += len(cool_lines_used) * 15 - len(hot_lines_used) * 18
            if has_bus:
                r.overall_score += 12

        if preferences.get("avoid_crowds"):
            hubs_in_route = route_stations & MAJOR_HUBS
            r.overall_score += 20 if not hubs_in_route else -len(hubs_in_route) * 12

        if preferences.get("prefer_buses"):
            has_bus = any("bus" in s.mode for s in r.steps)
            r.overall_score += 30 if has_bus else -10

        if preferences.get("minimise_changes"):
            if r.number_of_changes == 0:
                r.overall_score += 35
            elif r.number_of_changes == 1:
                r.overall_score += 15
            elif r.number_of_changes >= 3:
                r.overall_score -= 20

    return routes


# ---------------------------------------------------------------------
# ROUTE ENDPOINT
# ---------------------------------------------------------------------
@app.post("/route", response_model=RouteResponse)
async def plan_route(request: RouteRequest):
    try:
        logger.info(f"Route request: {request.origin} → {request.destination}")
        logger.info(f"Date: {request.travel_date}, Time: {request.start_time}, Arrive by: {request.arrive_by}")
        preferences_dict = request.preferences.model_dump()

        journey_data = tfl_client.get_journey_results(
            from_location=request.origin,
            to_location=request.destination,
            travel_date=request.travel_date,
            travel_time=request.start_time,
            arrive_by=request.arrive_by
        )

        if not journey_data or "error" in journey_data or not journey_data.get("journeys"):
            return RouteResponse(success=False, error=journey_data.get("error", "No routes found"))

        disruptions = tfl_client.get_line_disruptions()

        routes: List[Route] = []
        for idx, journey in enumerate(journey_data["journeys"][:5]):
            try:
                routes.append(parse_tfl_journey(journey, f"route_{idx}", preferences_dict, disruptions, request.travel_date, request.start_time))
            except Exception as e:
                logger.warning(f"Failed to parse journey {idx}: {e}")

        if not routes:
            return RouteResponse(success=False, error="No valid routes parsed")

        # Apply preference adjustments
        routes = apply_preference_adjustments(routes, preferences_dict)

        # Sort by score and pick recommended
        routes.sort(key=lambda r: r.overall_score, reverse=True)
        routes[0].recommended = True
        primary = routes[0]
        alternative = next((r for r in routes[1:] if len({s.line for s in r.steps if s.line} & {s.line for s in primary.steps if s.line}) / max(len({s.line for s in primary.steps if s.line}), 1) < 0.5), None) or (routes[1] if len(routes) > 1 else None)

        return RouteResponse(success=True, primary_route=primary, alternative_route=alternative)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return RouteResponse(success=False, error=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
