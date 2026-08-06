import warnings
from typing import NamedTuple
from dataclasses import dataclass


@dataclass(frozen=True)
class FlyingObject:
    icao24: str
    callsign: str
    country_code: str
    velocity: int
    altitude: int


@dataclass(frozen=True)
class Aircraft:
    registration: str
    manufacturer: str
    model: str
    operator: str
    age: float


@dataclass(frozen=True)
class Photo:
    image_url: str
    origin_url: str
    photographer: str


@dataclass(frozen=True)
class Airport:
    iata: str = "N/A"
    name: str = "Unknown airport"
    country_code: str = ""


@dataclass(frozen=True)
class Flight:
    departure: Airport
    destination: Airport
    stops: list[Airport]
    airline: str | None = None


@dataclass(frozen=True)
class State:
    altitude: int
    velocity: int


class Plane(NamedTuple):
    icao24: str
    callsign: str
    country_code: str
    aircraft: Aircraft
    flight: Flight
    state: State
    photo: Photo

    @property
    def route(self) -> Flight:
        warnings.warn(
            "'route' is deprecated since 0.2.0 and will be removed in v1.0.0, use 'flight' instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.flight


class Spotted(NamedTuple):
    objects_raw: list
    objects_filtered: list[FlyingObject]
    success: bool
    how_many: int
    errors: list
