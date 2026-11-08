import asyncio
import warnings
from typing import Any
from collections.abc import Generator, AsyncGenerator

import httpx

from .osn import OSN
from .utils import PlaneAboveClient, log
from .config import Config
from .flight import FlightRoute
from .models import Above, Photo, State, Flight, Airport, Spotted, Aircraft, FlyingObject
from .static import DEFAULT_DISTANCE_FROM_POINT, DataSource
from .aircraft import AircraftDetails


class PlaneAbove:
    """Retrieving detailed information about flying objects above given point.

    Fetches aircraft details, flight routes, and photos for each spotted object,
    combining data from multiple sources into structured `Above` instances.

    Attributes:
        spotted (Spotted): Container with flying objects and additional info.
    """

    def __init__(
        self,
        point: tuple[float, float],
        distance: float = DEFAULT_DISTANCE_FROM_POINT,
        config: Config | None = None,
        **kwargs: Any,
    ):
        """Initialize PlaneAbove client with search parameters and API credentials.

        Args:
            point: Geographic coordinates as (latitude, longitude).
            distance: Search radius in kilometers from the given point.
            config: Configuration parameters.
        """
        default_config = Config()
        if kwargs:
            warnings.warn(
                f"'{', '.join(kwargs.keys())}' will be removed in v1.0.0, use 'Config' for correct setup",
                DeprecationWarning,
                stacklevel=2,
            )
            self.config = Config(
                route_sources=kwargs.get("route_sources", default_config.route_sources),
                photo_sources=kwargs.get("photo_sources", default_config.photo_sources),
                user_agent=kwargs.get("ps_user_agent", default_config.user_agent),
                proxy_url=kwargs.get("osn_proxy", default_config.proxy_url),
                proxy_scope=(DataSource.OPENSKY,),
                osn_id=kwargs.get("osn_id", default_config.osn_id),
                osn_secret=kwargs.get("osn_secret", default_config.osn_secret),
            )
        else:
            self.config = config or default_config

        self.spotted = Spotted(*OSN.get_flying_objects(point, distance, self.config), errors=[])

    async def _collect_data(
        self,
        client: httpx.AsyncClient,
        f_object: FlyingObject,
    ) -> tuple[Aircraft, Flight, State]:
        try:
            aircraft, flight = await asyncio.gather(
                AircraftDetails.get_details(client, f_object.icao24, f_object.country, self.config.photo_sources),
                FlightRoute.get_route(client, f_object.callsign, self.config.route_sources),
            )
            return aircraft, flight, f_object.state

        except Exception as exc:  # noqa: BLE001
            log.error(f" ✈ Exception occurred for plane {f_object.icao24}: {exc}")
            self.spotted.errors.append((f"{f_object.icao24}", str(exc)))
            return (
                Aircraft(
                    icao24=f_object.icao24,
                    registration="",
                    manufacturer="",
                    model="",
                    type_code="",
                    country=f_object.country,
                    operator="",
                    age=0.0,
                    photos=[Photo()],
                ),
                Flight(
                    callsign=f_object.callsign,
                    departure=Airport(),
                    destination=Airport(),
                    stops=[],
                    airline="",
                ),
                f_object.state,
            )

    def fetch(self) -> Generator[Above]:
        """Retrieve detailed data for all spotted flying objects.

        Iterates over filtered flying objects, fetches data for each and yields populated Above instances.

        Yields:
            Above: Structured Aircraft, Flight and State data for each spotted object.
        """
        planes_generator = self.async_fetch()
        loop = asyncio.new_event_loop()
        try:
            while True:
                yield loop.run_until_complete(planes_generator.__anext__())
        except StopAsyncIteration:
            pass
        finally:
            loop.run_until_complete(planes_generator.aclose())
            loop.close()

    async def async_fetch(self) -> AsyncGenerator[Above]:
        """Asynchronously retrieve detailed data for all spotted flying objects.

        Iterates over filtered flying objects, fetches data for each and yields populated Above instances.

        Yields:
            Above: Structured Aircraft, Flight and State data for each spotted object.
        """
        headers = {"User-Agent": self.config.user_agent} if self.config.user_agent else {}
        mounts = (
            {
                f"all://*{source.value}": httpx.AsyncHTTPTransport(proxy=self.config.proxy_url)
                for source in self.config.proxy_scope
            }
            if self.config.proxy_url and self.config.proxy_scope
            else None
        )

        async with PlaneAboveClient(headers=headers, mounts=mounts) as client:
            for f_object in self.spotted.objects_filtered:
                yield Above(*await self._collect_data(client, f_object))
