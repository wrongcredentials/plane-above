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

    aircraft = await AircraftDetails.get_details(async_client, aircraft_icao, "España", photo_search="quick")

    assert aircraft.icao24 == aircraft_icao
    assert aircraft.registration == "A7-BCA"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.model == "737-8 MAX"
    assert aircraft.type_code == "B788"
    assert aircraft.operator == "Qatar Airways"
    assert aircraft.country == "España"
    assert aircraft.age >= 28.5
    assert aircraft.photos[0].image_url == "https://image.airport-data.com/aircraft/001868532.jpg"
    assert aircraft.photos[0].origin_url == "https://airport-data.com/aircraft/photo/001868532"
    assert aircraft.photos[0].photographer == ""


@pytest.mark.asyncio
async def test_all_aircraft_sources_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, aircraft_icao: str):
    httpx_mock.add_response(url=SB_AIRCRAFT_URL, **SB_AIRCRAFT_RESP_404)
    httpx_mock.add_response(url=HX_AIRCRAFT_URL, **HX_AIRCRAFT_RESP_404)
    httpx_mock.add_response(url=FD_AIRCRAFT_URL, **FD_AIRCRAFT_RESP_404)

    aircraft = await AircraftDetails.get_details(async_client, aircraft_icao, "Canada", photo_search="quick")

    assert aircraft == Aircraft(
        icao24=aircraft_icao,
        registration="",
        manufacturer="",
        model="",
        type_code="",
        operator="",
        country="Canada",
        age=0.0,
        photos=[Photo()],
    )


@pytest.mark.asyncio
async def test_all_aircraft_sources_unavailable(
    async_client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
    aircraft_icao: str,
):
    httpx_mock.add_response(url=SB_AIRCRAFT_URL, **SB_AIRCRAFT_RESP_502)
    httpx_mock.add_response(url=HX_AIRCRAFT_URL, **HX_AIRCRAFT_RESP_502)
    httpx_mock.add_response(url=FD_AIRCRAFT_URL, **FD_AIRCRAFT_RESP_502)

    aircraft = await AircraftDetails.get_details(async_client, aircraft_icao, country="", photo_search="quick")

    assert aircraft == Aircraft(
        icao24=aircraft_icao,
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
async def test_sb_aircraft_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, aircraft_icao: str):
    httpx_mock.add_response(url=SB_AIRCRAFT_URL, **SB_AIRCRAFT_RESP_404)
    httpx_mock.add_response(url=HX_AIRCRAFT_URL, **HX_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=FD_AIRCRAFT_URL, **FD_AIRCRAFT_RESP_200)

    aircraft = await AircraftDetails.get_details(async_client, aircraft_icao, "South Africa", photo_search="quick")

    assert aircraft.icao24 == aircraft_icao
    assert aircraft.registration == "A7-BCA"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.model == "747 422"
    assert aircraft.type_code == "B788"
    assert aircraft.operator == "Qatar Airways"
    assert aircraft.country == "South Africa"
    assert aircraft.age >= 28.5
    assert aircraft.photos[0].image_url == "https://image.airport-data.com/aircraft/001868532.jpg"
    assert aircraft.photos[0].origin_url == "https://airport-data.com/aircraft/photo/001868532"
    assert aircraft.photos[0].photographer == ""


@pytest.mark.asyncio
async def test_hx_aircraft_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, aircraft_icao: str):
    httpx_mock.add_response(url=SB_AIRCRAFT_URL, **SB_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=HX_AIRCRAFT_URL, **HX_AIRCRAFT_RESP_404)
    httpx_mock.add_response(url=FD_AIRCRAFT_URL, **FD_AIRCRAFT_RESP_200)

    aircraft = await AircraftDetails.get_details(
        async_client, aircraft_icao, "Korea, Republic of", photo_search="quick"
    )

    assert aircraft.icao24 == aircraft_icao
    assert aircraft.registration == "LV-KEI"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.model == "737-8 MAX"
    assert aircraft.type_code == "B38M"
    assert aircraft.operator == "Dubai Air Wing"
    assert aircraft.country == "Korea, Republic of"
    assert aircraft.age >= 28.5
    assert aircraft.photos[0].image_url == "https://image.airport-data.com/aircraft/001868532.jpg"
    assert aircraft.photos[0].origin_url == "https://airport-data.com/aircraft/photo/001868532"
    assert aircraft.photos[0].photographer == ""


@pytest.mark.asyncio
async def test_fd_aircraft_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, aircraft_icao: str):
    httpx_mock.add_response(url=SB_AIRCRAFT_URL, **SB_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=HX_AIRCRAFT_URL, **HX_AIRCRAFT_RESP_200)
    httpx_mock.add_response(url=FD_AIRCRAFT_URL, **FD_AIRCRAFT_RESP_404)

    aircraft = await AircraftDetails.get_details(
        async_client, aircraft_icao, "Czechia (Czech Republic)", photo_search="quick"
    )

    assert aircraft.icao24 == aircraft_icao
    assert aircraft.registration == "A7-BCA"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.model == "737-8 MAX"
    assert aircraft.type_code == "B788"
    assert aircraft.operator == "Qatar Airways"
    assert aircraft.age == 0.0
    assert aircraft.country == "Czechia (Czech Republic)"
    assert aircraft.photos == [Photo()]
