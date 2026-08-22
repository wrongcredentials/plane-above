import os
import asyncio
import logging
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
IMAGE_CONTENT_TYPE = "image/jpeg"


async def hx_source(client: httpx.AsyncClient) -> tuple[str, bool]:
    name = "hexdb.io"
    hx = await async_get(client, AIRCRAFT_PHOTO_HX_SOURCE_URL, params=dict(hex=AIRCRAFT_ICAO))
    photo = await async_get(client, hx.data)
    status_check = photo.status_code == httpx.codes.OK
    content_check = photo.headers.get("content-type") == IMAGE_CONTENT_TYPE
    return name, status_check and content_check


async def sb_source(client: httpx.AsyncClient) -> tuple[str, bool]:
    name = "adsbdb.com"
    sb = await async_get(client, urljoin(AIRCRAFT_DETAILS_SB_SOURCE_URL, AIRCRAFT_ICAO))
    resp = sb.json_data.get("response", {}).get("aircraft", {})

    photo = await async_get(client, resp["url_photo_thumbnail"])
    photo_status_check = photo.status_code == httpx.codes.OK
    photo_content_check = photo.headers.get("content-type") == IMAGE_CONTENT_TYPE

    origin = await async_get(client, resp["url_photo"])  # noqa: F841
    # origin_status_check = origin.status_code == httpx.codes.OK FIXME: known issue; reported directly to adsbdb

    return name, photo_status_check and photo_content_check  # and origin_status_check


async def ad_source(client: httpx.AsyncClient) -> tuple[str, bool]:
    name = "airport-data.com"
    ad = await async_get(client, AIRCRAFT_PHOTO_AD_SOURCE_URL, params=dict(m=AIRCRAFT_ICAO, r=AIRCRAFT_REG))
    resp = ad.json_data.get("data", [])
    if len(resp) == 0:
        return name, False

    photo = await async_get(client, resp[0]["image"])
    photo_status_check = photo.status_code == httpx.codes.OK
    photo_content_check = photo.headers.get("content-type") == IMAGE_CONTENT_TYPE

    origin = await async_get(client, resp[0]["link"])
    origin_status_check = origin.status_code == httpx.codes.OK

    replace = await async_get(client, AircraftPhoto.make_ad_image_url(resp[0]["image"]))
    replace_status_check = replace.status_code == httpx.codes.OK

    return name, photo_status_check and photo_content_check and origin_status_check and replace_status_check


async def ps_source(client: httpx.AsyncClient) -> tuple[str, bool]:
    headers = {"User-Agent": os.environ["PS_USER_AGENT"]}
    name = "planespotters.net"
    ps = await async_get(
        client,
        urljoin(AIRCRAFT_PHOTO_PS_SOURCE_URL, f"reg/{AIRCRAFT_REG}"),
        headers=headers,
    )
    resp = ps.json_data.get("photos", [])
    if len(resp) == 0:
        return name, False

    photo = await async_get(client, resp[0]["thumbnail_large"]["src"], headers=headers)
    photo_status_check = photo.status_code == httpx.codes.OK
    photo_content_check = photo.headers.get("content-type") == IMAGE_CONTENT_TYPE

    origin = await async_get(client, resp[0]["link"], headers=headers)
    origin_status_check = origin.status_code == httpx.codes.OK

    return name, photo_status_check and photo_content_check and origin_status_check


async def fd_source(client: httpx.AsyncClient) -> tuple[str, bool]:
    name = "flightdb.net"
    fd = await async_get(client, AIRCRAFT_DETAILS_FD_SOURCE_URL, params=dict(modes=AIRCRAFT_ICAO))
    resp = AircraftDetails._parse_fd_source(fd.data)

    photo = await async_get(client, resp["fd_image_url"])
    photo_status_check = photo.status_code == httpx.codes.OK
    photo_content_check = photo.headers.get("content-type") == IMAGE_CONTENT_TYPE

    origin = await async_get(client, resp["fd_origin_url"])
    origin_status_check = origin.status_code == httpx.codes.OK

    return name, photo_status_check and photo_content_check and origin_status_check


async def main() -> int:
    async with httpx.AsyncClient() as client:
        try:
            result = await asyncio.gather(
                hx_source(client),
                sb_source(client),
                ad_source(client),
                ps_source(client),
                fd_source(client),
            )
        except Exception as e:
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
