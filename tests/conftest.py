import os

import httpx2
import pytest

from tests.data import COORDINATES
from plane_above import Config, PlaneAbove, PhotoSource, RouteSource


@pytest.fixture
def async_client() -> httpx2.AsyncClient:
    return httpx2.AsyncClient()


@pytest.fixture
def plane_above_mock(request, monkeypatch) -> PlaneAbove:
    monkeypatch.setattr(
        "plane_above.osn.OSN._retrieve_objects_in_area",
        lambda client, area, auth_token: (request.param, True),
    )
    return PlaneAbove(
        COORDINATES,
        config=Config(
            route_sources=(RouteSource.HX,),
            photo_sources=(PhotoSource.HX,),
            user_agent=os.environ["USER_AGENT"],
        ),
    )
