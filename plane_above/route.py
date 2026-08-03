import asyncio
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx

from .utils import log, async_get
from .static import (
    ROUTE_DETAILS_HX_SOURCE_URL,
    ROUTE_DETAILS_SB_SOURCE_URL,
    AIRPORT_DETAILS_AD_SOURCE_URL,
    AIRPORT_DETAILS_HX_SOURCE_URL,
)


@dataclass(frozen=True)
class Airport:
    iata: str = "N/A"
    name: str = "Unknown airport"
    country_code: str = ""


@dataclass(frozen=True)
class Route:
    departure: Airport
    destination: Airport
    stops: list[Airport]
    airline: str | None = None


class FlightRoute:
    @staticmethod
    async def _get_airport_details(_client: httpx.AsyncClient, iata: str) -> Airport:
        result = await async_get(_client, urljoin(AIRPORT_DETAILS_HX_SOURCE_URL, iata))
        if (name := result.json_data.get("airport")) and (country_code := result.json_data.get("country_code")):
            return Airport(iata=iata, name=name, country_code=country_code)

        result = await async_get(_client, AIRPORT_DETAILS_AD_SOURCE_URL, params=dict(iata=iata))
        return Airport(
            iata=iata,
            name=result.json_data.get("name", "Unknown airport"),
            country_code=result.json_data.get("country_code") or "",
        )

    @classmethod
    async def _get_route_from_hx(cls, _client: httpx.AsyncClient, callsign: str) -> Route | None:
        result = await async_get(_client, urljoin(ROUTE_DETAILS_HX_SOURCE_URL, callsign))
        if (result.status_code != httpx.codes.NOT_FOUND) and (route := result.json_data.get("route")):
            try:
                departure_iata, *stops, destination_iata = route.split("-")
                departure, destination, *stops = await asyncio.gather(
                    cls._get_airport_details(_client, departure_iata),
                    cls._get_airport_details(_client, destination_iata),
                    *[cls._get_airport_details(_client, stop_iata) for stop_iata in stops],
                )
                return Route(departure=departure, destination=destination, stops=stops)

            except ValueError:
                log.error(f" ✈ Cannot parse route for {callsign}: {route}.")

        return None

    @staticmethod
    async def _get_route_from_sb(_client: httpx.AsyncClient, callsign: str) -> Route | None:
        result = await async_get(_client, urljoin(ROUTE_DETAILS_SB_SOURCE_URL, callsign))
        if not httpx.codes.is_success(result.status_code) or not result.json_data:
            return None

        response = result.json_data.get("response", {}).get("flightroute", {})
        departure = response.get("origin", {})
        destination = response.get("destination", {})
        stop = response.get("midpoint", {})
        airline = response.get("airline", {}).get("name")
        return Route(
            departure=Airport(
                iata=departure.get("iata_code"),
                name=departure.get("name"),
                country_code=departure.get("country_iso_name"),
            ),
            destination=Airport(
                iata=destination.get("iata_code"),
                name=destination.get("name"),
                country_code=destination.get("country_iso_name"),
            ),
            stops=[
                Airport(
                    iata=stop.get("iata_code"),
                    name=stop.get("name"),
                    country_code=stop.get("country_iso_name"),
                ),
            ]
            if stop
            else [],
            airline=airline,
        )

    @classmethod
    async def get_route(cls, _client: httpx.AsyncClient, callsign: str) -> Route:
        if callsign:
            if route := await cls._get_route_from_hx(_client, callsign):
                return route

            if route := await cls._get_route_from_sb(_client, callsign):
                return route

        return Route(
            departure=Airport(name="Unknown departure"),
            destination=Airport(name="Unknown destination"),
            stops=[],
            airline=None,
        )
