import asyncio
from collections.abc import Generator, AsyncGenerator

import httpx

from .osn import OSN
from .utils import PlaneAboveClient, log
from .flight import FlightRoute
from .models import Above, Photo, State, Flight, Airport, Spotted, Aircraft, FlyingObject
from .static import DEFAULT_DISTANCE_FROM_POINT
from .aircraft import AircraftDetails


class PlaneAbove:
    """Retrieving detailed information about flying objects above given point.

    Fetches aircraft details, flight routes, and photos for each spotted object,
    combining data from multiple sources into structured `Above` instances.

    Attributes:
        spotted (Spotted): Container with flying objects and additional info.
        _ps_user_agent (str): User-Agent string for PlaneSpotters API requests.
    """

    def __init__(
        self,
        point: tuple[float, float],
        *,
        distance: int | float = DEFAULT_DISTANCE_FROM_POINT,
        osn_id: str = "",
        osn_secret: str = "",
        osn_proxy: str | None = None,
        ps_user_agent: str = "",
    ):
        """Initialize PlaneAbove client with search parameters and API credentials.

        Args:
            point: Geographic coordinates as (latitude, longitude).
            distance: Search radius in kilometers from the given point.
            osn_id: OpenSky Network API identifier.
            osn_secret: OpenSky Network API secret.
            osn_proxy: Optional proxy URL for OpenSky Network requests.
            ps_user_agent: User-Agent string for PlaneSpotters API requests.
        """
        self._ps_user_agent = ps_user_agent
        self.spotted = Spotted(*OSN.get_flying_objects(point, distance, osn_id, osn_secret, osn_proxy), errors=[])

    async def _collect_data(
        self,
        client: httpx.AsyncClient,
        f_object: FlyingObject,
    ) -> tuple[Aircraft, Flight, State]:
        try:
            aircraft, flight = await asyncio.gather(
                AircraftDetails.get_details(
                    client,
                    f_object.icao24,
                    f_object.country,
                    self._ps_user_agent,
                ),
                FlightRoute.get_route(client, f_object.callsign),
            )
            return aircraft, flight, f_object.state

        except Exception as exc:
            log.error(f" ✈ Exception occurred for plane {f_object.icao24}: {exc}")
            self.spotted.errors.append((f"{f_object.icao24=}", exc))
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
        async with PlaneAboveClient() as client:
            for f_object in self.spotted.objects_filtered:
                yield Above(*await self._collect_data(client, f_object))
