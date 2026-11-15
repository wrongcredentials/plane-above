from enum import StrEnum


class DataSource(StrEnum):
    OPENSKY = OS = "opensky-network.org"  # https://opensky-network.org/about/terms-of-use
    HEX_DB = HX = "hexdb.io"  # https://hexdb.io/
    ADSB_DB = SB = "adsbdb.com"  # https://www.adsbdb.com/
    AIRPORT_DATA = AD = "airport-data.com"  # https://airport-data.com/terms
    PLANESPOTTERS = PS = "planespotters.net"  # https://www.planespotters.net/photo/api#terms
    FLIGHT_DB = FD = "flightdb.net"  # https://www.flightdb.net/faq.php


class RouteSource(StrEnum):
    HEX_DB = HX = DataSource.HX
    ADSB_DB = SB = DataSource.SB


class PhotoSource(StrEnum):
    HEX_DB = HX = DataSource.HX
    AIRPORT_DATA = AD = DataSource.AD
    PLANESPOTTERS = PS = DataSource.PS
