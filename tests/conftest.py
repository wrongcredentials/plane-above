import httpx
import pytest

from tests import AIRCRAFT_REG, AIRCRAFT_ICAO, FLIGHT_CALLSIGN
from plane_above import PlaneAbove


@pytest.fixture
def coordinates() -> tuple[float, float]:
    return 52.093454, 5.118284


@pytest.fixture
def aircraft_icao() -> str:
    return AIRCRAFT_ICAO


@pytest.fixture
def aircraft_registration() -> str:
    return AIRCRAFT_REG


@pytest.fixture
def flight_callsign() -> str:
    return FLIGHT_CALLSIGN


@pytest.fixture
def async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


@pytest.fixture
def plane_above_mock(request, monkeypatch, coordinates) -> PlaneAbove:
    monkeypatch.setattr(
        "plane_above.osn.OSN._retrieve_objects_in_area",
        lambda area, auth_token, proxy: (request.param, True),
    )
    return PlaneAbove(coordinates, ps_user_agent="PA-PS/0.1 (+https://t.me/pa-ps)")
