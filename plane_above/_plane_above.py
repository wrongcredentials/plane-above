import asyncio
from collections.abc import Generator, Collection, AsyncGenerator

import httpx

from .osn import OSN
from .utils import PlaneAboveClient, log
from .flight import FlightRoute
from .models import Above, Photo, State, Flight, Airport, Spotted, Aircraft, FlyingObject
from .static import DEFAULT_DISTANCE_FROM_POINT, PhotoSource, RouteSource
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
        *,
        distance: float = DEFAULT_DISTANCE_FROM_POINT,
        osn_id: str = "",
        osn_secret: str = "",
        osn_proxy: str | None = None,
        ps_user_agent: str = "",
        route_sources: Collection[RouteSource] = (RouteSource.HX,),
        photo_sources: Collection[PhotoSource] = (PhotoSource.AD, PhotoSource.HX),
    ):
        """Initialize PlaneAbove client with search parameters and API credentials.

        Args:
            point: Geographic coordinates as (latitude, longitude).
            distance: Search radius in kilometers from the given point.
            osn_id: OpenSky Network API identifier.
            osn_secret: OpenSky Network API secret.
            osn_proxy: Proxy URL for OpenSky Network requests.
            route_sources: Route data sources to query, as a collection of
                `RouteSource` members e.g. (RouteSource.HX, RouteSource.SB).
                Sources not included here are skipped entirely. By including any
                source in this collection, you confirm that you have read and agree
                to the terms and restrictions that apply to it. See the "Sources"
                section in README.md for details.
            photo_sources: Photo data sources to query, as a collection of
                `PhotoSource` members e.g. (PhotoSource.AD, PhotoSource.HX).
                Sources not included here are skipped entirely. By including any
                source in this collection, you confirm that you have read and agree
                to the terms and restrictions that apply to it. See the "Sources"
                section in README.md for details.
            ps_user_agent: User-Agent string for planespotters.net API requests.
                If this parameter is not provided, this source will not be queried
                even if `PhotoSource.PS` is included in `photo_sources`. By providing
                a User-Agent, you confirm that you have read and agree to comply
                with planespotters.net's Terms of Use. See the "Sources" section
                in README.md for details.
        """
        self._route_sources = route_sources
        self._photo_sources = photo_sources
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
                    self._photo_sources,
                    self._ps_user_agent,
                ),
                FlightRoute.get_route(client, f_object.callsign, self._route_sources),
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
        async with PlaneAboveClient() as client:
            for f_object in self.spotted.objects_filtered:
                yield Above(*await self._collect_data(client, f_object))
