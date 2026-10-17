import asyncio
import logging
from typing import Any
from urllib.parse import urljoin

import httpx
from common import HEADERS, PROXY_MOUNTS

from plane_above.utils import async_get
from plane_above.aircraft import AircraftPhoto, AircraftDetails
from plane_above.static.enums import Source
from plane_above.static.sources import (
    AIRCRAFT_PHOTO_AD_SOURCE_URL,
    AIRCRAFT_PHOTO_HX_SOURCE_URL,
    AIRCRAFT_PHOTO_PS_SOURCE_URL,
    AIRCRAFT_DETAILS_FD_SOURCE_URL,
    AIRCRAFT_DETAILS_SB_SOURCE_URL,
)

log = logging.getLogger(__name__)
AIRCRAFT_ICAO = "3950CE"
AIRCRAFT_REG = "F-GUGO"


class PhotoCheck:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    @staticmethod
    def _statuses_check(*args: int) -> bool:
        return all(s == httpx.codes.OK for s in args)

    @staticmethod
    def _content_check(headers: dict[Any, Any]) -> bool:
        return "image/jpeg" in headers.get("content-type", "")

    async def hx_source(self) -> tuple[str, bool]:
        name = Source.HX
        hx = await async_get(self.client, AIRCRAFT_PHOTO_HX_SOURCE_URL, params=dict(hex=AIRCRAFT_ICAO))
        photo = await async_get(self.client, hx.data)
        return name, self._statuses_check(photo.status_code) and self._content_check(photo.headers)

    async def sb_source(self) -> tuple[str, bool]:
        name = Source.SB
        sb = await async_get(self.client, urljoin(AIRCRAFT_DETAILS_SB_SOURCE_URL, AIRCRAFT_ICAO))
        resp = sb.json_data.get("response", {}).get("aircraft", {})

        photo = await async_get(self.client, resp["url_photo_thumbnail"], headers=HEADERS)
        origin = await async_get(self.client, resp["url_photo"], headers=HEADERS)

        return name, self._statuses_check(photo.status_code, origin.status_code) and self._content_check(photo.headers)

    async def ad_source(self) -> tuple[str, bool]:
        name = Source.AD
        ad = await async_get(
            self.client,
            AIRCRAFT_PHOTO_AD_SOURCE_URL,
            headers=HEADERS,
            params=dict(m=AIRCRAFT_ICAO, r=AIRCRAFT_REG),
        )
        resp = ad.json_data.get("data", [])
        if len(resp) == 0:
            return name, False

        photo = await async_get(self.client, resp[0]["image"], headers=HEADERS)
        origin = await async_get(self.client, resp[0]["link"], headers=HEADERS)
        replace = await async_get(self.client, AircraftPhoto.make_ad_image_url(resp[0]["image"]))

        return name, self._statuses_check(
            photo.status_code, origin.status_code, replace.status_code
        ) and self._content_check(photo.headers) and self._content_check(replace.headers)

    async def ps_source(self) -> tuple[str, bool]:
        name = Source.PS
        ps = await async_get(
            self.client,
            urljoin(AIRCRAFT_PHOTO_PS_SOURCE_URL, f"reg/{AIRCRAFT_REG}"),
            headers=HEADERS,
        )
        resp = ps.json_data.get("photos", [])
        if len(resp) == 0:
            return name, False

        photo = await async_get(self.client, resp[0]["thumbnail_large"]["src"], headers=HEADERS)
        origin = await async_get(self.client, resp[0]["link"], headers=HEADERS)  # noqa: F841

        return name, self._statuses_check(photo.status_code) and self._content_check(photo.headers)

    async def fd_source(self) -> tuple[str, bool]:
        name = Source.FD
        fd = await async_get(self.client, AIRCRAFT_DETAILS_FD_SOURCE_URL, params=dict(modes=AIRCRAFT_ICAO))
        resp = AircraftDetails._parse_fd_source(fd.data)

        photo = await async_get(self.client, resp["fd_image_url"], headers=HEADERS)
        origin = await async_get(self.client, resp["fd_origin_url"], headers=HEADERS)

        return name, self._statuses_check(photo.status_code, origin.status_code) and self._content_check(photo.headers)


async def main() -> int:
    async with httpx.AsyncClient(timeout=10.0, mounts=PROXY_MOUNTS) as client:
        check = PhotoCheck(client)
        checks = {
            Source.HX: check.hx_source,
            Source.SB: check.sb_source,
            Source.AD: check.ad_source,
            Source.PS: check.ps_source,
            Source.FD: check.fd_source,
        }
        results = await asyncio.gather(*(c() for c in checks.values()), return_exceptions=True)

    failures = {}
    for source, r in zip(checks, results):
        if isinstance(r, BaseException):
            failures[source] = f"{type(r).__name__}: {r}"
        elif r[1] is not True:
            failures[source] = "check failed"

    if not failures:
        log.info("All %d sources passed", len(checks))
        return 0

    log.error(
        "%d/%d sources failed: %s",
        len(failures),
        len(checks),
        "; ".join(f"{source}: {reason}" for source, reason in failures.items()),
    )
    return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(asyncio.run(main()))
