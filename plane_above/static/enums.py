from enum import Enum


class DataSource(str, Enum):
    OPENSKY = OS = "opensky-network.org"  # https://opensky-network.org/about/terms-of-use
    HEX_DB = HX = "hexdb.io"  # https://hexdb.io/
    ADSB_DB = SB = "adsbdb.com"  # https://www.adsbdb.com/
    AIRPORT_DATA = AD = "airport-data.com"  # https://airport-data.com/terms
    PLANESPOTTERS = PS = "planespotters.net"  # https://www.planespotters.net/photo/api#terms
    FLIGHT_DB = FD = "flightdb.net"  # https://www.flightdb.net/faq.php

    def __str__(self) -> str:
        return self.value  # pragma: no cover


class RouteSource(Enum):
    HEX_DB = HX = DataSource.HX
    ADSB_DB = SB = DataSource.SB


class PhotoSource(Enum):
    HEX_DB = HX = DataSource.HX
    AIRPORT_DATA = AD = DataSource.AD
    PLANESPOTTERS = PS = DataSource.PS
