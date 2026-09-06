import httpx
import pytest
from pytest_httpx import HTTPXMock

from tests import AircraftMocks
from tests.data import AIRCRAFT_ICAO, AIRCRAFT_COUNTRY
from plane_above.aircraft import Photo, Aircraft, AircraftDetails


@pytest.mark.asyncio
async def test_all_aircraft_sources_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=AircraftMocks.SB_AIRCRAFT_URL, **AircraftMocks.SB_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=AircraftMocks.HX_AIRCRAFT_URL, **AircraftMocks.HX_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=AircraftMocks.FD_AIRCRAFT_URL, **AircraftMocks.FD_AIRCRAFT_RESP_200)

    aircraft = await AircraftDetails.get_details(async_client, AIRCRAFT_ICAO, AIRCRAFT_COUNTRY, sources=())

    assert aircraft.icao24 == AIRCRAFT_ICAO
    assert aircraft.registration == "A7-BCA"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.model == "737-8 MAX"
    assert aircraft.type_code == "B788"
    assert aircraft.operator == "Qatar Airways"
    assert aircraft.country == AIRCRAFT_COUNTRY
    assert aircraft.age >= 28.5
    assert aircraft.photos[0].image_url == "https://image.airport-data.com/aircraft/001868532.jpg"
    assert aircraft.photos[0].origin_url == "https://airport-data.com/aircraft/photo/001868532"
    assert aircraft.photos[0].photographer == ""


@pytest.mark.asyncio
async def test_all_aircraft_sources_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=AircraftMocks.SB_AIRCRAFT_URL, **AircraftMocks.SB_AIRCRAFT_RESP_404)
    httpx_mock.add_response(url=AircraftMocks.HX_AIRCRAFT_URL, **AircraftMocks.HX_AIRCRAFT_RESP_404)
    httpx_mock.add_response(url=AircraftMocks.FD_AIRCRAFT_URL, **AircraftMocks.FD_AIRCRAFT_RESP_404)

    aircraft = await AircraftDetails.get_details(async_client, AIRCRAFT_ICAO, AIRCRAFT_COUNTRY, sources=())

    assert aircraft == Aircraft(
        icao24=AIRCRAFT_ICAO,
        registration="",
        manufacturer="",
        model="",
        type_code="",
        operator="",
        country=AIRCRAFT_COUNTRY,
        age=0.0,
        photos=[Photo()],
    )


@pytest.mark.asyncio
async def test_all_aircraft_sources_unavailable(
    async_client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
):
    httpx_mock.add_response(url=AircraftMocks.SB_AIRCRAFT_URL, **AircraftMocks.SB_AIRCRAFT_RESP_502)
    httpx_mock.add_response(url=AircraftMocks.HX_AIRCRAFT_URL, **AircraftMocks.HX_AIRCRAFT_RESP_502)
    httpx_mock.add_response(url=AircraftMocks.FD_AIRCRAFT_URL, **AircraftMocks.FD_AIRCRAFT_RESP_502)

    aircraft = await AircraftDetails.get_details(async_client, AIRCRAFT_ICAO, country="", sources=())

    assert aircraft == Aircraft(
        icao24=AIRCRAFT_ICAO,
        registration="",
        manufacturer="",
        model="",
        type_code="",
        operator="",
        country="",
        age=0.0,
        photos=[Photo()],
    )


@pytest.mark.asyncio
async def test_sb_aircraft_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=AircraftMocks.SB_AIRCRAFT_URL, **AircraftMocks.SB_AIRCRAFT_RESP_404)
    httpx_mock.add_response(url=AircraftMocks.HX_AIRCRAFT_URL, **AircraftMocks.HX_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=AircraftMocks.FD_AIRCRAFT_URL, **AircraftMocks.FD_AIRCRAFT_RESP_200)

    aircraft = await AircraftDetails.get_details(async_client, AIRCRAFT_ICAO, AIRCRAFT_COUNTRY, sources=())

    assert aircraft.icao24 == AIRCRAFT_ICAO
    assert aircraft.registration == "A7-BCA"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.model == "747 422"
    assert aircraft.type_code == "B788"
    assert aircraft.operator == "Qatar Airways"
    assert aircraft.country == AIRCRAFT_COUNTRY
    assert aircraft.age >= 28.5
    assert aircraft.photos[0].image_url == "https://image.airport-data.com/aircraft/001868532.jpg"
    assert aircraft.photos[0].origin_url == "https://airport-data.com/aircraft/photo/001868532"
    assert aircraft.photos[0].photographer == ""


@pytest.mark.asyncio
async def test_hx_aircraft_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=AircraftMocks.SB_AIRCRAFT_URL, **AircraftMocks.SB_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=AircraftMocks.HX_AIRCRAFT_URL, **AircraftMocks.HX_AIRCRAFT_RESP_404)
    httpx_mock.add_response(url=AircraftMocks.FD_AIRCRAFT_URL, **AircraftMocks.FD_AIRCRAFT_RESP_200)

    aircraft = await AircraftDetails.get_details(async_client, AIRCRAFT_ICAO, AIRCRAFT_COUNTRY, sources=())

    assert aircraft.icao24 == AIRCRAFT_ICAO
    assert aircraft.registration == "LV-KEI"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.model == "737-8 MAX"
    assert aircraft.type_code == "B38M"
    assert aircraft.operator == "Dubai Air Wing"
    assert aircraft.country == AIRCRAFT_COUNTRY
    assert aircraft.age >= 28.5
    assert aircraft.photos[0].image_url == "https://image.airport-data.com/aircraft/001868532.jpg"
    assert aircraft.photos[0].origin_url == "https://airport-data.com/aircraft/photo/001868532"
    assert aircraft.photos[0].photographer == ""


@pytest.mark.asyncio
@pytest.mark.parametrize("_fd_resp", [AircraftMocks.FD_AIRCRAFT_RESP_404, AircraftMocks.FD_AIRCRAFT_BAD_RESP_200])
async def test_fd_aircraft_source_empty(_fd_resp, async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=AircraftMocks.SB_AIRCRAFT_URL, **AircraftMocks.SB_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=AircraftMocks.HX_AIRCRAFT_URL, **AircraftMocks.HX_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=AircraftMocks.FD_AIRCRAFT_URL, **_fd_resp)

    aircraft = await AircraftDetails.get_details(async_client, AIRCRAFT_ICAO, AIRCRAFT_COUNTRY, sources=())

    assert aircraft.icao24 == AIRCRAFT_ICAO
    assert aircraft.registration == "A7-BCA"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.model == "737-8 MAX"
    assert aircraft.type_code == "B788"
    assert aircraft.operator == "Qatar Airways"
    assert aircraft.age == 0.0
    assert aircraft.country == AIRCRAFT_COUNTRY
    assert aircraft.photos == [Photo()]
