import asyncio
import datetime
from typing import Any
from urllib.parse import urljoin
from collections.abc import Callable, Coroutine, Collection

import httpx
from dateutil.relativedelta import relativedelta

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
        name = result.json_data.get("airport") or ""
        country_code = result.json_data.get("country_code") or ""
        if name and country_code:
            return Airport(iata=iata, name=name, country_code=country_code)

        result = await async_get(_client, AIRPORT_DETAILS_AD_SOURCE_URL, params=dict(iata=iata))
        return Airport(
            iata=iata,
            name=result.json_data.get("name") or "Unknown airport",
            country_code=result.json_data.get("country_code") or Airport.country_code,
        )

    @classmethod
    async def _build_flight_from_hx(
        cls,
        _client: httpx.AsyncClient,
        callsign: str,
        departure_iata: str,
        destination_iata: str,
        stops_iata: list[str],
    ) -> Flight:
        departure, destination, *stops = await asyncio.gather(
            cls._get_airport_details(_client, departure_iata),
            cls._get_airport_details(_client, destination_iata),
            *[cls._get_airport_details(_client, stop_iata) for stop_iata in stops_iata],
        )
        return Flight(callsign=callsign, departure=departure, destination=destination, stops=stops)

    @staticmethod
    async def _parse_flight_from_sb(callsign: str, response: dict[str, Any]) -> Flight:
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

    @staticmethod
    async def _get_route_from_hx(
        _client: httpx.AsyncClient, callsign: str
    ) -> tuple[str, str, list[str], int | None] | None:
        result = await async_get(_client, urljoin(ROUTE_DETAILS_HX_SOURCE_URL, callsign))
        if (result.status_code != httpx.codes.NOT_FOUND) and (route := result.json_data.get("route")):
            try:
                departure_iata, *stops, destination_iata = route.split("-")
                return departure_iata, destination_iata, stops, result.json_data.get("updatetime")
            except ValueError:
                log.error(f" ✈ Cannot parse route for {callsign}: {route}.")
        return None

    @staticmethod
    async def _get_route_from_sb(
        _client: httpx.AsyncClient, callsign: str
    ) -> tuple[str, str, list[str], dict[str, Any]] | None:
        result = await async_get(_client, urljoin(ROUTE_DETAILS_SB_SOURCE_URL, callsign))
        if not httpx.codes.is_success(result.status_code) or not result.json_data:
            return None

        response = result.json_data.get("response", {}).get("flightroute", {})
        departure_iata = response.get("origin", {}).get("iata_code")
        destination_iata = response.get("destination", {}).get("iata_code")
        stop_iata = response.get("midpoint", {}).get("iata_code")
        return departure_iata, destination_iata, [stop_iata] if stop_iata else [], response

    @staticmethod
    def _is_hx_route_stale(last_update: int | None, max_age_years: int = 3) -> bool:
        if last_update is None:
            return True
        updated_at = datetime.datetime.fromtimestamp(last_update, tz=datetime.timezone.utc)
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        return bool(updated_at + relativedelta(years=max_age_years) < now)

    @classmethod
    async def get_route(cls, _client: httpx.AsyncClient, callsign: str, sources: Collection[RouteSource]) -> Flight:
        tasks: dict[RouteSource, Callable[[], Coroutine[Any, Any, Any]]] = {
            RouteSource.HX: lambda: cls._get_route_from_hx(_client, callsign),
            RouteSource.SB: lambda: cls._get_route_from_sb(_client, callsign),
        }

        if callsign:
            active_sources = [source for source in tasks if source in sources]
            results = await asyncio.gather(*(tasks[source]() for source in active_sources))
            results_by_source = dict(zip(active_sources, results, strict=True))

            hx_route = results_by_source.get(RouteSource.HX, [])
            sb_route = results_by_source.get(RouteSource.SB, [])

            if hx_route and sb_route:
                hx_dep, hx_dest, hx_stops, hx_last_update = hx_route
                sb_dep, sb_dest, sb_stops, sb_response = sb_route
                if hx_dep == sb_dep and hx_dest == sb_dest and hx_stops == sb_stops:
                    return await cls._parse_flight_from_sb(callsign, sb_response)

                if cls._is_hx_route_stale(hx_last_update):
                    return await cls._parse_flight_from_sb(callsign, sb_response)

                if hx_dep == hx_dest and sb_dep != sb_dest:
                    return await cls._parse_flight_from_sb(callsign, sb_response)
                return await cls._build_flight_from_hx(_client, callsign, hx_dep, hx_dest, hx_stops)

            if hx_route:
                hx_dep, hx_dest, hx_stops, _ = hx_route
                return await cls._build_flight_from_hx(_client, callsign, hx_dep, hx_dest, hx_stops)

            if sb_route:
                *_, sb_response = sb_route
                return await cls._parse_flight_from_sb(callsign, sb_response)

        return Flight(
            callsign=callsign or "",
            departure=Airport(name="Unknown departure"),
            destination=Airport(name="Unknown destination"),
            stops=[],
            airline=Flight.airline,
        )
