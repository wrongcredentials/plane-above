from urllib.parse import urljoin

OPENSKY_AUTH_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"

OPENSKY_API_BASE_URL = "https://opensky-network.org/api/"
HEX_DB_API_BASE_URL = "https://hexdb.io/api/v1/"
AIRPORT_DATA_API_BASE_URL = "https://airport-data.com/api/"
ADSB_DB_API_BASE_URL = "https://api.adsbdb.com/v0/"

AIRCRAFT_IN_AREA_SOURCE_URL = urljoin(OPENSKY_API_BASE_URL, "states/all")

AIRCRAFT_DETAILS_HX_SOURCE_URL = urljoin(HEX_DB_API_BASE_URL, "aircraft/")
AIRCRAFT_DETAILS_FD_SOURCE_URL = "https://www.flightdb.net/aircraft.php"
AIRCRAFT_DETAILS_SB_SOURCE_URL = urljoin(ADSB_DB_API_BASE_URL, "aircraft/")

AIRCRAFT_PHOTO_PS_SOURCE_URL = "https://api.planespotters.net/pub/photos/"
AIRCRAFT_PHOTO_AD_SOURCE_URL = urljoin(AIRPORT_DATA_API_BASE_URL, "ac_thumb.json")
AIRCRAFT_PHOTO_AD_STATIC_URL = "https://image.airport-data.com/aircraft/"
AIRCRAFT_PHOTO_HX_SOURCE_URL = "https://hexdb.io/hex-image"

AIRPORT_DETAILS_HX_SOURCE_URL = urljoin(HEX_DB_API_BASE_URL, "airport/iata/")
AIRPORT_DETAILS_AD_SOURCE_URL = urljoin(AIRPORT_DATA_API_BASE_URL, "ap_info.json")

ROUTE_DETAILS_HX_SOURCE_URL = urljoin(HEX_DB_API_BASE_URL, "route/iata/")
ROUTE_DETAILS_SB_SOURCE_URL = urljoin(ADSB_DB_API_BASE_URL, "callsign/")
