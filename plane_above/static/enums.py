from enum import Enum


class RouteSource(Enum):
    HX = "hexdb.io"
    SB = "adsbdb.com"


class PhotoSource(Enum):
    HX = "hexdb.io"
    AD = "airport-data.com"
    PS = "planespotters.net"
