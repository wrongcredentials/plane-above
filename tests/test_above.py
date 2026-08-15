import pytest
import validators

from plane_above.models import State, FlyingObject

SUITE_BEL204_PHSFR = [
    [
        "44ccc8",
        "BEL204  ",
        "Belgium",
        1686539503,
        1686539503,
        4.5493,
        51.0993,
        899.16,
        False,
        93.76,
        156.39,
        0,
        None,
        1005.84,
        "1000",
        False,
        0,
        0,
    ],
    [
        "4864fa",
        "PHSFR   ",
        "Kingdom of the Netherlands",
        1686301664,
        1686301665,
        5.2843,
        51.5724,
        304.8,
        False,
        48.42,
        345.23,
        0.33,
        None,
        365.76,
        None,
        False,
        0,
    ],
]

SUITE_BBC305_ASL20K = [
    [
        "70209e",
        "BBC305  ",
        "Bangladesh",
        1686389405,
        1686389406,
        5.6401,
        52.3129,
        10972.8,
        False,
        245.67,
        299.89,
        0,
        None,
        11300.46,
        "3271",
        False,
        0,
        0,
    ],
    [
        "503cbf",
        "ASL20K  ",
        "Lithuania",
        1686389405,
        1686389406,
        4.8246,
        52.4818,
        2042.16,
        False,
        138.63,
        86.6,
        17.23,
        None,
        2171.7,
        "3157",
        False,
        0,
        0,
    ],
    [
        "405633",
        "EZY34TZ ",
        "United Kingdom",
        1687042343,
        1687042343,
        5.6231,
        50.8192,
        10972.8,
        True,
        210.37,
        287.5,
        -0.33,
        None,
        11300.46,
        "3110",
        False,
        0,
        1,
    ],
]


@pytest.mark.parametrize(
    "plane_above_mock",
    [SUITE_BEL204_PHSFR],
    indirect=True,
)
def test_sync_fetch(plane_above_mock):
    assert plane_above_mock.spotted.objects_raw == SUITE_BEL204_PHSFR
    assert plane_above_mock.spotted.objects_filtered == [
        FlyingObject(
            icao24="44ccc8",
            callsign="BEL204",
            country="Belgium",
            state=State(
                velocity=338,
                altitude=1006,
                latitude=51.0993,
                longitude=4.5493,
            ),
        ),
        FlyingObject(
            icao24="4864fa",
            callsign="PHSFR",
            country="Kingdom of the Netherlands",
            state=State(
                velocity=174,
                altitude=366,
                latitude=51.5724,
                longitude=5.2843,
            ),
        ),
    ]
    assert plane_above_mock.spotted.errors == []
    assert plane_above_mock.spotted.success is True
    assert plane_above_mock.spotted.how_many == 2
    for above in plane_above_mock.fetch():
        assert validators.url(above.photo.image_url) is True
        assert validators.url(above.photo.origin_url) is True
        assert len(above.route.stops) == 0
        assert any(above.aircraft.__dict__.values())
        assert any(above.route.__dict__.values())


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "plane_above_mock",
    [SUITE_BBC305_ASL20K],
    indirect=True,
)
async def test_async_fetch(plane_above_mock):
    assert plane_above_mock.spotted.objects_raw == SUITE_BBC305_ASL20K
    assert plane_above_mock.spotted.objects_filtered == [
        FlyingObject(
            icao24="70209e",
            callsign="BBC305",
            country="Bangladesh",
            state=State(
                velocity=884,
                altitude=11300,
                latitude=52.3129,
                longitude=5.6401,
            ),
        ),
        FlyingObject(
            icao24="503cbf",
            callsign="ASL20K",
            country="Lithuania",
            state=State(
                velocity=499,
                altitude=2172,
                latitude=52.4818,
                longitude=4.8246,
            ),
        ),
    ]
    assert plane_above_mock.spotted.errors == []
    assert plane_above_mock.spotted.success is True
    assert plane_above_mock.spotted.how_many == 2
    async for above in plane_above_mock.async_fetch():
        assert validators.url(above.photo.image_url) is True
        assert validators.url(above.photo.origin_url) is True
        assert all(above.route.departure.__dict__.values())
        assert all(above.route.destination.__dict__.values())
