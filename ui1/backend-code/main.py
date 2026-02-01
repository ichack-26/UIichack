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
        # Remove outer brackets and split
        import json
        points = json.loads(line_string)
       
        coordinates = []
        for point in points:
            if len(point) >= 2:
                # TfL uses [longitude, latitude] order
                lng, lat = point[0], point[1]
                coordinates.append(Coordinate(lat=lat, lng=lng))
       
        return coordinates
    except Exception as e:
        logger.warning(f"Failed to parse lineString: {e}")
        return []


def extract_leg_path(leg: Dict) -> List[Coordinate]:
    """Extract path coordinates from a journey leg."""
    path_data = leg.get("path", {})
   
    # Try lineString first (most detailed)
    line_string = path_data.get("lineString")
    if line_string:
        return parse_line_string(line_string)
   
    # Fallback: use stop points if available
    stop_points = path_data.get("stopPoints", [])
    if stop_points:
        coords = []
        for stop in stop_points:
            lat = stop.get("lat")
            lon = stop.get("lon")
            if lat and lon:
                coords.append(Coordinate(lat=lat, lng=lon))
        return coords
   
    # Final fallback: use departure and arrival points
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

    # Build datetime for scoring
    requested_datetime: Optional[datetime] = None
    if travel_date and travel_time:
        requested_datetime = datetime.combine(travel_date, travel_time)
    elif travel_time:
        requested_datetime = datetime.combine(datetime.now().date(), travel_time)

    steps: List[RouteStep] = []
    full_path: List[Coordinate] = []  # Combined path for entire journey
    num_transport_legs = 0
   
    start_coords: Optional[Coordinate] = None
    end_coords: Optional[Coordinate] = None

    for i, leg in enumerate(legs):
        mode_name = leg.get("mode", {}).get("name", "walking").lower()

        # Skip tiny walking legs
        if mode_name == "walking" and leg.get("duration", 0) < 2:
            continue

        from_point = leg.get("departurePoint", {})
        to_point = leg.get("arrivalPoint", {})

        from_name = from_point.get("commonName", "Unknown")
        to_name = to_point.get("commonName", "Unknown")
       
        # Extract coordinates for this leg
        leg_path = extract_leg_path(leg)
        departure_coords = get_point_coords(from_point)
        arrival_coords = get_point_coords(to_point)
       
        # Set overall start/end coords
        if i == 0 and departure_coords:
            start_coords = departure_coords
        if arrival_coords:
            end_coords = arrival_coords
       
        # Add to full path (avoid duplicates at leg boundaries)
        for coord in leg_path:
            if not full_path or (coord.lat != full_path[-1].lat or coord.lng != full_path[-1].lng):
                full_path.append(coord)
       
        # If leg_path is empty, at least add start/end points
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

    # -----------------------------------------------------------------
    # SCORING (time-aware)
    # -----------------------------------------------------------------
    crowding_score, crowd_level, crowd_desc = scorer.score_crowding(
        journey_data,
        preferences,
        disruptions,
        at=requested_datetime
    )

    noise_score, noise_level, noise_desc = scorer.score_noise(
        journey_data,
        preferences
    )

    heat_score, heat_level, heat_desc = scorer.score_heat(
        journey_data,
        preferences,
        at=requested_datetime
    )

    reliability_score, rel_level, rel_desc = scorer.score_reliability(
        journey_data,
        preferences,
        disruptions
    )

    overall_score = scorer.calculate_overall_score(
        crowding_score,
        noise_score,
        heat_score,
        reliability_score,
        preferences
    )

    warnings = scorer.generate_warnings(
        journey_data,
        disruptions,
        crowding_score,
        heat_score,
        at=requested_datetime
    )

    sensory_summary = SensorySummary(
        crowding={
            "score": crowding_score,
            "level": crowd_level,
            "description": crowd_desc
        },
        noise={
            "score": noise_score,
            "level": noise_level,
            "description": noise_desc
        },
        heat={
            "score": heat_score,
            "level": heat_level,
            "description": heat_desc
        },
        reliability={
            "score": reliability_score,
            "level": rel_level,
            "description": rel_desc
        }
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
# ROUTE ENDPOINT
# ---------------------------------------------------------------------
@app.post("/route", response_model=RouteResponse)
async def plan_route(request: RouteRequest):
    try:
        logger.info(f"Route request: {request.origin} → {request.destination}")
        logger.info(f"Date: {request.travel_date}, Time: {request.start_time}, Arrive by: {request.arrive_by}")

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

        # Apply preference bonuses
        if preferences_dict.get("prefer_buses"):
            fastest = min(r.duration_minutes for r in routes)
            for r in routes:
                if any("bus" in s.mode for s in r.steps) and r.duration_minutes <= fastest + 10:
                    r.overall_score += 15

        if preferences_dict.get("minimise_changes"):
            for r in routes:
                if r.number_of_changes == 0:
                    r.overall_score += 20
                elif r.number_of_changes == 1:
                    r.overall_score += 10

        routes.sort(key=lambda r: r.overall_score, reverse=True)
        routes[0].recommended = True

        primary = routes[0]
        alternative = None

        # Find a meaningfully different alternative
        for r in routes[1:]:
            primary_lines = {s.line for s in primary.steps if s.line}
            r_lines = {s.line for s in r.steps if s.line}
            overlap = len(primary_lines & r_lines) / max(len(primary_lines), 1) if primary_lines else 0
           
            if overlap < 0.5:  # Less than 50% line overlap
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