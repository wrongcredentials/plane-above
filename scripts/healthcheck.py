import os
import logging
from urllib.parse import urljoin
from collections.abc import Callable

import httpx

from plane_above.static.sources import (
    ADSB_DB_API_BASE_URL,
    OPENSKY_API_BASE_URL,
    AIRCRAFT_PHOTO_PS_SOURCE_URL,
    AIRPORT_DETAILS_AD_SOURCE_URL,
    AIRPORT_DETAILS_HX_SOURCE_URL,
    AIRCRAFT_DETAILS_FD_SOURCE_URL,
)

log = logging.getLogger(__name__)

SOURCES: dict[str, Callable[[httpx.Client], httpx.Response]] = {
    "opensky-network.org": lambda c: c.get(urljoin(OPENSKY_API_BASE_URL, "states/all")),
    "hexdb.io": lambda c: c.get(urljoin(AIRPORT_DETAILS_HX_SOURCE_URL, "ICN")),
    "adsbdb.com": lambda c: c.get(urljoin(ADSB_DB_API_BASE_URL, "online")),
    "airport-data.com": lambda c: c.get(AIRPORT_DETAILS_AD_SOURCE_URL, params={"iata": "ICN"}),
    "flightdb.net": lambda client: client.get(AIRCRAFT_DETAILS_FD_SOURCE_URL, params={"modes": "06A07A"}),
    "planespotters.net": lambda c: c.get(
        urljoin(AIRCRAFT_PHOTO_PS_SOURCE_URL, "hex/06A07A"),
        headers={"User-Agent": os.environ["PS_USER_AGENT"]},
    ),
}


def main() -> int:
    failed_sources = []

    with httpx.Client(timeout=10.0) as client:
        for name, request in SOURCES.items():
            try:
                r = request(client)
                r.raise_for_status()
            except httpx.HTTPError as exc:
                failed_sources.append(f"{name}: {exc}")

    if failed_sources:
        log.error("%d/%d sources failed: %s", len(failed_sources), len(SOURCES), ", ".join(failed_sources))
        return 1

    log.info("All %d sources passed", len(SOURCES))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
