import json
from urllib.parse import urljoin

from plane_above.static import sources

AIRCRAFT_ICAO = "abcde0"
AIRCRAFT_REG = "AB-CDE"
FLIGHT_CALLSIGN = "ABC123DE"
AIRPORT_DEPARTURE_IATA = "DEP"
AIRPORT_DESTINATION_IATA = "DST"
AIRPORT_MIDPOINT_IATA = "MID"


def _load_json(path: str):
    with open(path) as f:
        return json.load(f)


def _load_html(path: str):
    with open(path) as f:
        return f.read()


HEADER_HTML = {"Content-Type": "text/html; charset=utf-8"}
HEADER_JSON = {"Content-Type": "application/json; charset=utf-8"}

SB_AIRCRAFT_URL = urljoin(sources.AIRCRAFT_DETAILS_SB_SOURCE_URL, AIRCRAFT_ICAO)
HX_AIRCRAFT_URL = urljoin(sources.AIRCRAFT_DETAILS_HX_SOURCE_URL, AIRCRAFT_ICAO)
FD_AIRCRAFT_URL = urljoin(sources.AIRCRAFT_DETAILS_FD_SOURCE_URL, f"?modes={AIRCRAFT_ICAO}")

SB_AIRCRAFT_RESP_200 = {"status_code": 200, "json": _load_json("tests/data/aircraft/aircraft_sb.json"), "headers": HEADER_JSON}
SB_AIRCRAFT_RESP_404 = {"status_code": 404, "json": {"response": "unknown aircraft"}, "headers": HEADER_JSON}
SB_AIRCRAFT_RESP_502 = {"status_code": 502, "json": {}}
HX_AIRCRAFT_RESP_200 = {"status_code": 200, "json": _load_json("tests/data/aircraft/aircraft_hx.json"), "headers": HEADER_JSON}
HX_AIRCRAFT_RESP_404 = {"status_code": 404, "json": {"status": "404", "error": "Aircraft not found."}, "headers": HEADER_JSON}
HX_AIRCRAFT_RESP_502 = {"status_code": 502, "json": {}}
FD_AIRCRAFT_RESP_200 = {"status_code": 200, "text": _load_html("tests/data/aircraft/aircraft_fd.html"), "headers": HEADER_HTML}
FD_AIRCRAFT_RESP_404 = {"status_code": 200, "text": _load_html("tests/data/aircraft/aircraft_fd_empty.html"), "headers": HEADER_HTML}
FD_AIRCRAFT_RESP_502 = {"status_code": 502, "text": ""}

AD_PHOTO_URL = urljoin(sources.AIRCRAFT_PHOTO_AD_SOURCE_URL, f"?m={AIRCRAFT_ICAO}&r={AIRCRAFT_REG}")
HX_PHOTO_URL = urljoin(sources.AIRCRAFT_PHOTO_HX_SOURCE_URL, f"?hex={AIRCRAFT_ICAO}")
PS_HEX_PHOTO_URL = urljoin(sources.AIRCRAFT_PHOTO_PS_SOURCE_URL, f"hex/{AIRCRAFT_ICAO}")
PS_REG_PHOTO_URL = urljoin(sources.AIRCRAFT_PHOTO_PS_SOURCE_URL, f"reg/{AIRCRAFT_REG}")

AD_PHOTO_RESP_200 = {"status_code": 200, "json": _load_json("tests/data/aircraft/photo_ad.json"), "headers": HEADER_JSON}
AD_PHOTO_RESP_404 = {"status_code": 404, "json": {}, "headers": HEADER_JSON}
AD_PHOTO_RESP_502 = {"status_code": 502, "json": {}}
HX_PHOTO_RESP_200 = {"status_code": 200, "text": "https://hexdb.io/static/aircraft-images/PH-BXC.jpg", "headers": HEADER_HTML}
HX_PHOTO_RESP_404 = {"status_code": 404, "text": "n/a", "headers": HEADER_HTML}
HX_PHOTO_RESP_502 = {"status_code": 502, "text": ""}
PS_PHOTO_RESP_200 = {"status_code": 200, "json": _load_json("tests/data/aircraft/photo_ps.json"), "headers": HEADER_JSON}
PS_PHOTO_RESP_404 = {"status_code": 404, "json": {"photos": []}, "headers": HEADER_JSON}
PS_PHOTO_RESP_502 = {"status_code": 502, "json": {"error": "Hex invalid or missing"}, "headers": HEADER_JSON}

HX_ROUTE_URL = urljoin(sources.ROUTE_DETAILS_HX_SOURCE_URL, FLIGHT_CALLSIGN)
SB_ROUTE_URL = urljoin(sources.ROUTE_DETAILS_SB_SOURCE_URL, FLIGHT_CALLSIGN)
HX_DEP_AIRPORT_URL = urljoin(sources.AIRPORT_DETAILS_HX_SOURCE_URL, AIRPORT_DEPARTURE_IATA)
HX_DST_AIRPORT_URL = urljoin(sources.AIRPORT_DETAILS_HX_SOURCE_URL, AIRPORT_DESTINATION_IATA)
HX_MID_AIRPORT_URL = urljoin(sources.AIRPORT_DETAILS_HX_SOURCE_URL, AIRPORT_MIDPOINT_IATA)
AD_DEP_AIRPORT_URL = urljoin(sources.AIRPORT_DETAILS_AD_SOURCE_URL, f"?iata={AIRPORT_DEPARTURE_IATA}")
AD_DST_AIRPORT_URL = urljoin(sources.AIRPORT_DETAILS_AD_SOURCE_URL, f"?iata={AIRPORT_DESTINATION_IATA}")
AD_MID_AIRPORT_URL = urljoin(sources.AIRPORT_DETAILS_AD_SOURCE_URL, f"?iata={AIRPORT_MIDPOINT_IATA}")

HX_ROUTE_RESP_200 = {"status_code": 200, "json": {"flight": "UAE181", "route": f"{AIRPORT_DEPARTURE_IATA}-{AIRPORT_DESTINATION_IATA}", "updatetime": 1747593022}, "headers": HEADER_JSON}
HX_ROUTE_RESP_404 = {"status_code": 404, "json": {"status": "404", "error": "Route not found."}, "headers": HEADER_JSON}
HX_ROUTE_RESP_502 = {"status_code": 502, "json": {}}
HX_ROUTE_MP_RESP_200 = {"status_code": 200, "json": {"flight": "UAE192", "route": f"{AIRPORT_DEPARTURE_IATA}-{AIRPORT_MIDPOINT_IATA}-{AIRPORT_DESTINATION_IATA}", "updatetime": 1747594544}, "headers": HEADER_JSON}
SB_ROUTE_RESP_200 = {"status_code": 200, "json": _load_json("tests/data/flight/route_sb.json"), "headers": HEADER_JSON}
SB_ROUTE_RESP_404 = {"status_code": 404, "json": {"response": "unknown callsign"}, "headers": HEADER_JSON}
SB_ROUTE_RESP_502 = {"status_code": 502, "json": {}}
SB_ROUTE_MP_RESP_200 = {"status_code": 200, "json": _load_json("tests/data/flight/route_sb_mp.json"), "headers": HEADER_JSON}
HX_AIRPORT_RESP_200 = {"status_code": 200, "json": _load_json("tests/data/flight/airport_hx.json"), "headers": HEADER_JSON}
HX_AIRPORT_RESP_404 = {"status_code": 404, "json": {}, "headers": HEADER_JSON}
HX_AIRPORT_RESP_502 = {"status_code": 502, "json": {"status": "404", "error": "Airport not found."}}
AD_AIRPORT_RESP_200 = {"status_code": 200, "json": _load_json("tests/data/flight/airport_ad.json"), "headers": HEADER_JSON}
AD_AIRPORT_RESP_404 = {"status_code": 404, "json": {"status": 404, "error": "Airport not found."}, "headers": HEADER_JSON}
AD_AIRPORT_RESP_502 = {"status_code": 502, "json": {}}

OSN_STATES_RESP_200 = {"status_code": 200, "json": _load_json("tests/data/osn/osn_states.json"), "headers": HEADER_JSON}
OSN_STATES_RESP_404 = {"status_code": 200, "json": {"time": 1686301665, "states": None}, "headers": HEADER_JSON}
OSN_STATES_RESP_502 = {"status_code": 502, "json": {}}
