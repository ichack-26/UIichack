import requests
import os
from typing import List, Dict, Optional
from datetime import datetime, date, time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TfLClient:
    BASE_URL = "https://api.tfl.gov.uk"
    
    def __init__(self):
        self.app_id = os.getenv("TFL_APP_ID", "")
        self.app_key = os.getenv("TFL_APP_KEY", "")
        self.timeout = 10
    
    def _build_auth_params(self) -> Dict[str, str]:
        """Add auth params if keys are available"""
        params = {}
        if self.app_id and self.app_key:
            params["app_id"] = self.app_id
            params["app_key"] = self.app_key
        return params
    
    def get_journey_results(self, from_location: str, to_location: str, travel_date: Optional[date] = None,
    travel_time: Optional[time] = None,
    arrive_by: bool = False) -> Optional[Dict]:
        from urllib.parse import quote
        
        # URL encode the locations
        from_encoded = quote(from_location)
        to_encoded = quote(to_location)
        
        url = f"{self.BASE_URL}/Journey/JourneyResults/{from_encoded}/to/{to_encoded}"
        
        params = self._build_auth_params()
        params.update({
            "mode": "bus,cable-car,coach,dlr,elizabeth-line,international-rail,national-rail,overground,plane,replacement-bus,river-bus,river-tour,tram,tube,walking",
            "timeIs": "Departing",
            "journeyPreference": "LeastTime",
            "maxWalkingMinutes": "15",
            "walkingSpeed": "Average"
        })

        if travel_date:
            params["date"] = travel_date.strftime("%Y%m%d")

        if travel_time:
            params["time"] = travel_time.strftime("%H%M")
            params["timeIs"] = "Arriving" if arrive_by else "Departing"
        
        try:
            logger.info(f"Calling TfL API: {from_location} → {to_location}")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Check if we got disambiguation results instead of journeys
            if "$type" in data and "Disambiguation" in data["$type"]:
                logger.info("Got disambiguation result, trying to resolve...")
                
                # Try to pick the best station match
                resolved_from = from_location
                resolved_to = to_location
                
                # Handle 'from' disambiguation
                if "fromLocationDisambiguation" in data:
                    from_options = data["fromLocationDisambiguation"].get("disambiguationOptions", [])
                    if from_options:
                        # Pick first tube/bus stop (best match)
                        for option in from_options:
                            place = option.get("place", {})
                            if place.get("placeType") == "StopPoint":
                                modes = place.get("modes", [])
                                if "tube" in modes or "bus" in modes:
                                    resolved_from = option.get("parameterValue", from_location)
                                    logger.info(f"Resolved from: {from_location} -> {resolved_from}")
                                    break
                
                # Handle 'to' disambiguation
                if "toLocationDisambiguation" in data:
                    to_options = data["toLocationDisambiguation"].get("disambiguationOptions", [])
                    if to_options:
                        # Pick first tube/bus stop (best match)
                        for option in to_options:
                            place = option.get("place", {})
                            if place.get("placeType") == "StopPoint":
                                modes = place.get("modes", [])
                                if "tube" in modes or "bus" in modes:
                                    resolved_to = option.get("parameterValue", to_location)
                                    logger.info(f"Resolved to: {to_location} -> {resolved_to}")
                                    break
            
                # Retry with resolved locations
                if resolved_from != from_location or resolved_to != to_location:
                    logger.info(f"Retrying with resolved locations: {resolved_from} → {resolved_to}")
                    return self.get_journey_results(resolved_from, resolved_to)
                else:
                    logger.warning("Could not resolve disambiguation")
                    return None
            
            # Filter out journeys containing national rail
            # if "journeys" in data:
            #     filtered_journeys = []
            #     for journey in data["journeys"]:
            #         has_national_rail = False
            #         for leg in journey.get("legs", []):
            #             mode = leg.get("mode", {}).get("name", "").lower()
            #             if "national-rail" in mode or "rail" in mode:
            #                 has_national_rail = True
            #                 break
                    
            #         if not has_national_rail:
            #             filtered_journeys.append(journey)
                
            #     data["journeys"] = filtered_journeys
            
            return data
            
        except requests.exceptions.Timeout:
            logger.error("TfL API timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"TfL API error: {e}")
            return None
    def get_line_status(self) -> Optional[Dict]:
        """
        Get current line status for tube and buses
        """
        url = f"{self.BASE_URL}/Line/Mode/tube,bus/Status"
        params = self._build_auth_params()
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Line status API error: {e}")
            return None
    
    def get_line_disruptions(self) -> Dict[str, str]:
        """
        Returns a dict of line_name -> status_description
        e.g. {"Northern": "Minor Delays", "Central": "Good Service"}
        """
        disruptions = {}
        status_data = self.get_line_status()
        
        if not status_data:
            return disruptions
        
        for line in status_data:
            line_name = line.get("name", "")
            statuses = line.get("lineStatuses", [])
            
            if statuses:
                # Take first status
                status_severity = statuses[0].get("statusSeverityDescription", "Good Service")
                disruptions[line_name] = status_severity
        
        return disruptions