import warnings
from typing import NamedTuple
from dataclasses import dataclass

import country_converter


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
    objects_raw: list
    objects_filtered: list[FlyingObject]
    success: bool
    how_many: int
    errors: list


class Above(NamedTuple):
    aircraft: Aircraft
    flight: Flight
    state: State

    @property
    def route(self) -> Flight:  # pragma: no cover
        warnings.warn("'route' will be removed in v1.0.0, use 'flight'", DeprecationWarning, stacklevel=2)
        return self.flight

    @property
    def country_code(self) -> str:  # pragma: no cover
        warnings.warn(
            "'country_code' will be removed in v1.0.0, use 'aircraft.country'", DeprecationWarning, stacklevel=2
        )
        cc = country_converter.CountryConverter()
        return cc.convert(names=self.aircraft.country, to="ISO2", not_found="UN")  # type: ignore[no-any-return]

    @property
    def icao24(self) -> str:  # pragma: no cover
        warnings.warn("'icao24' will be removed in v1.0.0, use 'aircraft.icao24'", DeprecationWarning, stacklevel=2)
        return self.aircraft.icao24

    @property
    def photo(self) -> Photo:  # pragma: no cover
        warnings.warn("'photo' will be removed in v1.0.0, use 'aircraft.photos'", DeprecationWarning, stacklevel=2)
        return self.aircraft.photos[0]

    @property
    def callsign(self) -> str:  # pragma: no cover
        warnings.warn("'callsign' will be removed in v1.0.0, use 'flight.callsign'", DeprecationWarning, stacklevel=2)
        return self.flight.callsign
