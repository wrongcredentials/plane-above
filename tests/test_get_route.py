import httpx
import pytest
from pytest_httpx import HTTPXMock

from plane_above.flight import Flight, Airport, FlightRoute

from . import (
    HX_ROUTE_URL,
    SB_ROUTE_URL,
    HX_ROUTE_RESP_200,
    HX_ROUTE_RESP_404,
    HX_ROUTE_RESP_502,
    SB_ROUTE_RESP_200,
    SB_ROUTE_RESP_404,
    SB_ROUTE_RESP_502,
    AD_DEP_AIRPORT_URL,
    AD_DST_AIRPORT_URL,
    AD_MID_AIRPORT_URL,
    HX_DEP_AIRPORT_URL,
    HX_DST_AIRPORT_URL,
    HX_MID_AIRPORT_URL,
    AD_AIRPORT_RESP_200,
    AD_AIRPORT_RESP_404,
    AD_AIRPORT_RESP_502,
    HX_AIRPORT_RESP_200,
    HX_AIRPORT_RESP_404,
    HX_AIRPORT_RESP_502,
    HX_ROUTE_MP_RESP_200,
    SB_ROUTE_MP_RESP_200,
)

ROUTE_EMPTY = Flight(
    departure=Airport(iata="N/A", name="Unknown departure", country_code=""),
    destination=Airport(iata="N/A", name="Unknown destination", country_code=""),
    stops=[],
)
ROUTE_AIRPORT_UNKNOWN = Flight(
    departure=Airport(iata="DEP", name="Unknown airport", country_code=""),
    destination=Airport(iata="DST", name="Unknown airport", country_code=""),
    stops=[],
)
ROUTE_HX = Flight(
    departure=Airport(
        iata="DEP",
        name="Valencia Airport",
        country_code="ES",
    ),
    destination=Airport(
        iata="DST",
        name="Valencia Airport",
        country_code="ES",
    ),
    stops=[],
    airline=None,
)
ROUTE_HX_WITH_STOP = Flight(
    departure=Airport(
        iata="DEP",
        name="Valencia Airport",
        country_code="ES",
    ),
    destination=Airport(
        iata="DST",
        name="Valencia Airport",
        country_code="ES",
    ),
    stops=[
        Airport(
            iata="MID",
            name="Jeju International Airport",
            country_code="KR",
        ),
    ],
    airline=None,
)
ROUTE_HX_AD = Flight(
    departure=Airport(
        iata="DEP",
        name="Jeju International Airport",
        country_code="KR",
    ),
    destination=Airport(
        iata="DST",
        name="Jeju International Airport",
        country_code="KR",
    ),
    stops=[],
    airline=None,
)
ROUTE_SB = Flight(
    departure=Airport(
        iata="CRK",
        name="Diosdado Macapagal International Airport",
        country_code="PH",
    ),
    destination=Airport(
        iata="PUS",
        name="Gimhae International Airport",
        country_code="KR",
    ),
    stops=[],
    airline="Jin Air",
)
ROUTE_SB_WITH_STOP = Flight(
    departure=Airport(
        iata="SGN",
        name="Tan Son Nhat International Airport",
        country_code="VN",
    ),
    destination=Airport(
        iata="EWR",
        name="Newark Liberty International Airport",
        country_code="US",
    ),
    stops=[
        Airport(
            iata="HKG",
            name="Hong Kong International Airport",
            country_code="HK",
        )
    ],
    airline="United Airlines",
)


@pytest.mark.asyncio
@pytest.mark.parametrize("_callsign", ["", None])
async def test_route_without_callsign(_callsign: str | None, async_client: httpx.AsyncClient):
    route = await FlightRoute.get_route(async_client, _callsign)
    assert route == ROUTE_EMPTY


@pytest.mark.asyncio
async def test_hx_route_source_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, flight_callsign: str):
    httpx_mock.add_response(url=HX_ROUTE_URL, **HX_ROUTE_RESP_200)
    httpx_mock.add_response(url=HX_DEP_AIRPORT_URL, **HX_AIRPORT_RESP_200)
    httpx_mock.add_response(url=HX_DST_AIRPORT_URL, **HX_AIRPORT_RESP_200)

    route = await FlightRoute._get_route_from_hx(async_client, flight_callsign)
    assert route == ROUTE_HX


@pytest.mark.asyncio
async def test_hx_ad_route_source_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, flight_callsign: str):
    httpx_mock.add_response(url=HX_ROUTE_URL, **HX_ROUTE_RESP_200)
    httpx_mock.add_response(url=HX_DEP_AIRPORT_URL, **HX_AIRPORT_RESP_404)
    httpx_mock.add_response(url=HX_DST_AIRPORT_URL, **HX_AIRPORT_RESP_502)
    httpx_mock.add_response(url=AD_DEP_AIRPORT_URL, **AD_AIRPORT_RESP_200)
    httpx_mock.add_response(url=AD_DST_AIRPORT_URL, **AD_AIRPORT_RESP_200)

    route = await FlightRoute._get_route_from_hx(async_client, flight_callsign)
    assert route == ROUTE_HX_AD


@pytest.mark.asyncio
async def test_sb_route_source_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, flight_callsign: str):
    httpx_mock.add_response(url=SB_ROUTE_URL, **SB_ROUTE_RESP_200)

    route = await FlightRoute._get_route_from_sb(async_client, flight_callsign)
    assert route == ROUTE_SB


@pytest.mark.asyncio
async def test_hx_route_source_mp_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, flight_callsign: str):
    httpx_mock.add_response(url=HX_ROUTE_URL, **HX_ROUTE_MP_RESP_200)
    httpx_mock.add_response(url=HX_DEP_AIRPORT_URL, **HX_AIRPORT_RESP_200)
    httpx_mock.add_response(url=HX_DST_AIRPORT_URL, **HX_AIRPORT_RESP_200)
    httpx_mock.add_response(url=HX_MID_AIRPORT_URL, **HX_AIRPORT_RESP_404)
    httpx_mock.add_response(url=AD_MID_AIRPORT_URL, **AD_AIRPORT_RESP_200)

    route = await FlightRoute._get_route_from_hx(async_client, flight_callsign)
    assert route == ROUTE_HX_WITH_STOP


@pytest.mark.asyncio
async def test_sb_route_source_mp_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, flight_callsign: str):
    httpx_mock.add_response(url=SB_ROUTE_URL, **SB_ROUTE_MP_RESP_200)

    route = await FlightRoute._get_route_from_sb(async_client, flight_callsign)
    assert route == ROUTE_SB_WITH_STOP


@pytest.mark.asyncio
async def test_hx_ad_route_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, flight_callsign: str):
    httpx_mock.add_response(url=HX_ROUTE_URL, **HX_ROUTE_RESP_200)
    httpx_mock.add_response(url=HX_DEP_AIRPORT_URL, **HX_AIRPORT_RESP_502)
    httpx_mock.add_response(url=HX_DST_AIRPORT_URL, **HX_AIRPORT_RESP_404)
    httpx_mock.add_response(url=AD_DEP_AIRPORT_URL, **AD_AIRPORT_RESP_404)
    httpx_mock.add_response(url=AD_DST_AIRPORT_URL, **AD_AIRPORT_RESP_502)

    route = await FlightRoute._get_route_from_hx(async_client, flight_callsign)
    assert route == ROUTE_AIRPORT_UNKNOWN


@pytest.mark.asyncio
async def test_sb_route_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, flight_callsign: str):
    httpx_mock.add_response(url=SB_ROUTE_URL, **SB_ROUTE_RESP_404)

    route = await FlightRoute._get_route_from_sb(async_client, flight_callsign)
    assert route is None


@pytest.mark.asyncio
async def test_hx_route_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, flight_callsign: str):
    httpx_mock.add_response(url=HX_ROUTE_URL, **HX_ROUTE_RESP_404)

    route = await FlightRoute._get_route_from_hx(async_client, flight_callsign)
    assert route is None


@pytest.mark.asyncio
@pytest.mark.parametrize("_route", ["", "FCO/DUB", None])
async def test_hx_route_source_unavailable(
    _route: str,
    async_client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
    flight_callsign: str,
):
    httpx_mock.add_response(url=HX_ROUTE_URL, **HX_ROUTE_RESP_502)
    httpx_mock.add_response(url=SB_ROUTE_URL, **SB_ROUTE_RESP_200)

    route = await FlightRoute.get_route(async_client, flight_callsign)
    assert route == ROUTE_SB


@pytest.mark.asyncio
@pytest.mark.parametrize("_route", ["", "FCO/DUB", None])
async def test_all_route_sources_unavailable(
    _route: str,
    async_client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
    flight_callsign: str,
):
    httpx_mock.add_response(url=SB_ROUTE_URL, **SB_ROUTE_RESP_502)
    httpx_mock.add_response(url=HX_ROUTE_URL, **HX_ROUTE_RESP_502)

    route = await FlightRoute.get_route(async_client, flight_callsign)
    assert route == ROUTE_EMPTY
