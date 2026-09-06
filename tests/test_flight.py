import httpx
import pytest
from pytest_httpx import HTTPXMock

from tests import FlightMocks
from tests.data import FLIGHT_CALLSIGN
from plane_above.flight import FlightRoute
from plane_above.models import Flight, Airport
from plane_above.static import RouteSource

CALLSIGN_EMPTY = Flight(
    callsign="",
    departure=Airport(iata="N/A", name="Unknown departure", country_code="UN"),
    destination=Airport(iata="N/A", name="Unknown destination", country_code="UN"),
    stops=[],
)
ROUTE_EMPTY = Flight(
    callsign=FLIGHT_CALLSIGN,
    departure=Airport(iata="N/A", name="Unknown departure", country_code="UN"),
    destination=Airport(iata="N/A", name="Unknown destination", country_code="UN"),
    stops=[],
)
ROUTE_AIRPORT_UNKNOWN = Flight(
    callsign=FLIGHT_CALLSIGN,
    departure=Airport(iata="DEP", name="Unknown airport", country_code="UN"),
    destination=Airport(iata="DST", name="Unknown airport", country_code="UN"),
    stops=[],
)
ROUTE_HX = Flight(
    callsign=FLIGHT_CALLSIGN,
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
    airline="",
)
ROUTE_HX_WITH_STOP = Flight(
    callsign=FLIGHT_CALLSIGN,
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
            name="Valencia Airport",
            country_code="ES",
        ),
    ],
    airline="",
)
ROUTE_HX_AD_WITH_STOP = Flight(
    callsign=FLIGHT_CALLSIGN,
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
    airline="",
)
ROUTE_HX_AD = Flight(
    callsign=FLIGHT_CALLSIGN,
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
    airline="",
)
ROUTE_SB = Flight(
    callsign=FLIGHT_CALLSIGN,
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
    callsign=FLIGHT_CALLSIGN,
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
            country_code="UN",
        )
    ],
    airline="United Airlines",
)


@pytest.mark.asyncio
@pytest.mark.parametrize("_callsign", ["", None])
async def test_route_without_callsign(_callsign: str | None, async_client: httpx.AsyncClient):
    route = await FlightRoute.get_route(async_client, _callsign, {RouteSource.HX, RouteSource.SB})
    assert route == CALLSIGN_EMPTY


@pytest.mark.asyncio
async def test_hx_route_source_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_RESP_200, is_reusable=True)
    httpx_mock.add_response(url=FlightMocks.HX_DEP_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_200, is_reusable=True)
    httpx_mock.add_response(url=FlightMocks.HX_DST_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_200, is_reusable=True)

    route_from_hx = await FlightRoute._get_route_from_hx(async_client, FLIGHT_CALLSIGN)
    assert route_from_hx == ("DEP", "DST", [], 1536225143)

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, (RouteSource.HX,))
    assert route == ROUTE_HX


@pytest.mark.asyncio
async def test_hx_ad_route_source_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_RESP_200)
    httpx_mock.add_response(url=FlightMocks.HX_DEP_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_404)
    httpx_mock.add_response(url=FlightMocks.HX_DST_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_502)
    httpx_mock.add_response(url=FlightMocks.AD_DEP_AIRPORT_URL, **FlightMocks.AD_AIRPORT_RESP_200)
    httpx_mock.add_response(url=FlightMocks.AD_DST_AIRPORT_URL, **FlightMocks.AD_AIRPORT_RESP_200)

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, (RouteSource.HX,))
    assert route == ROUTE_HX_AD


@pytest.mark.asyncio
async def test_sb_route_source_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.SB_ROUTE_URL, **FlightMocks.SB_ROUTE_RESP_200, is_reusable=True)

    route_from_sb = await FlightRoute._get_route_from_sb(async_client, FLIGHT_CALLSIGN)
    assert route_from_sb is not None
    assert route_from_sb[0] == "CRK"
    assert route_from_sb[1] == "PUS"
    assert route_from_sb[2] == []

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, (RouteSource.SB,))
    assert route == ROUTE_SB


@pytest.mark.asyncio
async def test_hx_route_source_mp_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_MP_RESP_200)
    httpx_mock.add_response(url=FlightMocks.HX_DEP_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_200)
    httpx_mock.add_response(url=FlightMocks.HX_DST_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_200)
    httpx_mock.add_response(url=FlightMocks.HX_MID_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_404)
    httpx_mock.add_response(url=FlightMocks.AD_MID_AIRPORT_URL, **FlightMocks.AD_AIRPORT_RESP_200)

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, (RouteSource.HX,))
    assert route == ROUTE_HX_AD_WITH_STOP


@pytest.mark.asyncio
async def test_sb_route_source_mp_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.SB_ROUTE_URL, **FlightMocks.SB_ROUTE_MP_RESP_200)

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, (RouteSource.SB,))
    assert route == ROUTE_SB_WITH_STOP


@pytest.mark.asyncio
async def test_all_route_sources_mp_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.SB_ROUTE_URL, **FlightMocks.SB_ROUTE_MP_RESP_200)
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_MP_RESP_200)
    httpx_mock.add_response(url=FlightMocks.HX_DEP_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_200)
    httpx_mock.add_response(url=FlightMocks.HX_DST_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_200)
    httpx_mock.add_response(url=FlightMocks.HX_MID_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_200)

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, (RouteSource.SB, RouteSource.HX))
    assert route == ROUTE_HX_WITH_STOP


@pytest.mark.asyncio
async def test_hx_ad_route_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_RESP_200)
    httpx_mock.add_response(url=FlightMocks.HX_DEP_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_502)
    httpx_mock.add_response(url=FlightMocks.HX_DST_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_404)
    httpx_mock.add_response(url=FlightMocks.AD_DEP_AIRPORT_URL, **FlightMocks.AD_AIRPORT_RESP_404)
    httpx_mock.add_response(url=FlightMocks.AD_DST_AIRPORT_URL, **FlightMocks.AD_AIRPORT_RESP_502)

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, (RouteSource.HX,))
    assert route == ROUTE_AIRPORT_UNKNOWN


@pytest.mark.asyncio
async def test_sb_route_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.SB_ROUTE_URL, **FlightMocks.SB_ROUTE_RESP_404)

    route = await FlightRoute._get_route_from_sb(async_client, FLIGHT_CALLSIGN)
    assert route is None


@pytest.mark.asyncio
async def test_hx_route_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_RESP_404)

    route = await FlightRoute._get_route_from_hx(async_client, FLIGHT_CALLSIGN)
    assert route is None


@pytest.mark.asyncio
async def test_hx_route_source_invalid(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_VAR_RESP_200)

    route = await FlightRoute._get_route_from_hx(async_client, FLIGHT_CALLSIGN)
    assert route is None


@pytest.mark.asyncio
async def test_hx_route_source_unavailable_with_sb_setup(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_RESP_502)
    httpx_mock.add_response(url=FlightMocks.SB_ROUTE_URL, **FlightMocks.SB_ROUTE_RESP_200)

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, {RouteSource.HX, RouteSource.SB})
    assert route == ROUTE_SB


@pytest.mark.asyncio
async def test_hx_route_source_unavailable_without_sb_setup(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_RESP_404)

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, {RouteSource.HX})
    assert route == ROUTE_EMPTY


@pytest.mark.asyncio
async def test_all_route_sources_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_RESP_200)
    httpx_mock.add_response(url=FlightMocks.SB_ROUTE_URL, **FlightMocks.SB_ROUTE_RESP_200)

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, (RouteSource.SB, RouteSource.HX))
    assert route == ROUTE_SB


@pytest.mark.asyncio
async def test_all_route_sources_agree(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_AS_SB_RESP_200)
    httpx_mock.add_response(url=FlightMocks.SB_ROUTE_URL, **FlightMocks.SB_ROUTE_RESP_200)

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, (RouteSource.SB, RouteSource.HX))
    assert route == ROUTE_SB


@pytest.mark.asyncio
async def test_hx_route_source_round(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_ROUND_RESP_200)
    httpx_mock.add_response(url=FlightMocks.SB_ROUTE_URL, **FlightMocks.SB_ROUTE_RESP_200)

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, (RouteSource.SB, RouteSource.HX))
    assert route == ROUTE_SB


@pytest.mark.asyncio
async def test_all_route_sources_unavailable(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=FlightMocks.SB_ROUTE_URL, **FlightMocks.SB_ROUTE_RESP_502)
    httpx_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_RESP_502)

    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, {RouteSource.HX, RouteSource.SB})
    assert route == ROUTE_EMPTY


@pytest.mark.asyncio
async def test_no_route_sources_requested(async_client: httpx.AsyncClient):
    route = await FlightRoute.get_route(async_client, FLIGHT_CALLSIGN, {})
    assert route == ROUTE_EMPTY
