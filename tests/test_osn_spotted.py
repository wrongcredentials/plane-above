import pytest_httpx

from tests import OSNMocks
from tests.data import COORDINATES
from plane_above import PlaneAbove
from plane_above.models import State, FlyingObject


def test_retrieve_ok(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(**OSNMocks.OSN_STATES_RESP_200)
    plane_above = PlaneAbove(COORDINATES)
    assert plane_above.spotted.objects_raw == OSNMocks.OSN_STATES_RESP_200["json"]["states"]
    assert plane_above.spotted.objects_filtered == [
        FlyingObject(
            icao24="8960b4",
            callsign="DUB1",
            country="United Arab Emirates",
            state=State(
                velocity=999,
                altitude=11613,
                latitude=50.5601,
                longitude=5.6853,
            ),
        )
    ]
    assert plane_above.spotted.errors == []
    assert plane_above.spotted.success is True
    assert plane_above.spotted.how_many == 1


def test_retrieve_no_planes(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(**OSNMocks.OSN_STATES_RESP_404)
    plane_above = PlaneAbove(COORDINATES)
    assert plane_above.spotted.objects_raw == []
    assert plane_above.spotted.objects_filtered == []
    assert plane_above.spotted.errors == []
    assert plane_above.spotted.success is True
    assert plane_above.spotted.how_many == 0
    assert list(plane_above.fetch()) == []


def test_retrieve_unavailable(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(**OSNMocks.OSN_STATES_RESP_502)
    plane_above = PlaneAbove(COORDINATES)
    assert plane_above.spotted.objects_raw == []
    assert plane_above.spotted.objects_filtered == []
    assert plane_above.spotted.errors == []
    assert plane_above.spotted.success is False
    assert plane_above.spotted.how_many == 0
    assert list(plane_above.fetch()) == []


def test_retrieve_wrong_content_type(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(content=b"<!doctype html>")
    plane_above = PlaneAbove(COORDINATES)
    assert plane_above.spotted.objects_raw == []
    assert plane_above.spotted.objects_filtered == []
    assert plane_above.spotted.errors == []
    assert plane_above.spotted.success is False
    assert plane_above.spotted.how_many == 0
    assert list(plane_above.fetch()) == []
