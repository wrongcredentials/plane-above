from enum import Enum


class RouteSource(Enum):
    HX = "https://hexdb.io/"
    SB = "https://www.adsbdb.com/"


class PhotoSource(Enum):
    HX = "https://hexdb.io/"
    AD = "https://airport-data.com/terms"
    PS = "https://www.planespotters.net/photo/api#terms"
