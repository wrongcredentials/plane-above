import os

import httpx
import pytest

from tests.data import COORDINATES
from plane_above import PlaneAbove, PhotoSource, RouteSource


@pytest.fixture
def async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


@pytest.fixture
def ps_user_agent() -> str:
    return os.environ["PS_USER_AGENT"]


@pytest.fixture
def plane_above_mock(request, monkeypatch, ps_user_agent) -> PlaneAbove:
    monkeypatch.setattr(
        "plane_above.osn.OSN._retrieve_objects_in_area",
        lambda area, auth_token, proxy: (request.param, True),
    )
    return PlaneAbove(
        COORDINATES,
        route_sources=(RouteSource.HX, RouteSource.SB),
        photo_sources=(PhotoSource.HX, PhotoSource.AD, PhotoSource.PS),
        ps_user_agent=ps_user_agent,
    )
