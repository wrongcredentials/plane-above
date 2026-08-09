import warnings
from typing import Any

from .models import Above, Photo, State, Flight, Airport, Aircraft
from ._plane_above import PlaneAbove


def __getattr__(name: str) -> Any:
    if name == "Plane":
        warnings.warn("'Plane' will be removed in v1.0.0, use 'Above'", DeprecationWarning, stacklevel=2)
        return Above
    if name == "Route":
        warnings.warn("'Route' will be removed in v1.0.0, use 'Flight'", DeprecationWarning, stacklevel=2)
        return Flight
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["Above", "Aircraft", "Airport", "Flight", "Photo", "PlaneAbove", "State"]
__version__ = "0.2.0-rc"
