import os
import asyncio
import logging
from typing import Any
from urllib.parse import urljoin
from collections.abc import Callable, Coroutine

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

AIRCRAFT_ICAO = "06A07A"
AIRPORT_IATA = "ICN"
SOURCES: dict[str, Callable[[httpx.AsyncClient], Coroutine[Any, Any, httpx.Response]]] = {
    "opensky-network.org": lambda c: c.get(urljoin(OPENSKY_API_BASE_URL, "states/all")),
    "hexdb.io": lambda c: c.get(urljoin(AIRPORT_DETAILS_HX_SOURCE_URL, AIRPORT_IATA)),
    "adsbdb.com": lambda c: c.get(urljoin(ADSB_DB_API_BASE_URL, "online")),
    "airport-data.com": lambda c: c.get(AIRPORT_DETAILS_AD_SOURCE_URL, params={"iata": AIRPORT_IATA}),
    "flightdb.net": lambda c: c.get(AIRCRAFT_DETAILS_FD_SOURCE_URL, params={"modes": AIRCRAFT_ICAO}),
    "planespotters.net": lambda c: c.get(
        urljoin(AIRCRAFT_PHOTO_PS_SOURCE_URL, f"hex/{AIRCRAFT_ICAO}"),
        headers={"User-Agent": os.environ["PS_USER_AGENT"]},
    ),
}


async def main() -> int:
    async def _check_source(
        _client: httpx.AsyncClient,
        name: str,
        request: Callable[[httpx.AsyncClient], Coroutine[Any, Any, httpx.Response]],
    ) -> str | None:
        try:
            r = await request(_client)
            r.raise_for_status()
            return None
        except httpx.HTTPError as exc:
            return f"{name}: {exc}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        results = await asyncio.gather(*(_check_source(client, name, request) for name, request in SOURCES.items()))

    if failed_sources := [r for r in results if r is not None]:
        log.error("%d/%d sources failed: %s", len(failed_sources), len(SOURCES), ", ".join(failed_sources))
        return 1

    log.info("All %d sources passed", len(SOURCES))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(asyncio.run(main()))
