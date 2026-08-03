import json
import math
from datetime import datetime, timedelta
from dataclasses import dataclass

import httpx
import country_converter

from .utils import log
from .static import EARTH_RADIUS, OPENSKY_AUTH_URL, AIRCRAFT_IN_AREA_SOURCE_URL, DEFAULT_DISTANCE_FROM_POINT


@dataclass(frozen=True)
class FlyingObject:
    icao24: str
    callsign: str
    country_code: str
    velocity: int
    altitude: int


class OSNAuth:
    def __init__(self, client_id: str, client_secret: str, proxy: str | None = None):
        self.proxy = proxy
        self.client_id = client_id
        self.client_secret = client_secret
        self.token: str | None = None
        self.expires_at: datetime | None = None

    def get_token(self) -> str | None:
        if self.token and self.expires_at and datetime.now() < self.expires_at:
            return self.token
        return self._refresh()

    def _refresh(self) -> str | None:
        try:
            r = httpx.post(
                OPENSKY_AUTH_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                proxy=self.proxy,
            )
            r.raise_for_status()
            data = r.json()
            self.token = data.get("access_token")
            self.expires_at = datetime.now() + timedelta(seconds=data.get("expires_in", 1800) - 30)
            return self.token

        except (httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
            log.error(f" ✈ OSN authorization request timeout: {exc}")
            return None

        except (httpx.HTTPError, json.JSONDecodeError) as exc:
            log.error(f" ✈ Exception occurred with OSN authorization: {exc}")
            return None


class OSN:
    @staticmethod
    def _validate_coordinates(latitude: float, longitude: float) -> tuple[float, float]:
        if -90 <= latitude <= 90 and -180 <= longitude <= 180:
            return latitude, longitude

        log.error(
            " ✈ Coordinates should be passed in degrees with possible values [-90, 90]"
            " for latitude and [-180, 180] for longitude."
        )
        raise ValueError("Invalid coordinates.")

    @staticmethod
    def _get_bounding_box(latitude: float, longitude: float, distance: int | float) -> dict[str, float]:
        if isinstance(distance, (int, float)) is False or distance < 1:
            distance = DEFAULT_DISTANCE_FROM_POINT
            log.warning(f" ✈ Invalid distance value, will proceed with {DEFAULT_DISTANCE_FROM_POINT} as default.")

        latitude_rad = math.radians(latitude)
        longitude_rad = math.radians(longitude)

        angular_distance = distance / EARTH_RADIUS
        delta_longitude = math.asin(math.sin(angular_distance) / math.cos(latitude_rad))

        return dict(
            lamin=math.degrees(latitude_rad - angular_distance),
            lomin=math.degrees(longitude_rad - delta_longitude),
            lamax=math.degrees(latitude_rad + angular_distance),
            lomax=math.degrees(longitude_rad + delta_longitude),
        )

    @staticmethod
    def _retrieve_objects_in_area(
        area: dict,
        auth_token: str | None = "",
        proxy: str | None = "",
    ) -> tuple[list, bool]:
        try:
            r = httpx.get(
                AIRCRAFT_IN_AREA_SOURCE_URL,
                headers={"Authorization": f"Bearer {auth_token}"} if auth_token else {},
                params=dict(**area, extended=1),
                timeout=10.0,
                proxy=proxy,
            )
            r.raise_for_status()
            data = r.json()
            return data.get("states") or [], True

        except (httpx.HTTPError, json.JSONDecodeError) as exc:
            log.error(f" ✈ Exception occurred with OSN request: {exc}")
            return [], False

    @staticmethod
    def _filter_objects(objects: list) -> tuple[list, int]:
        cc = country_converter.CountryConverter()
        filtered = [
            FlyingObject(
                icao24=state[0],
                callsign=state[1].strip(),
                country_code=cc.convert(names=state[2], to="ISO2", not_found="UN"),
                velocity=round((state[9] or 0) * 3.6),
                altitude=round(state[13] or 0),
            )
            for state in objects
            if state[2] and state[8] is False
            # 2: missing country usually means that other data are also missing
            # 8: objects on ground (service vehicles or landed aircraft) do not matter
        ]
        return filtered, len(filtered)

    @classmethod
    def get_flying_objects(
        cls,
        point: tuple[float, float],
        distance: int | float,
        osn_id: str,
        osn_secret: str,
        osn_proxy: str | None = None,
    ) -> tuple[list, list, bool, int]:

        area = cls._get_bounding_box(*cls._validate_coordinates(*point), distance)
        auth = OSNAuth(osn_id, osn_secret, osn_proxy).get_token() if all((osn_id, osn_secret)) else ""
        objects_raw, success = cls._retrieve_objects_in_area(area, auth_token=auth, proxy=osn_proxy)
        objects_filtered, how_many = cls._filter_objects(objects_raw)
        return objects_raw, objects_filtered, success, how_many
