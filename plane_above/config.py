from dataclasses import dataclass
from collections.abc import Collection

from .utils import log
from .static import DataSource, PhotoSource, RouteSource


@dataclass(frozen=True, kw_only=True, slots=True)
class Config:
    """Configuration parameters for PlaneAbove.

    Attributes:
        route_sources: Route data sources to query, as a collection of `RouteSource` members
            e.g. (RouteSource.HEX_DB, RouteSource.ADSB_DB). Sources not included here are skipped entirely.
        photo_sources: Photo data sources to query, as a collection of `PhotoSource` members
            e.g. (PhotoSource.HEX_DB, PhotoSource.AIRPORT_DATA). Sources not included here are skipped entirely.
        user_agent: User-Agent string for API requests. If this parameter is not provided,
            planespotters.net source will not be queried even if `PhotoSource.PLANESPOTTERS`
            is included in `photo_sources`.
        proxy_url: Proxy URL for API calls, e.g. `"http://user:pass@host:8080"`
        proxy_scope: Sources whose requests go through `proxy_url` as a collection of `DataSource` members
            e.g. (DataSource.OPENSKY, DataSource.AIRPORT_DATA). Sources not included here are called directly.
        osn_id: OpenSky Network API identifier.
        osn_secret: OpenSky Network API secret.

    By including any source in `route_sources`, `photo_sources` and/or providing `user_agent` parameter,
    you confirm that you have read and agree to the terms and restrictions that applies to that source.
    See the "Sources" section in README.md for details.
    """

    route_sources: Collection[RouteSource] = (RouteSource.HX,)
    photo_sources: Collection[PhotoSource] = (PhotoSource.AD, PhotoSource.HX)
    user_agent: str = ""
    proxy_url: str | None = None
    proxy_scope: Collection[DataSource] | None = None
    osn_id: str = ""
    osn_secret: str = ""

    def __post_init__(self) -> None:  # pragma: no cover
        if not self.user_agent and PhotoSource.PS in self.photo_sources:
            log.warning(" ✈ No User-Agent detected; Planespotters.net requires a unique and descriptive value")
            photo_sources = tuple(s for s in self.photo_sources if s is not PhotoSource.PS)
            object.__setattr__(self, "photo_sources", photo_sources)
