import httpx
import pytest
from pytest_httpx import HTTPXMock

from tests import PhotoMocks
from tests.data import AIRCRAFT_REG, AIRCRAFT_ICAO
from plane_above.static import PhotoSource
from plane_above.aircraft import Photo, AircraftPhoto

PHOTO_HX = Photo(
    image_url="https://hexdb.io/static/aircraft-images/PH-BXC.jpg",
    origin_url="https://hexdb.io/static/aircraft-images/PH-BXC.jpg",
    photographer="",
)
PHOTO_AD = Photo(
    image_url="https://image.airport-data.com/aircraft/001744757.jpg",
    origin_url="https://airport-data.com/aircraft/photo/001744757",
    photographer="Guy with a camera",
)
PHOTO_PS = Photo(
    image_url="https://t.plnspttrs.net/45207/1439864_c8394801ac_280.jpg",
    origin_url="https://www.planespotters.net/photo/1439864/n2534u-united-airlines-boeing-777-322er",
    photographer="Guy with a camera",
)
PHOTO_EMPTY = Photo(image_url="", origin_url="", photographer="")


@pytest.mark.asyncio
async def test_ad_photo_source_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=PhotoMocks.AD_PHOTO_URL, **PhotoMocks.AD_PHOTO_RESP_200)
    photo = await AircraftPhoto._get_photo_from_ad(async_client, AIRCRAFT_ICAO, AIRCRAFT_REG)
    assert photo == PHOTO_AD


@pytest.mark.asyncio
async def test_hx_photo_source_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=PhotoMocks.HX_PHOTO_URL, **PhotoMocks.HX_PHOTO_RESP_200)
    photo = await AircraftPhoto._get_photo_from_hx(async_client, AIRCRAFT_ICAO)
    assert photo == PHOTO_HX


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("_url", "_by", "_item"),
    [(PhotoMocks.PS_HEX_PHOTO_URL, "hex", AIRCRAFT_ICAO), (PhotoMocks.PS_REG_PHOTO_URL, "reg", AIRCRAFT_REG)],
)
async def test_ps_source_ok(
    _url: str,
    _by: str,
    _item: str,
    async_client: httpx.AsyncClient,
    ps_user_agent: str,
    httpx_mock: HTTPXMock,
):
    httpx_mock.add_response(url=_url, **PhotoMocks.PS_PHOTO_RESP_200)
    photo = await AircraftPhoto._get_photo_from_ps(async_client, _by, _item, ps_user_agent)
    assert photo == PHOTO_PS


@pytest.mark.asyncio
async def test_all_photo_sources_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, ps_user_agent: str):
    httpx_mock.add_response(url=PhotoMocks.HX_PHOTO_URL, **PhotoMocks.HX_PHOTO_RESP_200)
    httpx_mock.add_response(url=PhotoMocks.AD_PHOTO_URL, **PhotoMocks.AD_PHOTO_RESP_200)
    httpx_mock.add_response(url=PhotoMocks.PS_HEX_PHOTO_URL, **PhotoMocks.PS_PHOTO_RESP_200)
    httpx_mock.add_response(url=PhotoMocks.PS_REG_PHOTO_URL, **PhotoMocks.PS_PHOTO_RESP_200)

    photos = await AircraftPhoto.get_photos(
        async_client, AIRCRAFT_ICAO, AIRCRAFT_REG, (PhotoSource.HX, PhotoSource.AD, PhotoSource.PS), ps_user_agent
    )
    assert photos == [PHOTO_HX, PHOTO_AD, PHOTO_PS]


@pytest.mark.asyncio
async def test_all_photo_sources_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, ps_user_agent: str):
    httpx_mock.add_response(url=PhotoMocks.HX_PHOTO_URL, **PhotoMocks.HX_PHOTO_RESP_404)
    httpx_mock.add_response(url=PhotoMocks.AD_PHOTO_URL, **PhotoMocks.AD_PHOTO_RESP_404)
    httpx_mock.add_response(url=PhotoMocks.PS_HEX_PHOTO_URL, **PhotoMocks.PS_PHOTO_RESP_404)
    httpx_mock.add_response(url=PhotoMocks.PS_REG_PHOTO_URL, **PhotoMocks.PS_PHOTO_RESP_404)

    photos = await AircraftPhoto.get_photos(
        async_client, AIRCRAFT_ICAO, AIRCRAFT_REG, (PhotoSource.HX, PhotoSource.AD, PhotoSource.PS), ps_user_agent
    )
    assert photos == [PHOTO_EMPTY]


@pytest.mark.asyncio
async def test_all_photo_sources_unavailable(
    async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, ps_user_agent: str
):
    httpx_mock.add_response(url=PhotoMocks.HX_PHOTO_URL, **PhotoMocks.HX_PHOTO_RESP_502)
    httpx_mock.add_response(url=PhotoMocks.AD_PHOTO_URL, **PhotoMocks.AD_PHOTO_RESP_502)
    httpx_mock.add_response(url=PhotoMocks.PS_HEX_PHOTO_URL, **PhotoMocks.PS_PHOTO_RESP_502)
    httpx_mock.add_response(url=PhotoMocks.PS_REG_PHOTO_URL, **PhotoMocks.PS_PHOTO_RESP_502)

    photos = await AircraftPhoto.get_photos(
        async_client, AIRCRAFT_ICAO, AIRCRAFT_REG, (PhotoSource.HX, PhotoSource.AD, PhotoSource.PS), ps_user_agent
    )

    assert photos == [PHOTO_EMPTY]


@pytest.mark.asyncio
async def test_hx_photo_source_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, ps_user_agent: str):
    httpx_mock.add_response(url=PhotoMocks.HX_PHOTO_URL, **PhotoMocks.HX_PHOTO_RESP_404)
    httpx_mock.add_response(url=PhotoMocks.AD_PHOTO_URL, **PhotoMocks.AD_PHOTO_RESP_200)
    httpx_mock.add_response(url=PhotoMocks.PS_HEX_PHOTO_URL, **PhotoMocks.PS_PHOTO_RESP_200)
    httpx_mock.add_response(url=PhotoMocks.PS_REG_PHOTO_URL, **PhotoMocks.PS_PHOTO_RESP_200)

    photos = await AircraftPhoto.get_photos(
        async_client, AIRCRAFT_ICAO, AIRCRAFT_REG, (PhotoSource.HX, PhotoSource.AD, PhotoSource.PS), ps_user_agent
    )

    assert photos == [PHOTO_AD, PHOTO_PS]


@pytest.mark.asyncio
async def test_hx_ad_photo_sources_empty(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, ps_user_agent: str):
    httpx_mock.add_response(url=PhotoMocks.HX_PHOTO_URL, **PhotoMocks.HX_PHOTO_RESP_502)
    httpx_mock.add_response(url=PhotoMocks.AD_PHOTO_URL, **PhotoMocks.AD_PHOTO_RESP_404)
    httpx_mock.add_response(url=PhotoMocks.PS_HEX_PHOTO_URL, **PhotoMocks.PS_PHOTO_RESP_200)
    httpx_mock.add_response(url=PhotoMocks.PS_REG_PHOTO_URL, **PhotoMocks.PS_PHOTO_RESP_200)

    photos = await AircraftPhoto.get_photos(
        async_client, AIRCRAFT_ICAO, AIRCRAFT_REG, (PhotoSource.HX, PhotoSource.AD, PhotoSource.PS), ps_user_agent
    )

    assert photos == [PHOTO_PS]


@pytest.mark.asyncio
async def test_ad_photo_source_requested(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, ps_user_agent: str):
    httpx_mock.add_response(url=PhotoMocks.AD_PHOTO_URL, **PhotoMocks.AD_PHOTO_RESP_200)

    photos = await AircraftPhoto.get_photos(async_client, AIRCRAFT_ICAO, AIRCRAFT_REG, (PhotoSource.AD,), ps_user_agent)

    assert photos == [PHOTO_AD]


@pytest.mark.asyncio
async def test_hx_and_ad_photo_source_requested(
    async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, ps_user_agent: str
):
    httpx_mock.add_response(url=PhotoMocks.HX_PHOTO_URL, **PhotoMocks.HX_PHOTO_RESP_200)
    httpx_mock.add_response(url=PhotoMocks.AD_PHOTO_URL, **PhotoMocks.AD_PHOTO_RESP_502)

    photos = await AircraftPhoto.get_photos(
        async_client, AIRCRAFT_ICAO, AIRCRAFT_REG, (PhotoSource.AD, PhotoSource.HX), ps_user_agent
    )

    assert photos == [PHOTO_HX]


@pytest.mark.asyncio
async def test_no_photo_sources_requested(async_client: httpx.AsyncClient, ps_user_agent: str):
    photos = await AircraftPhoto.get_photos(async_client, AIRCRAFT_ICAO, AIRCRAFT_REG, {}, ps_user_agent)

    assert photos == [PHOTO_EMPTY]
