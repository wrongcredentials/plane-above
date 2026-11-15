import json

import pytest
from pytest_httpx2 import HTTPXMock

from tests import PhotoMocks, FlightMocks, AircraftMocks
from tests.data import AIRCRAFT_AGE, AIRCRAFT_ICAO, FLIGHT_CALLSIGN, AIRCRAFT_COUNTRY
from plane_above.flight import FlightRoute
from plane_above.models import Photo, State, Flight, Airport, Aircraft, FlyingObject
from plane_above.aircraft import AircraftDetails
from tests.data.osn.flying_objects import ABOVE_FETCH


@pytest.mark.parametrize(
    "plane_above_mock",
    [ABOVE_FETCH],
    indirect=True,
)
def test_sync_fetch(plane_above_mock, httpx2_mock: HTTPXMock):
    assert plane_above_mock.spotted.objects_raw == ABOVE_FETCH
    assert plane_above_mock.spotted.objects_filtered == [
        FlyingObject(
            icao24=AIRCRAFT_ICAO,
            callsign=FLIGHT_CALLSIGN,
            country=AIRCRAFT_COUNTRY,
            state=State(velocity=174, altitude=366, latitude=51.5724, longitude=5.2843),
        ),
    ]
    assert plane_above_mock.spotted.errors == []
    assert plane_above_mock.spotted.success is True
    assert plane_above_mock.spotted.how_many == 1

    httpx2_mock.add_response(url=AircraftMocks.SB_AIRCRAFT_URL, **AircraftMocks.SB_AIRCRAFT_RESP_200)
    httpx2_mock.add_response(url=AircraftMocks.HX_AIRCRAFT_URL, **AircraftMocks.HX_AIRCRAFT_RESP_200)
    httpx2_mock.add_response(url=AircraftMocks.FD_AIRCRAFT_URL, **AircraftMocks.FD_AIRCRAFT_RESP_200)
    httpx2_mock.add_response(url=AircraftMocks.AD_AIRCRAFT_URL, **AircraftMocks.AD_AIRCRAFT_RESP_200)
    httpx2_mock.add_response(url=PhotoMocks.HX_PHOTO_URL, **PhotoMocks.HX_PHOTO_RESP_200)

    httpx2_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_RESP_200)
    httpx2_mock.add_response(url=FlightMocks.HX_DEP_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_200)
    httpx2_mock.add_response(url=FlightMocks.HX_DST_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_200)

    for above in plane_above_mock.fetch():
        assert above.aircraft.icao24 == AIRCRAFT_ICAO
        assert above.aircraft.country == AIRCRAFT_COUNTRY
        assert above.aircraft.age >= AIRCRAFT_AGE
        assert above.aircraft.registration == "A7-BCA"
        assert above.aircraft.manufacturer == "Boeing"
        assert above.aircraft.model == "737-8 MAX"
        assert above.aircraft.type_code == "B788"
        assert len(above.aircraft.photos) == 1
        assert above.aircraft.photos[0]._has_urls is True
        assert above.aircraft.photos[0].image_url == "https://hexdb.io/static/aircraft-images/PH-BXC.jpg"
        assert above.aircraft.photos[0].origin_url == "https://hexdb.io/static/aircraft-images/PH-BXC.jpg"
        assert above.aircraft.photos[0].photographer == ""
        assert above.aircraft.operator == "Qatar Airways"
        assert above.flight.callsign == FLIGHT_CALLSIGN
        assert above.flight.departure.iata == "DEP"
        assert above.flight.departure.name == "Valencia Airport"
        assert above.flight.departure.country_code == "ES"
        assert above.flight.destination.iata == "DST"
        assert above.flight.destination.name == "Valencia Airport"
        assert above.flight.destination.country_code == "ES"
        assert above.flight.stops == []
        assert above.flight.airline == ""
        assert above.state.altitude == 366
        assert above.state.velocity == 174
        assert above.state.latitude == 51.5724
        assert above.state.longitude == 5.2843
        assert json.loads(above.to_json()) == above.to_dict()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "plane_above_mock",
    [ABOVE_FETCH],
    indirect=True,
)
async def test_async_fetch(plane_above_mock, httpx2_mock: HTTPXMock):
    assert plane_above_mock.spotted.objects_raw == ABOVE_FETCH
    assert plane_above_mock.spotted.objects_filtered == [
        FlyingObject(
            icao24=AIRCRAFT_ICAO,
            callsign=FLIGHT_CALLSIGN,
            country=AIRCRAFT_COUNTRY,
            state=State(velocity=174, altitude=366, latitude=51.5724, longitude=5.2843),
        ),
    ]
    assert plane_above_mock.spotted.errors == []
    assert plane_above_mock.spotted.success is True
    assert plane_above_mock.spotted.how_many == 1

    httpx2_mock.add_response(url=AircraftMocks.SB_AIRCRAFT_URL, **AircraftMocks.SB_AIRCRAFT_RESP_200)
    httpx2_mock.add_response(url=AircraftMocks.HX_AIRCRAFT_URL, **AircraftMocks.HX_AIRCRAFT_RESP_200)
    httpx2_mock.add_response(url=AircraftMocks.FD_AIRCRAFT_URL, **AircraftMocks.FD_AIRCRAFT_RESP_404)
    httpx2_mock.add_response(url=AircraftMocks.AD_AIRCRAFT_URL, **AircraftMocks.AD_AIRCRAFT_RESP_404)

    httpx2_mock.add_response(url=PhotoMocks.HX_PHOTO_URL, **PhotoMocks.HX_PHOTO_RESP_200)

    httpx2_mock.add_response(url=FlightMocks.HX_ROUTE_URL, **FlightMocks.HX_ROUTE_MP_RESP_200)
    httpx2_mock.add_response(url=FlightMocks.HX_DEP_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_200)
    httpx2_mock.add_response(url=FlightMocks.HX_MID_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_200)
    httpx2_mock.add_response(url=FlightMocks.HX_DST_AIRPORT_URL, **FlightMocks.HX_AIRPORT_RESP_200)

    async for above in plane_above_mock.async_fetch():
        assert above.aircraft.icao24 == AIRCRAFT_ICAO
        assert above.flight.callsign == FLIGHT_CALLSIGN
        assert above.aircraft.country == "Korea, Republic of"
        assert above.aircraft.age == 0.0
        assert above.aircraft.registration == "A7-BCA"
        assert above.aircraft.manufacturer == "Boeing"
        assert above.aircraft.model == "737-8 MAX"
        assert above.aircraft.type_code == "B788"
        assert above.aircraft.operator == "Qatar Airways"
        assert above.aircraft.photos[0]._has_urls is True
        assert above.aircraft.photos[0].image_url == "https://hexdb.io/static/aircraft-images/PH-BXC.jpg"
        assert above.aircraft.photos[0].origin_url == "https://hexdb.io/static/aircraft-images/PH-BXC.jpg"
        assert above.aircraft.photos[0].photographer == ""
        assert above.flight.departure.iata == "DEP"
        assert above.flight.departure.name == "Valencia Airport"
        assert above.flight.departure.country_code == "ES"
        assert above.flight.destination.iata == "DST"
        assert above.flight.destination.name == "Valencia Airport"
        assert above.flight.destination.country_code == "ES"
        assert len(above.flight.stops) == 1
        assert above.flight.stops[0].iata == "MID"
        assert above.flight.stops[0].name == "Valencia Airport"
        assert above.flight.stops[0].country_code == "ES"
        assert above.flight.airline == ""
        assert above.state.altitude == 366
        assert above.state.velocity == 174
        assert above.state.latitude == 51.5724
        assert above.state.longitude == 5.2843


@pytest.mark.parametrize(
    "plane_above_mock",
    [ABOVE_FETCH],
    indirect=True,
)
def test_fetch_error(plane_above_mock, monkeypatch):
    async def broken_get_details(*args, **kwargs):
        raise RuntimeError("Pull up!")

    monkeypatch.setattr(AircraftDetails, "get_details", broken_get_details)
    monkeypatch.setattr(FlightRoute, "get_route", broken_get_details)

    results = list(plane_above_mock.fetch())
    assert len(results) == 1
    assert len(plane_above_mock.spotted.errors) == 1
    error_key, error_message = plane_above_mock.spotted.errors[0]
    assert error_key == AIRCRAFT_ICAO
    assert error_message == "Pull up!"
    assert results[0] == (
        Aircraft(
            icao24=AIRCRAFT_ICAO,
            registration="",
            manufacturer="",
            model="",
            type_code="",
            country=AIRCRAFT_COUNTRY,
            operator="",
            age=0.0,
            photos=[Photo()],
        ),
        Flight(
            callsign=FLIGHT_CALLSIGN,
            departure=Airport(),
            destination=Airport(),
            stops=[],
            airline="",
        ),
        State(
            altitude=366,
            velocity=174,
            latitude=51.5724,
            longitude=5.2843,
        ),
    )
