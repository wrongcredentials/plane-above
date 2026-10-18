import pytest

from tests.data import COORDINATES
from plane_above.osn import OSN


@pytest.mark.parametrize("point", [(-90, -180), (90, 180), (0, 0), (-89.999937, 179.0), (52.15, 25)])
def test_validate_coordinates_ok(point):
    latitude, longitude = point
    assert OSN._validate_coordinates(latitude, longitude)


@pytest.mark.parametrize(
    "point",
    [
        (-91, -180),
        (90, 181),
        (-90.523482, 180.012832),
        (100, 10.0),
    ],
)
def test_validate_coordinates_invalid(point):
    latitude, longitude = point
    with pytest.raises(ValueError, match=r"^Invalid coordinates\.$"):
        OSN._validate_coordinates(latitude, longitude)


@pytest.mark.parametrize(
    ("_distance", "_area"),
    [
        (
            10,
            {
                "lamax": 52.18338616059188,
                "lamin": 52.00352183940813,
                "lomax": 5.264663931644737,
                "lomin": 4.971904068355263,
            },
        ),
        (
            1,
            {
                "lamax": 52.10244721605919,
                "lamin": 52.08446078394081,
                "lomax": 5.132921983350318,
                "lomin": 5.103646016649683,
            },
        ),
        (
            15.02,
            {
                "lamax": 52.22853210520899,
                "lamin": 51.95837589479101,
                "lomax": 5.338146844347557,
                "lomin": 4.898421155652444,
            },
        ),
    ],
)
def test_calculate_area_distance_ok(_distance, _area):
    area = OSN._get_bounding_box(*COORDINATES, distance=_distance)
    assert area == _area


@pytest.mark.parametrize("_distance", [0, -1, "distance", None])
def test_calculate_area_distance_invalid(_distance):
    area = OSN._get_bounding_box(*COORDINATES, distance=_distance)
    assert area == {
        "lamax": 52.228352240887816,
        "lamin": 51.958555759112194,
        "lomax": 5.337854083342443,
        "lomin": 4.898713916657557,
    }
