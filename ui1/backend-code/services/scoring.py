
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Known deep-level lines (hot and noisy)
DEEP_LEVEL_LINES = {
    "central", "northern", "piccadilly", "bakerloo", "victoria",
    "waterloo & city", "jubilee"
}

# Known hot lines
HOT_LINES = {"central", "bakerloo", "northern"}

# Known noisy lines
NOISY_LINES = {"central", "northern", "piccadilly", "bakerloo", "victoria"}

# Major interchange stations (crowded)
MAJOR_HUBS = {
    "kings cross st pancras", "king's cross st. pancras", "oxford circus",
    "victoria", "waterloo", "london bridge", "liverpool street",
    "bank", "leicester square", "green park", "paddington"
}


class JourneyScorer:
   
    @staticmethod
    def is_peak_hour(at: Optional[datetime] = None) -> bool:
        """
        Check if given time is peak hour (Mon-Fri 7:30-9:30am or 5-7pm)
       
        Args:
            at: The datetime to check. If None, uses current time.
        """
        now = at if at is not None else datetime.now()
       
        if now.weekday() >= 5:  # Weekend
            return False
       
        hour = now.hour
        minute = now.minute
       
        # Morning peak: 7:30-9:30
        if hour == 7 and minute >= 30:
            return True
        if hour == 8:
            return True
        if hour == 9 and minute < 30:
            return True
       
        # Evening peak: 17:00-19:00
        if 17 <= hour < 19:
            return True
       
        return False
   
    @staticmethod
    def score_crowding(
        journey_data: Dict,
        preferences: Dict,
        disruptions: Dict[str, str],
        at: Optional[datetime] = None
    ) -> tuple[int, str, str]:
        """
        Score crowding from 0-100 (100 = least crowded)
        Returns: (score, level, description)
       
        Args:
            at: Reference time for peak hour calculation. If None, uses current time.
        """
        score = 100
        reasons = []
       
        legs = journey_data.get("legs", [])
        num_changes = sum(1 for leg in legs if leg.get("mode", {}).get("name") != "walking")
       
        # Peak hour penalty
        if JourneyScorer.is_peak_hour(at):
            score -= 30
            reasons.append("peak travel time")
       
        # Major hub penalty
        major_hub_count = 0
        for leg in legs:
            from_name = leg.get("departurePoint", {}).get("commonName", "").lower()
            to_name = leg.get("arrivalPoint", {}).get("commonName", "").lower()
           
            if from_name in MAJOR_HUBS:
                major_hub_count += 1
            if to_name in MAJOR_HUBS:
                major_hub_count += 1
       
        score -= major_hub_count * 10
        if major_hub_count > 0:
            reasons.append(f"{major_hub_count} major stations")
       
        # Changes penalty
        score -= num_changes * 5
        if num_changes > 1:
            reasons.append(f"{num_changes} changes")
       
        # Deep level lines during peak
        if JourneyScorer.is_peak_hour(at):
            for leg in legs:
                line_name = leg.get("routeOptions", [{}])[0].get("name", "").lower() if leg.get("routeOptions") else ""
                if any(deep in line_name for deep in DEEP_LEVEL_LINES):
                    score -= 10
       
        # Clamp score
        score = max(0, min(100, score))
       
        # Determine level
        if score >= 70:
            level = "Low"
        elif score >= 40:
            level = "Medium"
        else:
            level = "High"
       
        description = f"Expected to be {level.lower()}ly crowded"
        if reasons:
            description += f" ({', '.join(reasons)})"
       
        return score, level, description
   
    @staticmethod
    def score_noise(journey_data: Dict, preferences: Dict) -> tuple[int, str, str]:
        """Score noise level 0-100 (100 = quietest)"""
        score = 100
        reasons = []
       
        legs = journey_data.get("legs", [])
       
        for leg in legs:
            mode = leg.get("mode", {}).get("name", "").lower()
            line_name = leg.get("routeOptions", [{}])[0].get("name", "").lower() if leg.get("routeOptions") else ""
           
            # Bus bonus
            if "bus" in mode:
                score += 10
                continue
           
            # Deep level penalty
            if any(deep in line_name for deep in DEEP_LEVEL_LINES):
                score -= 20
                reasons.append("deep-level tube")
           
            # Specific noisy lines
            if any(noisy in line_name for noisy in NOISY_LINES):
                score -= 15
                if "central" in line_name or "victoria" in line_name:
                    reasons.append(f"{line_name.title()} line can be loud")
       
        score = max(0, min(100, score))
       
        if score >= 70:
            level = "Low"
        elif score >= 40:
            level = "Medium"
        else:
            level = "High"
       
        description = f"{level} noise expected"
        if reasons:
            description += f" ({', '.join(set(reasons))})"
       
        return score, level, description
   
    @staticmethod
    def score_heat(
        journey_data: Dict,
        preferences: Dict,
        at: Optional[datetime] = None
    ) -> tuple[int, str, str]:
        """
        Score heat level 0-100 (100 = coolest)
       
        Args:
            at: Reference time for peak hour and season calculation
        """
        score = 100
        reasons = []
       
        legs = journey_data.get("legs", [])
       
        # Check if summer months (Jun-Aug)
        ref_time = at if at is not None else datetime.now()
        month = ref_time.month
        is_summer = month in [6, 7, 8]
       
        for leg in legs:
            mode = leg.get("mode", {}).get("name", "").lower()
            line_name = leg.get("routeOptions", [{}])[0].get("name", "").lower() if leg.get("routeOptions") else ""
           
            # Bus bonus (fresh air)
            if "bus" in mode:
                score += 15
                continue
           
            # Deep level penalty
            if any(deep in line_name for deep in DEEP_LEVEL_LINES):
                score -= 25
           
            # Known hot lines
            if any(hot in line_name for hot in HOT_LINES):
                score -= 20
                reasons.append(f"{line_name.title()} line runs warm")
           
            # Elizabeth line bonus (air-conditioned)
            if "elizabeth" in line_name:
                score += 25
       
        # Summer penalty
        if is_summer:
            score -= 15
            reasons.append("summer weather")
       
        # Peak hour body heat
        if JourneyScorer.is_peak_hour(at):
            score -= 10
       
        score = max(0, min(100, score))
       
        if score >= 70:
            level = "Low"
        elif score >= 40:
            level = "Medium"
        else:
            level = "High"
       
        description = f"Temperature likely {level.lower()}"
        if reasons:
            description += f" ({', '.join(set(reasons))})"
       
        return score, level, description
   
    @staticmethod
    def score_reliability(
        journey_data: Dict,
        preferences: Dict,
        disruptions: Dict[str, str]
    ) -> tuple[int, str, str]:
        """Score reliability 0-100 (100 = most reliable)"""
        score = 100
        reasons = []
       
        legs = journey_data.get("legs", [])
        num_changes = sum(1 for leg in legs if leg.get("mode", {}).get("name") != "walking")
       
        # Changes penalty (more points of failure)
        score -= num_changes * 10
       
        # Check for current disruptions
        for leg in legs:
            line_name = leg.get("routeOptions", [{}])[0].get("name", "") if leg.get("routeOptions") else ""
           
            if line_name in disruptions:
                status = disruptions[line_name]
               
                if "Severe Delays" in status or "Part Closure" in status:
                    score -= 50
                    reasons.append(f"{line_name}: {status}")
                elif "Minor Delays" in status:
                    score -= 20
                    reasons.append(f"{line_name}: {status}")
       
        # Bus reliability bonus (frequent, easier alternatives)
        bus_count = sum(1 for leg in legs if "bus" in leg.get("mode", {}).get("name", "").lower())
        if bus_count > 0:
            score += 10
       
        # Direct journey bonus
        if num_changes == 0:
            score += 20
       
        score = max(0, min(100, score))
       
        if score >= 70:
            level = "High"
        elif score >= 40:
            level = "Medium"
        else:
            level = "Low"
       
        description = f"{level} reliability"
        if reasons:
            description += f" ({', '.join(reasons)})"
       
        return score, level, description
   
    @staticmethod
    def calculate_overall_score(
        crowding_score: int,
        noise_score: int,
        heat_score: int,
        reliability_score: int,
        preferences: Dict
    ) -> float:
        """Calculate weighted overall score based on user preferences"""
       
        # Default weights
        w_crowd = 1.0
        w_noise = 1.0
        w_heat = 1.0
        w_reliable = 1.0
       
        # Increase weights for enabled preferences
        if preferences.get("avoid_crowds"):
            w_crowd = 5.0
        if preferences.get("avoid_noise"):
            w_noise = 5.0
        if preferences.get("avoid_heat"):
            w_heat = 50
       
        total_weight = w_crowd + w_noise + w_heat + w_reliable
       
        overall = (
            w_crowd * crowding_score +
            w_noise * noise_score +
            w_heat * heat_score +
            w_reliable * reliability_score
        ) / total_weight
       
        return round(overall, 1)
   
    @staticmethod
    def generate_warnings(
        journey_data: Dict,
        disruptions: Dict[str, str],
        crowding_score: int,
        heat_score: int,
        at: Optional[datetime] = None
    ) -> List[str]:
        """
        Generate user-friendly warnings
       
        Args:
            at: Reference time for peak hour warnings
        """
        warnings = []
       
        legs = journey_data.get("legs", [])
       
        # Check for disruptions
        for leg in legs:
            line_name = leg.get("routeOptions", [{}])[0].get("name", "") if leg.get("routeOptions") else ""
            if line_name in disruptions and disruptions[line_name] != "Good Service":
                warnings.append(f"⚠️ {line_name} line: {disruptions[line_name]}")
       
        # Crowding warning
        if crowding_score < 50 and JourneyScorer.is_peak_hour(at):
            warnings.append("⚠️ Major stations will be busy during peak hours")
       
        # Heat warning
        if heat_score < 50:
            warnings.append("🌡️ Some sections may be warm — consider removing layers")
       
        # Check for major hubs
        major_hubs_in_route = []
        for leg in legs:
            from_name = leg.get("departurePoint", {}).get("commonName", "")
            to_name = leg.get("arrivalPoint", {}).get("commonName", "")
           
            if from_name.lower() in MAJOR_HUBS and from_name not in major_hubs_in_route:
                major_hubs_in_route.append(from_name)
            if to_name.lower() in MAJOR_HUBS and to_name not in major_hubs_in_route:
                major_hubs_in_route.append(to_name)
       
        if len(major_hubs_in_route) > 1:
            warnings.append(f"ℹ️ Route passes through major stations: {', '.join(major_hubs_in_route[:2])}")
       
        return warnings