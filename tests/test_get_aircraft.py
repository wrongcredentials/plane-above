import httpx
import pytest
from pytest_httpx import HTTPXMock

from plane_above.aircraft import Photo, Aircraft, AircraftDetails

from . import (
    FD_AIRCRAFT_URL,
    HX_AIRCRAFT_URL,
    SB_AIRCRAFT_URL,
    FD_AIRCRAFT_RESP_200,
    FD_AIRCRAFT_RESP_404,
    FD_AIRCRAFT_RESP_502,
    HX_AIRCRAFT_RESP_200,
    HX_AIRCRAFT_RESP_404,
    HX_AIRCRAFT_RESP_502,
    SB_AIRCRAFT_RESP_200,
    SB_AIRCRAFT_RESP_404,
    SB_AIRCRAFT_RESP_502,
)


@pytest.mark.asyncio
async def test_all_aircraft_sources_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, aircraft_icao):
    httpx_mock.add_response(url=SB_AIRCRAFT_URL, **SB_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=HX_AIRCRAFT_URL, **HX_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=FD_AIRCRAFT_URL, **FD_AIRCRAFT_RESP_200)

    aircraft, photo = await AircraftDetails.get_details(async_client, aircraft_icao)

    assert aircraft.registration == "A7-BCA"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.model == "737-8 MAX"
    assert aircraft.operator == "Qatar Airways"
    assert aircraft.age >= 28.5
    assert photo.image_url == "https://image.airport-data.com/aircraft/001868532.jpg"
    assert photo.origin_url == "https://airport-data.com/aircraft/photo/001868532"
    assert photo.photographer == ""


@pytest.mark.asyncio
async def test_all_aircraft_sources_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, aircraft_icao: str):
    httpx_mock.add_response(url=SB_AIRCRAFT_URL, **SB_AIRCRAFT_RESP_404)
    httpx_mock.add_response(url=HX_AIRCRAFT_URL, **HX_AIRCRAFT_RESP_404)
    httpx_mock.add_response(url=FD_AIRCRAFT_URL, **FD_AIRCRAFT_RESP_404)

    aircraft, photo = await AircraftDetails.get_details(async_client, aircraft_icao)

    assert aircraft == Aircraft(registration="", manufacturer="", model="", operator="", age=0.0)
    assert photo.image_url == "https://image.airport-data.com/aircraft/nophoto.png"
    assert photo.origin_url == ""
    assert photo.photographer == ""


@pytest.mark.asyncio
async def test_all_aircraft_sources_unavailable(
    async_client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
    aircraft_icao: str,
):
    httpx_mock.add_response(url=SB_AIRCRAFT_URL, **SB_AIRCRAFT_RESP_502)
    httpx_mock.add_response(url=HX_AIRCRAFT_URL, **HX_AIRCRAFT_RESP_502)
    httpx_mock.add_response(url=FD_AIRCRAFT_URL, **FD_AIRCRAFT_RESP_502)

    aircraft, photo = await AircraftDetails.get_details(async_client, aircraft_icao)

    assert aircraft == Aircraft(registration="", manufacturer="", model="", operator="", age=0.0)
    assert photo == Photo(image_url="", origin_url="", photographer="")


@pytest.mark.asyncio
async def test_sb_aircraft_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, aircraft_icao: str):
    httpx_mock.add_response(url=SB_AIRCRAFT_URL, **SB_AIRCRAFT_RESP_404)
    httpx_mock.add_response(url=HX_AIRCRAFT_URL, **HX_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=FD_AIRCRAFT_URL, **FD_AIRCRAFT_RESP_200)

    aircraft, photo = await AircraftDetails.get_details(async_client, aircraft_icao)

    assert aircraft.registration == "A7-BCA"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.model == "747 422"
    assert aircraft.operator == "Qatar Airways"
    assert aircraft.age >= 28.5
    assert photo.image_url == "https://image.airport-data.com/aircraft/001868532.jpg"
    assert photo.origin_url == "https://airport-data.com/aircraft/photo/001868532"
    assert photo.photographer == ""


@pytest.mark.asyncio
async def test_hx_aircraft_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, aircraft_icao: str):
    httpx_mock.add_response(url=SB_AIRCRAFT_URL, **SB_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=HX_AIRCRAFT_URL, **HX_AIRCRAFT_RESP_404)
    httpx_mock.add_response(url=FD_AIRCRAFT_URL, **FD_AIRCRAFT_RESP_200)

    aircraft, photo = await AircraftDetails.get_details(async_client, aircraft_icao)

    assert aircraft.registration == "LV-KEI"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.model == "737-8 MAX"
    assert aircraft.operator == "Dubai Air Wing"
    assert aircraft.age >= 28.5
    assert photo.image_url == "https://image.airport-data.com/aircraft/001868532.jpg"
    assert photo.origin_url == "https://airport-data.com/aircraft/photo/001868532"
    assert photo.photographer == ""


@pytest.mark.asyncio
async def test_fd_aircraft_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, aircraft_icao: str):
    httpx_mock.add_response(url=SB_AIRCRAFT_URL, **SB_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=HX_AIRCRAFT_URL, **HX_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=FD_AIRCRAFT_URL, **FD_AIRCRAFT_RESP_404)

    aircraft, photo = await AircraftDetails.get_details(async_client, aircraft_icao)

    assert aircraft.registration == "A7-BCA"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.model == "737-8 MAX"
    assert aircraft.operator == "Qatar Airways"
    assert aircraft.age == 0.0
    assert photo.image_url == "https://image.airport-data.com/aircraft/nophoto.png"
    assert photo.origin_url == ""
    assert photo.photographer == ""
