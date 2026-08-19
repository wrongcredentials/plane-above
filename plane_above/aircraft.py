import asyncio
from datetime import date, datetime
from collections import ChainMap
from urllib.parse import urljoin
from collections.abc import Collection

import httpx
from lxml import html
from dateutil.relativedelta import relativedelta

from .utils import HttpResult, log, async_get
from .models import Photo, Aircraft
from .static import (
    AIRCRAFT_PHOTO_AD_SOURCE_URL,
    AIRCRAFT_PHOTO_AD_STATIC_URL,
    AIRCRAFT_PHOTO_HX_SOURCE_URL,
    AIRCRAFT_PHOTO_PS_SOURCE_URL,
    AIRCRAFT_DETAILS_FD_SOURCE_URL,
    AIRCRAFT_DETAILS_HX_SOURCE_URL,
    AIRCRAFT_DETAILS_SB_SOURCE_URL,
    PhotoSource,
)


class AircraftDetails:
    @staticmethod
    def _parse_fd_source(html_text: str) -> dict:
        if not html_text:
            return {}
        tree = html.fromstring(html_text)
        row = tree.xpath("//table[contains(@class, 'table')]/tbody/tr[th[@scope='row']][1]")
        if not row:
            return {}

        row = row[0]
        image_url = row.xpath(".//td[1]//img/@src")
        origin_url = row.xpath(".//td[1]//a/@href")
        registration = row.xpath("./td[2]/text()")
        aircraft_type = row.xpath("./td[3]/text()[normalize-space()][1]")
        owner = row.xpath("./td[5]/text()[normalize-space()][1]")
        year_built = row.xpath("./td[7]/text()")

        aircraft_type = aircraft_type[0].strip().rstrip("(").strip()
        if aircraft_type:
            parts = aircraft_type.split(maxsplit=1)
            manufacturer = parts[0]
            model = parts[1] if len(parts) > 1 else None
        else:
            manufacturer = model = None

        return {
            "fd_image_url": image_url[0].strip() if image_url else None,
            "fd_origin_url": origin_url[0].strip() if origin_url else None,
            "fd_registration": registration[0].strip() if registration else None,
            "fd_manufacturer": manufacturer,
            "fd_model": model,
            "fd_owner": owner[0].strip().rstrip("(").strip() if owner else None,
            "fd_year_built": year_built[0].strip() if year_built else None,
        }

    @staticmethod
    def _parse_sb_source(result: HttpResult) -> dict:
        if result.status_code == httpx.codes.NOT_FOUND or not result.json_data:
            return {}

        return result.json_data.get("response", {}).get("aircraft", {})  # type: ignore[no-any-return]

    @classmethod
    async def get_details(
        cls,
        _client: httpx.AsyncClient,
        icao24: str,
        country: str,
        sources: Collection[PhotoSource],
        ps_user_agent: str = "",
    ) -> Aircraft:
        results = await asyncio.gather(
            async_get(_client, AIRCRAFT_DETAILS_FD_SOURCE_URL, params=dict(modes=icao24)),
            async_get(_client, urljoin(AIRCRAFT_DETAILS_HX_SOURCE_URL, icao24)),
            async_get(_client, urljoin(AIRCRAFT_DETAILS_SB_SOURCE_URL, icao24)),
        )
        data = dict(
            ChainMap(
                cls._parse_fd_source(results[0].data),
                results[1].json_data,
                cls._parse_sb_source(results[2]),
            )
        )

        def pick_from(fields: tuple) -> str:
            return values[0] if (values := [v for f in fields if (v := data.get(f))]) else ""

        def get_age_from(year_built: str | None) -> float:
            if not year_built:
                return 0.0

            try:
                relative_age = relativedelta(date.today(), datetime.strptime(year_built, "%Y"))
                age = round(relative_age.years + relative_age.months / 12.0, ndigits=1)
                return age if age > 0 else 0.0

            except (ValueError, TypeError):
                log.error(f" ✈ Cannot parse plane age for {icao24}: {year_built}.")
                return 0.0

        ac_details: dict[str, str] = dict(
            registration=pick_from(("Registration", "registration", "fd_registration")),
            manufacturer=pick_from(("Manufacturer", "manufacturer", "fd_manufacturer")),
            model=pick_from(("Type", "type", "fd_model")),
            type_code=pick_from(("ICAOTypeCode", "icao_type")),  # TODO: add from fd source
            operator=pick_from(("RegisteredOwners", "registered_owner", "fd_owner")),
        )
        fd_photo = Photo(
            image_url=AircraftPhoto.make_ad_image_url(data.get("fd_image_url")),
            origin_url=data.get("fd_origin_url") or "",
        )
        sb_photo = Photo(
            image_url=AircraftPhoto.make_ad_image_url(data.get("url_photo_thumbnail")),
            origin_url="",  # FIXME sb source returns broken url in 'url_photo'
        )

        if fd_photo.has_urls:
            photos = [fd_photo]
        elif sb_photo.has_urls:
            photos = [sb_photo]
        elif not sources:
            photos = [Photo()]
        else:
            photos = await AircraftPhoto.get_photos(_client, icao24, ac_details["registration"], sources, ps_user_agent)

        return Aircraft(
            icao24=icao24,
            age=get_age_from(data.get("fd_year_built")),
            country=country,
            photos=photos,
            **ac_details,
        )


class AircraftPhoto:
    @staticmethod
    async def _get_photo_from_hx(_client: httpx.AsyncClient, icao24: str) -> Photo | None:
        result = await async_get(_client, AIRCRAFT_PHOTO_HX_SOURCE_URL, params=dict(hex=icao24))
        if result.status_code != httpx.codes.NOT_FOUND and result.data:
            return Photo(image_url=result.data, origin_url=result.data)
        return None

    @staticmethod
    async def _get_photo_from_ps(_client: httpx.AsyncClient, by: str, item: str, user_agent: str) -> Photo | None:
        if not user_agent:
            log.warning(" ✈ No User-Agent detected; Planespotters.net requires a unique and descriptive value")
            return None

        result = await async_get(
            _client,
            urljoin(AIRCRAFT_PHOTO_PS_SOURCE_URL, f"{by}/{item}"),
            headers={"User-Agent": user_agent},
        )

        if photos := result.json_data.get("photos"):
            photo = photos[0]
            return Photo(
                image_url=photo["thumbnail_large"]["src"],
                origin_url=photo["link"],
                photographer=photo["photographer"],
            )
        return None

    @staticmethod
    def make_ad_image_url(image_url: str | None) -> str:
        if not image_url:
            return ""

        filename = image_url.rsplit("/", maxsplit=1)[-1]
        return urljoin(AIRCRAFT_PHOTO_AD_STATIC_URL, filename)

    @classmethod
    async def _get_photo_from_ad(cls, _client: httpx.AsyncClient, icao24: str, registration: str) -> Photo | None:
        result = await async_get(_client, AIRCRAFT_PHOTO_AD_SOURCE_URL, params=dict(m=icao24, r=registration))
        if photos := result.json_data.get("data"):
            photo = photos[0]
            return Photo(
                image_url=cls.make_ad_image_url(photo.get("image")),
                origin_url=photo.get("link"),
                photographer=photo.get("photographer"),
            )
        return None

    @classmethod
    async def get_photos(
        cls,
        _client: httpx.AsyncClient,
        icao24: str,
        registration: str,
        sources: Collection[PhotoSource],
        ps_user_agent: str,
    ) -> list[Photo]:
        tasks: dict[PhotoSource, list] = {
            PhotoSource.HX: [lambda: cls._get_photo_from_hx(_client, icao24)],
            PhotoSource.AD: [lambda: cls._get_photo_from_ad(_client, icao24, registration)],
            PhotoSource.PS: [
                lambda: cls._get_photo_from_ps(_client, "hex", icao24, ps_user_agent),
                lambda: cls._get_photo_from_ps(_client, "reg", registration, ps_user_agent),
            ],
        }

        results = await asyncio.gather(*[task() for source in sources for task in tasks.get(source, [])])
        photos: dict[str, Photo] = {photo.image_url: photo for photo in results if photo is not None and photo.has_urls}
        return list(photos.values()) or [Photo()]
