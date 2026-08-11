from plane_above.osn import OSN
from plane_above.models import State, FlyingObject

from .data.osn.flying_objects import (
    UNKNOWN,
    ON_GROUND,
    NO_COUNTRY,
    NO_CALLSIGN,
    ZERO_ALTITUDE,
    ZERO_VELOCITY,
    MISSPELLED_COUNTRY,
)


def test_on_ground():
    filtered, quantity = OSN._filter_objects(ON_GROUND)
    assert quantity == 0
    assert filtered == []


def test_unknown():
    filtered, quantity = OSN._filter_objects(UNKNOWN)
    assert quantity == 0
    assert filtered == []


def test_no_country():
    filtered, quantity = OSN._filter_objects(NO_COUNTRY)
    assert quantity == 0
    assert filtered == []


def test_no_callsign():
    filtered, quantity = OSN._filter_objects(NO_CALLSIGN)
    assert quantity == 1
    assert filtered == [
        FlyingObject(
            icao24="44e697",
            callsign="",
            country="Belgium",
            state=State(velocity=4, altitude=82, latitude=51.0031, longitude=5.063),
        )
    ]


def test_zero_altitude():
    filtered, quantity = OSN._filter_objects(ZERO_ALTITUDE)
    assert quantity == 1
    assert filtered == [
        FlyingObject(
            icao24="505cbb",
            callsign="OMS575",
            country="Slovakia",
            state=State(velocity=156, altitude=0, latitude=50.4194, longitude=6.2806),
        )
    ]


def test_zero_velocity():
    filtered, quantity = OSN._filter_objects(ZERO_VELOCITY)
    assert quantity == 1
    assert filtered == [
        FlyingObject(
            icao24="39e680",
            callsign="AFR94XK",
            country="France",
            state=State(velocity=0, altitude=11567, latitude=52.5609, longitude=5.7613),
        )
    ]


def test_country_code_convert():
    filtered, quantity = OSN._filter_objects(MISSPELLED_COUNTRY)
    assert quantity == 1
    assert filtered == [
        FlyingObject(
            icao24="76cec5",
            callsign="SIA318",
            country="S1ngap0re",
            state=State(velocity=897, altitude=11232, latitude=51.5289, longitude=5.4091),
        )
    ]
