import os
import asyncio
import logging
from typing import Any
from urllib.parse import urljoin

import httpx

from plane_above.utils import async_get
from plane_above.aircraft import AircraftPhoto, AircraftDetails
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
        name = "hexdb.io"
        hx = await async_get(self.client, AIRCRAFT_PHOTO_HX_SOURCE_URL, params=dict(hex=AIRCRAFT_ICAO))
        photo = await async_get(self.client, hx.data)
        return name, self._statuses_check(photo.status_code) and self._content_check(photo.headers)

    async def sb_source(self) -> tuple[str, bool]:
        name = "adsbdb.com"
        sb = await async_get(self.client, urljoin(AIRCRAFT_DETAILS_SB_SOURCE_URL, AIRCRAFT_ICAO))
        resp = sb.json_data.get("response", {}).get("aircraft", {})

        photo = await async_get(self.client, resp["url_photo_thumbnail"])
        origin = await async_get(self.client, resp["url_photo"])  # noqa: F841
        # FIXME: known issue; reported directly to adsbdb: https://github.com/mrjackwills/adsbdb/issues/92

        return name, self._statuses_check(photo.status_code) and self._content_check(photo.headers)

    async def ad_source(self) -> tuple[str, bool]:
        name = "airport-data.com"
        ad = await async_get(self.client, AIRCRAFT_PHOTO_AD_SOURCE_URL, params=dict(m=AIRCRAFT_ICAO, r=AIRCRAFT_REG))
        resp = ad.json_data.get("data", [])
        if len(resp) == 0:
            return name, False

        photo = await async_get(self.client, resp[0]["image"])
        origin = await async_get(self.client, resp[0]["link"])
        replace = await async_get(self.client, AircraftPhoto.make_ad_image_url(resp[0]["image"]))

        return name, self._statuses_check(
            photo.status_code, origin.status_code, replace.status_code
        ) and self._content_check(photo.headers) and self._content_check(replace.headers)

    async def ps_source(self) -> tuple[str, bool]:
        headers = {"User-Agent": os.environ["PS_USER_AGENT"]}
        name = "planespotters.net"
        ps = await async_get(
            self.client,
            urljoin(AIRCRAFT_PHOTO_PS_SOURCE_URL, f"reg/{AIRCRAFT_REG}"),
            headers=headers,
        )
        resp = ps.json_data.get("photos", [])
        if len(resp) == 0:
            return name, False

        photo = await async_get(self.client, resp[0]["thumbnail_large"]["src"], headers=headers)
        origin = await async_get(self.client, resp[0]["link"], headers=headers)

        return name, self._statuses_check(photo.status_code, origin.status_code) and self._content_check(photo.headers)

    async def fd_source(self) -> tuple[str, bool]:
        name = "flightdb.net"
        fd = await async_get(self.client, AIRCRAFT_DETAILS_FD_SOURCE_URL, params=dict(modes=AIRCRAFT_ICAO))
        resp = AircraftDetails._parse_fd_source(fd.data)

        photo = await async_get(self.client, resp["fd_image_url"])
        origin = await async_get(self.client, resp["fd_origin_url"])

        return name, self._statuses_check(photo.status_code, origin.status_code) and self._content_check(photo.headers)


async def main() -> int:
    async with httpx.AsyncClient() as client:
        try:
            check = PhotoCheck(client)
            result = await asyncio.gather(
                check.hx_source(),
                check.sb_source(),
                check.ad_source(),
                check.ps_source(),
                check.fd_source(),
            )
        except Exception as e:  # noqa: BLE001
            log.error("Exception occurred: %s", e)
            return 1
        else:
            if failed_sources := [source[0] for source in result if source[1] is False]:
                log.error("%d/%d sources failed: %s", len(failed_sources), len(result), ", ".join(failed_sources))
                return 1

            log.info("All %d sources passed", len(result))
            return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(asyncio.run(main()))
