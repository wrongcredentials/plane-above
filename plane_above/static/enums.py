from enum import Enum


class Source(str, Enum):
    OS = "opensky-network.org"  # https://opensky-network.org/about/terms-of-use
    HX = "hexdb.io"  # https://hexdb.io/
    SB = "adsbdb.com"  # https://www.adsbdb.com/
    AD = "airport-data.com"  # https://airport-data.com/terms
    PS = "planespotters.net"  # https://www.planespotters.net/photo/api#terms
    FD = "flightdb.net"  # https://www.flightdb.net/faq.php

    def __str__(self) -> str:
        return self.value


class RouteSource(Enum):
    HX = Source.HX
    SB = Source.SB


class PhotoSource(Enum):
    HX = Source.HX
    AD = Source.AD
    PS = Source.PS
