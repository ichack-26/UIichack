from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# -------------------------------------------------
# LINE / MODE DEFINITIONS
# -------------------------------------------------

DEEP_LEVEL_LINES = {
    "central", "northern", "piccadilly", "bakerloo",
    "victoria", "waterloo & city", "jubilee"
}

HOT_LINES = {"central", "bakerloo", "northern"}
NOISY_LINES = {"central", "northern", "piccadilly", "bakerloo", "victoria"}

MAJOR_HUBS = {
    "kings cross st pancras", "king's cross st. pancras",
    "oxford circus", "victoria", "waterloo", "london bridge",
    "liverpool street", "bank", "leicester square",
    "green park", "paddington"
}

RAIL_MODES = {"tube", "dlr", "overground", "elizabeth", "elizabeth-line", "tram"}
BUS_MODES = {"bus"}


class JourneyScorer:

    # -------------------------------------------------
    # TIME HELPERS
    # -------------------------------------------------

    @staticmethod
    def is_peak_hour(at: Optional[datetime] = None) -> bool:
        now = at if at else datetime.now()
        if now.weekday() >= 5:
            return False
        h, m = now.hour, now.minute
        return (
            (h == 7 and m >= 30)
            or h == 8
            or (h == 9 and m < 30)
            or (17 <= h < 19)
        )

    # -------------------------------------------------
    # CROWDING
    # -------------------------------------------------

    @staticmethod
    def score_crowding(
        journey_data: Dict,
        preferences: Dict,
        disruptions: Dict[str, str],
        at: Optional[datetime] = None
    ) -> tuple[int, str, str]:

        score = 100
        reasons = []

        legs = journey_data.get("legs", [])
        transport_legs = [l for l in legs if l.get("mode", {}).get("name") != "walking"]
        num_changes = max(0, len(transport_legs) - 1)

        if JourneyScorer.is_peak_hour(at):
            score -= 20
            reasons.append("peak travel time")

        hub_count = sum(
            1 for leg in legs for p in ("departurePoint", "arrivalPoint")
            if leg.get(p, {}).get("commonName", "").lower() in MAJOR_HUBS
        )

        if hub_count:
            score -= hub_count * 10
            reasons.append(f"{hub_count} major stations")

        score -= num_changes * 5
        if num_changes > 1:
            reasons.append(f"{num_changes} changes")

        if JourneyScorer.is_peak_hour(at):
            for leg in legs:
                line = (leg.get("routeOptions") or [{}])[0].get("name", "").lower()
                if any(d in line for d in DEEP_LEVEL_LINES):
                    score -= 10

        score = max(0, min(100, score))
        level = "Low" if score >= 70 else "Medium" if score >= 40 else "High"
        desc = f"Expected to be {level.lower()}ly crowded"
        if reasons:
            desc += f" ({', '.join(reasons)})"

        return score, level, desc

    # -------------------------------------------------
    # NOISE
    # -------------------------------------------------

    @staticmethod
    def score_noise(journey_data: Dict, preferences: Dict) -> tuple[int, str, str]:
        score = 100
        reasons = []

        for leg in journey_data.get("legs", []):
            mode = leg.get("mode", {}).get("name", "").lower()
            line = (leg.get("routeOptions") or [{}])[0].get("name", "").lower()

            if mode in BUS_MODES:
                if preferences.get("prefer_buses"):
                    score += 20
                else:
                    score -= 20  # buses penalised by default
                continue

            if any(d in line for d in DEEP_LEVEL_LINES):
                score -= 20
                reasons.append("deep-level tube")

            if any(n in line for n in NOISY_LINES):
                score -= 15
                reasons.append(f"{line.title()} line can be loud")

        score = max(0, min(100, score))
        level = "Low" if score >= 70 else "Medium" if score >= 40 else "High"
        desc = f"{level} noise expected"
        if reasons:
            desc += f" ({', '.join(set(reasons))})"

        return score, level, desc

    # -------------------------------------------------
    # HEAT
    # -------------------------------------------------

    @staticmethod
    def score_heat(
        journey_data: Dict,
        preferences: Dict,
        at: Optional[datetime] = None
    ) -> tuple[int, str, str]:

        score = 100
        reasons = []

        ref = at if at else datetime.now()
        is_summer = ref.month in {6, 7, 8}

        for leg in journey_data.get("legs", []):
            mode = leg.get("mode", {}).get("name", "").lower()
            line = (leg.get("routeOptions") or [{}])[0].get("name", "").lower()

            if mode in BUS_MODES:
                if preferences.get("prefer_buses"):
                    score += 15
                else:
                    score -= 10
                continue

            if any(d in line for d in DEEP_LEVEL_LINES):
                score -= 20

            if any(h in line for h in HOT_LINES):
                score -= 15
                reasons.append(f"{line.title()} line runs warm")

            if "elizabeth" in line:
                score += 20

        if is_summer:
            score -= 10
            reasons.append("summer weather")

        if JourneyScorer.is_peak_hour(at):
            score -= 5

        score = max(0, min(100, score))
        level = "Low" if score >= 70 else "Medium" if score >= 40 else "High"
        desc = f"Temperature likely {level.lower()}"
        if reasons:
            desc += f" ({', '.join(set(reasons))})"

        return score, level, desc

    # -------------------------------------------------
    # RELIABILITY
    # -------------------------------------------------

    @staticmethod
    def score_reliability(
        journey_data: Dict,
        preferences: Dict,
        disruptions: Dict[str, str]
    ) -> tuple[int, str, str]:

        score = 100
        reasons = []

        legs = journey_data.get("legs", [])
        transport_legs = [l for l in legs if l.get("mode", {}).get("name") != "walking"]
        num_changes = max(0, len(transport_legs) - 1)

        score -= num_changes * 10

        for leg in legs:
            line = (leg.get("routeOptions") or [{}])[0].get("name", "")
            if line in disruptions:
                status = disruptions[line]
                if "Severe" in status or "Closure" in status:
                    score -= 50
                    reasons.append(f"{line}: {status}")
                elif "Minor" in status:
                    score -= 20
                    reasons.append(f"{line}: {status}")

        bus_legs = sum(1 for l in legs if l.get("mode", {}).get("name", "").lower() in BUS_MODES)
        rail_legs = sum(1 for l in legs if l.get("mode", {}).get("name", "").lower() in RAIL_MODES)

        if preferences.get("prefer_buses"):
            score += bus_legs * 20
            score -= rail_legs * 5
        else:
            score += rail_legs * 15
            score -= bus_legs * 20

        if num_changes == 0:
            score += 15

        score = max(0, min(100, score))
        level = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
        desc = f"{level} reliability"
        if reasons:
            desc += f" ({', '.join(reasons)})"

        return score, level, desc

    # -------------------------------------------------
    # OVERALL SCORE (FINAL AUTHORITY)
    # -------------------------------------------------

    @staticmethod
    def calculate_overall_score(
        crowding_score: int,
        noise_score: int,
        heat_score: int,
        reliability_score: int,
        preferences: Dict,
        journey_data: Dict
    ) -> float:

        w_crowd = 50 if preferences.get("avoid_crowds") else 1.0
        w_noise = 50 if preferences.get("avoid_noise") else 1.0
        w_heat = 50 if preferences.get("avoid_heat") else 1.0
        w_rel = 10

        total = w_crowd + w_noise + w_heat + w_rel

        overall = (
            w_crowd * crowding_score +
            w_noise * noise_score +
            w_heat * heat_score +
            w_rel * reliability_score
        ) / total

        legs = journey_data.get("legs", [])
        rail_legs = sum(1 for l in legs if l.get("mode", {}).get("name", "").lower() in RAIL_MODES)
        bus_legs = sum(1 for l in legs if l.get("mode", {}).get("name", "").lower() in BUS_MODES)

        if preferences.get("prefer_buses"):
            overall += bus_legs * 25
            overall -= rail_legs * 10
        else:
            overall += rail_legs * 20
            overall -= bus_legs * 25

        overall = max(0, min(100, overall))
        return round(overall, 1)

    # -------------------------------------------------
    # WARNINGS
    # -------------------------------------------------

    @staticmethod
    def generate_warnings(
        journey_data: Dict,
        disruptions: Dict[str, str],
        crowding_score: int,
        heat_score: int,
        at: Optional[datetime] = None
    ) -> List[str]:

        warnings = []

        for leg in journey_data.get("legs", []):
            line = (leg.get("routeOptions") or [{}])[0].get("name", "")
            if line in disruptions and disruptions[line] != "Good Service":
                warnings.append(f"⚠️ {line}: {disruptions[line]}")

        if crowding_score < 50 and JourneyScorer.is_peak_hour(at):
            warnings.append("⚠️ Major stations will be busy during peak hours")

        if heat_score < 50:
            warnings.append("🌡️ Some sections may be warm")

        hubs = set()
        for leg in journey_data.get("legs", []):
            for p in ("departurePoint", "arrivalPoint"):
                name = leg.get(p, {}).get("commonName", "")
                if name.lower() in MAJOR_HUBS:
                    hubs.add(name)

        if len(hubs) > 1:
            warnings.append(
                f"ℹ️ Route passes through major stations: {', '.join(list(hubs)[:2])}"
            )

        return warnings
