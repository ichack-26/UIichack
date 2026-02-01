from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import date, time


class SensoryLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class UserPreferences(BaseModel):
    avoid_crowds: bool = False
    avoid_noise: bool = False
    avoid_heat: bool = False
    prefer_buses: bool = False
    minimise_changes: bool = False


class Coordinate(BaseModel):
    """A single lat/lng coordinate point."""
    lat: float
    lng: float


class RouteStep(BaseModel):
    """A single leg/step of the journey."""
    mode: str  # tube, bus, walking, dlr, etc.
    line: Optional[str] = None
    from_station: str
    to_station: str
    duration_minutes: int
    instructions: str
    # Coordinates for this leg
    path: List[Coordinate] = Field(default_factory=list, description="Coordinates for this leg")
    departure_coords: Optional[Coordinate] = None
    arrival_coords: Optional[Coordinate] = None


class SensorySummary(BaseModel):
    crowding: dict  # {score, level, description}
    noise: dict
    heat: dict
    reliability: dict


class Route(BaseModel):
    journey_id: str
    duration_minutes: int
    number_of_changes: int
    steps: List[RouteStep]
    sensory_summary: SensorySummary
    warnings: List[str]
    overall_score: float
    recommended: bool = False
    suggested_departure_time: Optional[str] = None
    expected_arrival_time: Optional[str] = None
    # Full route path for mapping
    full_path: List[Coordinate] = Field(default_factory=list, description="Complete route coordinates for map display")
    start_coords: Optional[Coordinate] = None
    end_coords: Optional[Coordinate] = None


class RouteResponse(BaseModel):
    success: bool
    primary_route: Optional[Route] = None
    alternative_route: Optional[Route] = None
    error: Optional[str] = None


class RouteRequest(BaseModel):
    origin: str
    destination: str
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    travel_date: Optional[date] = Field(
        None, description="Date of travel (YYYY-MM-DD)"
    )
    start_time: Optional[time] = Field(
        None, description="Desired departure time (HH:MM)"
    )
    arrive_by: bool = Field(
        False, description="If true, time is treated as arrival time"
    )
