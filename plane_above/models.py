import json
from typing import Any, NamedTuple
from dataclasses import asdict, dataclass

from .static import OSNStateVectorType


@dataclass(frozen=True)
class Photo:
    image_url: str = ""
    origin_url: str = ""
    photographer: str = ""

    @property
    def _has_urls(self) -> bool:
        return bool(self.image_url and self.origin_url)


@dataclass(frozen=True)
class Aircraft:
    icao24: str
    country: str
    age: float
    photos: list[Photo]
    registration: str = ""
    manufacturer: str = ""
    model: str = ""
    type_code: str = ""
    operator: str = ""


@dataclass(frozen=True)
class Airport:
    iata: str = "N/A"
    name: str = "Unknown airport"
    country_code: str = "UN"


@dataclass(frozen=True)
class Flight:
    callsign: str
    departure: Airport
    destination: Airport
    stops: list[Airport]
    airline: str = ""


@dataclass(frozen=True)
class State:
    altitude: int
    velocity: int
    latitude: float | None = None
    longitude: float | None = None


@dataclass(frozen=True, slots=True)
class FlyingObject:
    icao24: str
    callsign: str
    country: str
    state: State


class Spotted(NamedTuple):
    objects_raw: list[OSNStateVectorType]
    objects_filtered: list[FlyingObject]
    success: bool
    how_many: int
    errors: list[tuple[str, str]]


class Above(NamedTuple):
    aircraft: Aircraft
    flight: Flight
    state: State

    def to_dict(self) -> dict[str, Any]:
        return {
            "aircraft": asdict(self.aircraft),
            "flight": asdict(self.flight),
            "state": asdict(self.state),
        }

    def to_json(self, **kwargs: Any) -> str:
        kwargs.setdefault("ensure_ascii", False)
        return json.dumps(self.to_dict(), **kwargs)
