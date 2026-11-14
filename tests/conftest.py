import os

import httpx
import pytest

from tests.data import COORDINATES
from plane_above import PlaneAbove, PhotoSource, RouteSource


@pytest.fixture
def async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


@pytest.fixture
def plane_above_mock(request, monkeypatch) -> PlaneAbove:
    monkeypatch.setattr(
        "plane_above.osn.OSN._retrieve_objects_in_area",
        lambda client, area, auth_token: (request.param, True),
    )
    return PlaneAbove(
        COORDINATES,
        route_sources=(RouteSource.HX,),
        photo_sources=(PhotoSource.HX,),
        ps_user_agent=os.environ["USER_AGENT"],
    )
