from enum import Enum


class RouteSource(Enum):
    HX = "hexdb.io"  # https://hexdb.io/
    SB = "adsbdb.com"  # https://www.adsbdb.com/


class PhotoSource(Enum):
    HX = "hexdb.io"  # https://hexdb.io/
    AD = "airport-data.com"  # https://airport-data.com/terms
    PS = "planespotters.net"  # https://www.planespotters.net/photo/api#terms
