import httpx
import pytest
from pytest_httpx import HTTPXMock

from plane_above.aircraft import Photo, AircraftPhoto

from . import (
    AD_PHOTO_URL,
    HX_PHOTO_URL,
    PS_HEX_PHOTO_URL,
    PS_REG_PHOTO_URL,
    AD_PHOTO_RESP_200,
    AD_PHOTO_RESP_404,
    AD_PHOTO_RESP_502,
    HX_PHOTO_RESP_200,
    HX_PHOTO_RESP_404,
    HX_PHOTO_RESP_502,
    PS_PHOTO_RESP_200,
    PS_PHOTO_RESP_404,
    PS_PHOTO_RESP_502,
)

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
async def test_ad_photo_source_ok(
    async_client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
    aircraft_icao: str,
    aircraft_registration: str,
):
    httpx_mock.add_response(url=AD_PHOTO_URL, **AD_PHOTO_RESP_200)
    photo = await AircraftPhoto._get_photo_from_ad(async_client, aircraft_icao, aircraft_registration)
    assert photo == PHOTO_AD


@pytest.mark.asyncio
async def test_hx_photo_source_ok(async_client: httpx.AsyncClient, httpx_mock: HTTPXMock, aircraft_icao: str):
    httpx_mock.add_response(url=HX_PHOTO_URL, **HX_PHOTO_RESP_200)
    photo = await AircraftPhoto._get_photo_from_hx(async_client, aircraft_icao)
    assert photo == PHOTO_HX


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("_url", "_by", "_item"),
    [(PS_HEX_PHOTO_URL, "hex", "aircraft_icao"), (PS_REG_PHOTO_URL, "reg", "aircraft_registration")],
)
async def test_ps_source_ok(
    _url: str,
    _by: str,
    _item: str,
    async_client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
    request,
):
    httpx_mock.add_response(url=_url, **PS_PHOTO_RESP_200)
    photo = await AircraftPhoto._get_photo_from_ps(async_client, _by, request.getfixturevalue(_item), "")
    assert photo == PHOTO_PS


@pytest.mark.asyncio
async def test_all_photo_sources_ok(
    async_client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
    aircraft_icao: str,
    aircraft_registration: str,
    ps_user_agent: str,
):
    httpx_mock.add_response(url=HX_PHOTO_URL, **HX_PHOTO_RESP_200)
    httpx_mock.add_response(url=AD_PHOTO_URL, **AD_PHOTO_RESP_200)
    httpx_mock.add_response(url=PS_HEX_PHOTO_URL, **PS_PHOTO_RESP_200)
    httpx_mock.add_response(url=PS_REG_PHOTO_URL, **PS_PHOTO_RESP_200)

    photo = await AircraftPhoto.get_photo(async_client, aircraft_icao, aircraft_registration, ps_user_agent)
    assert photo == PHOTO_HX


@pytest.mark.asyncio
async def test_all_photo_sources_empty(
    async_client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
    aircraft_icao: str,
    aircraft_registration: str,
    ps_user_agent: str,
):
    httpx_mock.add_response(url=HX_PHOTO_URL, **HX_PHOTO_RESP_404)
    httpx_mock.add_response(url=AD_PHOTO_URL, **AD_PHOTO_RESP_404)
    httpx_mock.add_response(url=PS_HEX_PHOTO_URL, **PS_PHOTO_RESP_404)
    httpx_mock.add_response(url=PS_REG_PHOTO_URL, **PS_PHOTO_RESP_404)

    photo = await AircraftPhoto.get_photo(async_client, aircraft_icao, aircraft_registration, ps_user_agent)
    assert photo == PHOTO_EMPTY


@pytest.mark.asyncio
async def test_all_photo_sources_unavailable(
    async_client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
    aircraft_icao: str,
    aircraft_registration: str,
    ps_user_agent: str,
):
    httpx_mock.add_response(url=HX_PHOTO_URL, **HX_PHOTO_RESP_502)
    httpx_mock.add_response(url=AD_PHOTO_URL, **AD_PHOTO_RESP_502)
    httpx_mock.add_response(url=PS_HEX_PHOTO_URL, **PS_PHOTO_RESP_502)
    httpx_mock.add_response(url=PS_REG_PHOTO_URL, **PS_PHOTO_RESP_502)

    photo = await AircraftPhoto.get_photo(async_client, aircraft_icao, aircraft_registration, ps_user_agent)

    assert photo == PHOTO_EMPTY


@pytest.mark.asyncio
async def test_hx_photo_source_empty(
    async_client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
    aircraft_icao: str,
    aircraft_registration: str,
    ps_user_agent: str,
):
    httpx_mock.add_response(url=HX_PHOTO_URL, **HX_PHOTO_RESP_404)
    httpx_mock.add_response(url=AD_PHOTO_URL, **AD_PHOTO_RESP_200)
    httpx_mock.add_response(url=PS_HEX_PHOTO_URL, **PS_PHOTO_RESP_200)
    httpx_mock.add_response(url=PS_REG_PHOTO_URL, **PS_PHOTO_RESP_200)

    photo = await AircraftPhoto.get_photo(async_client, aircraft_icao, aircraft_registration, ps_user_agent)

    assert photo == PHOTO_AD


@pytest.mark.asyncio
async def test_hx_ad_photo_sources_empty(
    async_client: httpx.AsyncClient,
    httpx_mock: HTTPXMock,
    aircraft_icao: str,
    aircraft_registration: str,
    ps_user_agent: str,
):
    httpx_mock.add_response(url=HX_PHOTO_URL, **HX_PHOTO_RESP_502)
    httpx_mock.add_response(url=AD_PHOTO_URL, **AD_PHOTO_RESP_404)
    httpx_mock.add_response(url=PS_HEX_PHOTO_URL, **PS_PHOTO_RESP_200)
    httpx_mock.add_response(url=PS_REG_PHOTO_URL, **PS_PHOTO_RESP_200)

    photo = await AircraftPhoto.get_photo(async_client, aircraft_icao, aircraft_registration, ps_user_agent)

    assert photo == PHOTO_PS
