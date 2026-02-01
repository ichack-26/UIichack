import requests
import os
import logging
from typing import Dict, Optional, List
from datetime import date, time
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TfLClient:
    BASE_URL = "https://api.tfl.gov.uk"
    TIMEOUT = 10

    JOURNEY_PREFERENCES = [
        "LeastTime",
        "LeastInterchange",
    ]

    MAX_JOURNEYS_PER_CALL = 6
    MAX_TOTAL_JOURNEYS = 20

    def __init__(self):
        self.app_id = os.getenv("TFL_APP_ID", "")
        self.app_key = os.getenv("TFL_APP_KEY", "")

    def _auth_params(self) -> Dict[str, str]:
        if self.app_id and self.app_key:
            return {"app_id": self.app_id, "app_key": self.app_key}
        return {}

    def _base_params(
        self,
        journey_preference: str,
        travel_date: Optional[date],
        travel_time: Optional[time],
        arrive_by: bool,
    ) -> Dict[str, str]:
        params = {
            "mode": (
                "bus,cable-car,coach,dlr,elizabeth-line,"
                "national-rail,overground,river-bus,tram,tube,walking"
            ),
            "journeyPreference": journey_preference,
            "maxWalkingMinutes": "7",
            "walkingSpeed": "Slow",
            "timeIs": "Arriving" if arrive_by else "Departing",
        }

        if travel_date:
            params["date"] = travel_date.strftime("%Y%m%d")
        if travel_time:
            params["time"] = travel_time.strftime("%H%M")

        params.update(self._auth_params())
        return params

    def _journey_signature(self, journey: Dict) -> str:
        """
        Used to de-duplicate journeys across preference calls.
        """
        sig = []
        for leg in journey.get("legs", []):
            mode = leg.get("mode", {}).get("name", "")
            line = None
            if leg.get("routeOptions"):
                line = leg["routeOptions"][0].get("name")
            sig.append(f"{mode}:{line}")
        return "|".join(sig)

    def _fetch(
        self,
        from_location: str,
        to_location: str,
        params: Dict[str, str],
    ) -> List[Dict]:
        url = (
            f"{self.BASE_URL}/Journey/JourneyResults/"
            f"{quote(from_location)}/to/{quote(to_location)}"
        )

        try:
            response = requests.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            data = response.json()
            return data.get("journeys", [])[: self.MAX_JOURNEYS_PER_CALL]
        except requests.exceptions.RequestException as e:
            logger.warning(f"TfL call failed ({params.get('journeyPreference')}): {e}")
            return []

    def get_journey_results(
        self,
        from_location: str,
        to_location: str,
        travel_date: Optional[date] = None,
        travel_time: Optional[time] = None,
        arrive_by: bool = False,
    ) -> Optional[Dict]:
        logger.info(f"TfL multi-pass journey search: {from_location} → {to_location}")

        journeys: List[Dict] = []
        seen = set()

        for pref in self.JOURNEY_PREFERENCES:
            params = self._base_params(pref, travel_date, travel_time, arrive_by)
            fetched = self._fetch(from_location, to_location, params)

            for j in fetched:
                sig = self._journey_signature(j)
                if sig not in seen:
                    seen.add(sig)
                    journeys.append(j)

            if len(journeys) >= self.MAX_TOTAL_JOURNEYS:
                break

        if not journeys:
            return None

        return {"journeys": journeys}

    # -----------------------------
    # LINE STATUS (unchanged)
    # -----------------------------
    def get_line_status(self) -> Optional[Dict]:
        url = f"{self.BASE_URL}/Line/Mode/tube,bus/Status"
        try:
            response = requests.get(
                url, params=self._auth_params(), timeout=self.TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Line status API error: {e}")
            return None

    def get_line_disruptions(self) -> Dict[str, str]:
        disruptions = {}
        status_data = self.get_line_status()

        if not status_data:
            return disruptions

        for line in status_data:
            name = line.get("name")
            statuses = line.get("lineStatuses", [])
            if statuses:
                disruptions[name] = statuses[0].get(
                    "statusSeverityDescription", "Good Service"
                )

        return disruptions
