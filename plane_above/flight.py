import asyncio
from urllib.parse import urljoin
from collections.abc import Collection

import httpx

from .utils import log, async_get
from .models import Flight, Airport
from .static import (
    ROUTE_DETAILS_HX_SOURCE_URL,
    ROUTE_DETAILS_SB_SOURCE_URL,
    AIRPORT_DETAILS_AD_SOURCE_URL,
    AIRPORT_DETAILS_HX_SOURCE_URL,
    RouteSource,
)


class FlightRoute:
    @staticmethod
    async def _get_airport_details(_client: httpx.AsyncClient, iata: str) -> Airport:
        result = await async_get(_client, urljoin(AIRPORT_DETAILS_HX_SOURCE_URL, iata))
        if (name := result.json_data.get("airport")) and (country_code := result.json_data.get("country_code")):
            return Airport(iata=iata, name=name, country_code=country_code)

        result = await async_get(_client, AIRPORT_DETAILS_AD_SOURCE_URL, params=dict(iata=iata))
        return Airport(
            iata=iata,
            name=result.json_data.get("name") or "Unknown airport",
            country_code=result.json_data.get("country_code") or Airport.country_code,
        )

    @classmethod
    async def _get_route_from_hx(cls, _client: httpx.AsyncClient, callsign: str) -> Flight | None:
        result = await async_get(_client, urljoin(ROUTE_DETAILS_HX_SOURCE_URL, callsign))
        if (result.status_code != httpx.codes.NOT_FOUND) and (route := result.json_data.get("route")):
            try:
                departure_iata, *stops, destination_iata = route.split("-")
                departure, destination, *stops = await asyncio.gather(
                    cls._get_airport_details(_client, departure_iata),
                    cls._get_airport_details(_client, destination_iata),
                    *[cls._get_airport_details(_client, stop_iata) for stop_iata in stops],
                )
                return Flight(callsign=callsign, departure=departure, destination=destination, stops=stops)

            except ValueError:
                log.error(f" ✈ Cannot parse route for {callsign}: {route}.")

        return None

    @staticmethod
    async def _get_route_from_sb(_client: httpx.AsyncClient, callsign: str) -> Flight | None:
        result = await async_get(_client, urljoin(ROUTE_DETAILS_SB_SOURCE_URL, callsign))
        if not httpx.codes.is_success(result.status_code) or not result.json_data:
            return None

        response = result.json_data.get("response", {}).get("flightroute", {})
        departure = response.get("origin", {})
        destination = response.get("destination", {})
        stop = response.get("midpoint", {})
        airline = response.get("airline", {}).get("name") or Flight.airline
        return Flight(
            callsign=callsign,
            departure=Airport(
                iata=departure.get("iata_code") or Airport.iata,
                name=departure.get("name") or Airport.name,
                country_code=departure.get("country_iso_name") or Airport.country_code,
            ),
            destination=Airport(
                iata=destination.get("iata_code") or Airport.iata,
                name=destination.get("name") or Airport.name,
                country_code=destination.get("country_iso_name") or Airport.country_code,
            ),
            stops=[
                Airport(
                    iata=stop.get("iata_code") or Airport.iata,
                    name=stop.get("name") or Airport.name,
                    country_code=stop.get("country_iso_name") or Airport.country_code,
                ),
            ]
            if stop
            else [],
            airline=airline,
        )

    @classmethod
    async def get_route(cls, _client: httpx.AsyncClient, callsign: str, sources: Collection[RouteSource]) -> Flight:
        if callsign:
            if RouteSource.HX in sources and (route := await cls._get_route_from_hx(_client, callsign)):
                return route

            if RouteSource.SB in sources and (route := await cls._get_route_from_sb(_client, callsign)):
                return route

        return Flight(
            callsign=callsign or "",
            departure=Airport(name="Unknown departure"),
            destination=Airport(name="Unknown destination"),
            stops=[],
            airline=Flight.airline,
        )
